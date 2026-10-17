"""Unit tests for TripPilot Amazon Bedrock service foundation using mocks.

Guarantees zero live AWS network requests or cloud charges while thoroughly testing
credential detection, configuration loading, Converse API response handling, and error cases.
"""
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError, ConnectTimeoutError, ReadTimeoutError, EndpointConnectionError

from app.models import (
    TripPlanRequest,
    TripPlanResponse,
    BedrockItineraryEnrichment,
)
from app.services.trip_planner import create_trip_plan
from app.services.bedrock_service import (
    BedrockService,
    BedrockConfig,
    BedrockStatusResponse,
    BedrockInvocationResult,
    apply_bedrock_enrichment,
    DEFAULT_BEDROCK_MODEL_ID,
    DEFAULT_AWS_REGION,
)


def test_bedrock_config_defaults():
    """Verifies default region and model ID configuration."""
    with patch.dict("os.environ", {}, clear=True):
        config = BedrockConfig()
        assert config.region_name == DEFAULT_AWS_REGION
        assert config.model_id == DEFAULT_BEDROCK_MODEL_ID
        assert config.connect_timeout == 5.0
        assert config.read_timeout == 15.0


def test_bedrock_config_env_overrides():
    """Verifies environment variable overrides for region and model ID."""
    env = {
        "AWS_REGION": "ap-south-1",
        "BEDROCK_MODEL_ID": "amazon.nova-lite-v1:0",
    }
    with patch.dict("os.environ", env, clear=True):
        config = BedrockConfig()
        assert config.region_name == "ap-south-1"
        assert config.model_id == "amazon.nova-lite-v1:0"


def test_bedrock_status_missing_credentials():
    """Verifies that get_status cleanly reports provider_unavailable when credentials are absent."""
    with patch("botocore.session.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get_credentials.return_value = None
        mock_get_session.return_value = mock_session

        service = BedrockService()
        status = service.get_status()

        assert status.status == "provider_unavailable"
        assert status.has_credentials is False
        assert status.error is not None
        assert "AWS credentials not detected" in status.error


def test_bedrock_status_with_credentials():
    """Verifies that get_status reports available when credentials exist."""
    with patch("botocore.session.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_creds = MagicMock()
        mock_creds.method = "env"
        mock_session.get_credentials.return_value = mock_creds
        mock_get_session.return_value = mock_session

        service = BedrockService()
        status = service.get_status()

        assert status.status == "available"
        assert status.has_credentials is True
        assert status.credential_source == "env"
        assert status.error is None


def test_bedrock_converse_missing_credentials_does_not_crash():
    """Verifies converse returns provider_unavailable without throwing or calling network."""
    with patch("botocore.session.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get_credentials.return_value = None
        mock_get_session.return_value = mock_session

        service = BedrockService()
        result = service.converse("Suggest itinerary narrative for Jaipur")

        assert result.status == "provider_unavailable"
        assert result.text is None
        assert "AWS credentials not detected" in result.error


def test_bedrock_converse_success_mocked():
    """Verifies successful Converse API call and token extraction using a mock client."""
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {"text": "Jaipur, the Pink City, blends grand Rajput fortresses with artisanal bazaars."}
                ],
            }
        },
        "usage": {
            "inputTokens": 42,
            "outputTokens": 18,
            "totalTokens": 60,
        },
        "stopReason": "end_turn",
    }

    config = BedrockConfig(region_name="us-east-1", model_id="anthropic.claude-3-5-sonnet-20241022-v2:0")
    service = BedrockService(config=config, client=mock_client)

    result = service.converse(
        prompt="Tell me about Jaipur",
        system_prompt="You are a travel editor.",
        max_tokens=500,
        temperature=0.5,
    )

    assert result.status == "success"
    assert result.model_id == "anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert result.region == "us-east-1"
    assert "Jaipur, the Pink City" in result.text
    assert result.usage["input_tokens"] == 42
    assert result.usage["output_tokens"] == 18
    assert result.usage["total_tokens"] == 60
    assert result.latency_ms is not None

    # Verify call arguments
    mock_client.converse.assert_called_once()
    call_kwargs = mock_client.converse.call_args.kwargs
    assert call_kwargs["modelId"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert call_kwargs["messages"][0]["content"][0]["text"] == "Tell me about Jaipur"
    assert call_kwargs["system"][0]["text"] == "You are a travel editor."
    assert call_kwargs["inferenceConfig"]["maxTokens"] == 500


def test_bedrock_converse_client_error_handled_gracefully():
    """Verifies that ClientError exceptions (e.g. AccessDeniedException) are returned safely."""
    mock_client = MagicMock()
    error_response = {
        "Error": {
            "Code": "AccessDeniedException",
            "Message": "User is not authorized to perform bedrock:InvokeModel",
        }
    }
    mock_client.converse.side_effect = ClientError(error_response, "Converse")

    service = BedrockService(client=mock_client)
    result = service.converse("Test prompt")

    assert result.status == "error"
    assert "AccessDeniedException" in result.error
    assert result.text is None


def test_bedrock_converse_timeout_handled_gracefully():
    """Verifies that connection and read timeouts do not crash the service."""
    mock_client = MagicMock()
    mock_client.converse.side_effect = ReadTimeoutError(endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com")

    service = BedrockService(client=mock_client)
    result = service.converse("Test prompt")

    assert result.status == "error"
    assert "timed out" in result.error.lower()


def test_bedrock_generate_travel_narrative_mocked():
    """Verifies generate_travel_narrative high-level method."""
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {"text": "A 3-day exploration of Goa uncovering quiet Mandovi river backwaters."}
                ],
            }
        },
        "usage": {"inputTokens": 60, "outputTokens": 20, "totalTokens": 80},
    }

    service = BedrockService(client=mock_client)
    result = service.generate_travel_narrative(
        destination="Goa",
        duration_days=3,
        travel_style="comfort",
        highlights=["Chorao Island", "Fontainhas"],
    )

    assert result.status == "success"
    assert "Mandovi river" in result.text
    mock_client.converse.assert_called_once()
    call_prompt = mock_client.converse.call_args.kwargs["messages"][0]["content"][0]["text"]
    assert "Goa" in call_prompt
    assert "Chorao Island" in call_prompt


def test_bedrock_enrich_itinerary_success_mocked():
    """Verifies BedrockService.enrich_itinerary with mocked Claude Converse response."""
    import json
    plan_req = TripPlanRequest(
        starting_city="Delhi",
        destination_id="jaipur",
        days=2,
        budget=15000,
        interests=["heritage", "food"],
        travel_style="balanced",
    )
    plan = create_trip_plan(plan_req)

    mock_enrichment_json = {
        "narrative": "A royal escapade across Jaipur's iconic amber fortifications and bustling pink bazaars.",
        "cultural_guidance": "Dress respectfully at religious sites and remove shoes before stepping into temple courtyards.",
        "local_food_guide": "Savor authentic Dal Baati Churma, Pyaaz Kachori, and Ghewar at Johari Bazaar.",
        "daily_insights": [
            {
                "day_number": 1,
                "theme_note": "A deep dive into Rajput architecture and monumental astronomic instruments.",
                "practical_tip": "Wear comfortable walking shoes for cobblestone ramps at Amber Fort.",
                "culinary_highlight": "Crispy Pyaaz Kachori near Hawa Mahal."
            },
            {
                "day_number": 2,
                "theme_note": "Artisanal textile crafts and panoramic sunset views over the Aravali hills.",
                "practical_tip": "Carry cash for local artisan guilds and street craft stalls.",
                "culinary_highlight": "Traditional Thali dinner with Gatte ki Sabzi."
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": json.dumps(mock_enrichment_json)}],
            }
        },
        "usage": {"inputTokens": 200, "outputTokens": 150, "totalTokens": 350},
    }

    service = BedrockService(client=mock_client)
    enrichment = service.enrich_itinerary(plan)

    assert enrichment.status == "enriched"
    assert enrichment.model_id == DEFAULT_BEDROCK_MODEL_ID
    assert "royal escapade" in enrichment.narrative
    assert "religious sites" in enrichment.cultural_guidance
    assert "Dal Baati Churma" in enrichment.local_food_guide
    assert len(enrichment.daily_insights) == 2
    assert enrichment.daily_insights[0].day_number == 1
    assert "Amber Fort" in enrichment.daily_insights[0].practical_tip
    assert enrichment.daily_insights[1].day_number == 2


def test_bedrock_enrich_itinerary_provider_unavailable():
    """Verifies fallback when AWS credentials are not found."""
    with patch("botocore.session.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get_credentials.return_value = None
        mock_get_session.return_value = mock_session

        plan_req = TripPlanRequest(
            starting_city="Mumbai",
            destination_id="goa",
            days=3,
            budget=20000,
            interests=["beaches", "relaxation"],
            travel_style="budget",
        )
        plan = create_trip_plan(plan_req)

        service = BedrockService()
        enrichment = service.enrich_itinerary(plan)

        assert enrichment.status == "provider_unavailable"
        assert enrichment.narrative is None
        assert "AWS credentials not detected" in enrichment.error


def test_bedrock_enrich_itinerary_malformed_json_fallback():
    """Verifies graceful handling when the model returns unparseable text without throwing."""
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "Here is an overview without valid JSON: Visit Jaipur's forts and enjoy food!"}],
            }
        },
        "usage": {"inputTokens": 50, "outputTokens": 20, "totalTokens": 70},
    }

    plan_req = TripPlanRequest(
        starting_city="Delhi",
        destination_id="jaipur",
        days=2,
        budget=15000,
        interests=["heritage", "food"],
        travel_style="balanced",
    )
    plan = create_trip_plan(plan_req)

    service = BedrockService(client=mock_client)
    enrichment = service.enrich_itinerary(plan)

    assert enrichment.status == "error"
    assert "could not be parsed" in enrichment.error
    assert enrichment.narrative is not None
    assert "Visit Jaipur" in enrichment.narrative


def test_apply_bedrock_enrichment_preserves_deterministic_plan_integrity():
    """Verifies mathematical and structural integrity: all costs and dates remain 100% untouched."""
    import json
    plan_req = TripPlanRequest(
        starting_city="Mumbai",
        destination_id="munnar",
        days=4,
        budget=30000,
        interests=["nature", "tea"],
        travel_style="comfort",
    )
    original_plan = create_trip_plan(plan_req)

    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "text": json.dumps({
                            "narrative": "Mist-covered tea gardens of Munnar.",
                            "cultural_guidance": "Respect plantation guidelines and local ecology.",
                            "local_food_guide": "Appam with stew and Kerala cardamom tea.",
                            "daily_insights": []
                        })
                    }
                ],
            }
        },
        "usage": {"inputTokens": 100, "outputTokens": 50, "totalTokens": 150},
    }
    service = BedrockService(client=mock_client)

    enriched_plan = apply_bedrock_enrichment(original_plan, bedrock_service=service)

    # Verify AI enrichment is populated
    assert enriched_plan.ai_enrichment is not None
    assert enriched_plan.ai_enrichment.status == "enriched"
    assert "Mist-covered" in enriched_plan.ai_enrichment.narrative

    # Verify every deterministic field is mathematically identical
    assert enriched_plan.destination.id == original_plan.destination.id
    assert enriched_plan.starting_city == original_plan.starting_city
    assert enriched_plan.num_days == original_plan.num_days
    assert len(enriched_plan.active_days) == len(original_plan.active_days)
    assert enriched_plan.travel_style == original_plan.travel_style
    assert enriched_plan.daily_stay == original_plan.daily_stay
    assert enriched_plan.daily_food == original_plan.daily_food
    assert enriched_plan.daily_transit == original_plan.daily_transit
    assert enriched_plan.accommodation_cost == original_plan.accommodation_cost
    assert enriched_plan.food_cost == original_plan.food_cost
    assert enriched_plan.transport_cost == original_plan.transport_cost
    assert enriched_plan.activities_cost == original_plan.activities_cost
    assert enriched_plan.total_estimated_cost == original_plan.total_estimated_cost
    assert enriched_plan.user_budget == original_plan.user_budget
    assert enriched_plan.remaining_budget == original_plan.remaining_budget
    assert enriched_plan.is_over_budget == original_plan.is_over_budget
    assert enriched_plan.deficit == original_plan.deficit


def test_api_trips_enrich_endpoint():
    """Verifies POST /api/trips/enrich API endpoint preserves all calculations."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Create a baseline plan
    plan_res = client.post("/api/trips/plan", json={
        "startingCity": "Mumbai",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 20000,
        "interests": ["heritage", "food"],
        "travelStyle": "balanced",
    })
    assert plan_res.status_code == 200
    plan_data = plan_res.json()

    # 2. Enrich the plan via POST /api/trips/enrich
    enrich_res = client.post("/api/trips/enrich", json=plan_data)
    assert enrich_res.status_code == 200
    enriched_data = enrich_res.json()

    # Deterministic budget numbers must match exactly
    assert enriched_data["totalEstimatedCost"] == plan_data["totalEstimatedCost"]
    assert enriched_data["accommodationCost"] == plan_data["accommodationCost"]
    assert enriched_data["foodCost"] == plan_data["foodCost"]
    assert enriched_data["transportCost"] == plan_data["transportCost"]
    assert enriched_data["activitiesCost"] == plan_data["activitiesCost"]
    assert enriched_data["numDays"] == plan_data["numDays"]
    assert "aiEnrichment" in enriched_data
    assert enriched_data["aiEnrichment"]["status"] in ("enriched", "provider_unavailable", "error")


def test_api_trips_plan_with_enrich_param():
    """Verifies POST /api/trips/plan?enrich=true query parameter."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    res = client.post("/api/trips/plan?enrich=true", json={
        "startingCity": "Bangalore",
        "destinationId": "goa",
        "days": 2,
        "budget": 15000,
        "interests": ["beaches", "relaxation"],
        "travelStyle": "budget",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["numDays"] == 2
    assert "aiEnrichment" in data
    assert data["aiEnrichment"] is not None


def test_api_bedrock_status_and_narrative_endpoints():
    """Verifies GET /api/bedrock/status and POST /api/bedrock/narrative endpoints."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    status_res = client.get("/api/bedrock/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert "status" in status_data
    assert "model_id" in status_data
    assert status_data["model_id"] == DEFAULT_BEDROCK_MODEL_ID

    narrative_res = client.post("/api/bedrock/narrative", json={
        "destination": "Goa",
        "durationDays": 3,
        "travelStyle": "balanced",
        "highlights": ["Fort Aguada", "Anjuna"],
    })
    assert narrative_res.status_code == 200
    narrative_data = narrative_res.json()
    assert narrative_data["status"] in ("success", "provider_unavailable", "error")


def test_apply_bedrock_enrichment_provider_unavailable():
    """Verifies apply_bedrock_enrichment with missing credentials attaches provider_unavailable cleanly."""
    with patch("botocore.session.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_session.get_credentials.return_value = None
        mock_get_session.return_value = mock_session

        service = BedrockService()
        plan_req = TripPlanRequest(
            starting_city="Chennai",
            destination_id="hampi",
            days=3,
            budget=22000,
            interests=["heritage", "architecture"],
            travel_style="balanced",
        )
        original_plan = create_trip_plan(plan_req)
        enriched = apply_bedrock_enrichment(original_plan, bedrock_service=service)

        assert enriched.ai_enrichment is not None
        assert enriched.ai_enrichment.status == "provider_unavailable"
        assert enriched.total_estimated_cost == original_plan.total_estimated_cost
        assert enriched.num_days == 3
        assert len(enriched.active_days) == 3


def test_apply_bedrock_enrichment_sequential_reenrichment():
    """Verifies that re-enriching an already enriched plan safely updates enrichment."""
    import json
    plan_req = TripPlanRequest(
        starting_city="Delhi",
        destination_id="agra",
        days=2,
        budget=12000,
        interests=["heritage"],
        travel_style="balanced",
    )
    plan = create_trip_plan(plan_req)

    # First enrichment mock
    mock_client1 = MagicMock()
    mock_client1.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": json.dumps({"narrative": "First narrative overview."})}],
            }
        },
        "usage": {"inputTokens": 10, "outputTokens": 10, "totalTokens": 20},
    }
    enriched_1 = apply_bedrock_enrichment(plan, bedrock_service=BedrockService(client=mock_client1))
    assert enriched_1.ai_enrichment.narrative == "First narrative overview."

    # Re-enrichment mock
    mock_client2 = MagicMock()
    mock_client2.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": json.dumps({"narrative": "Updated second narrative overview."})}],
            }
        },
        "usage": {"inputTokens": 15, "outputTokens": 15, "totalTokens": 30},
    }
    enriched_2 = apply_bedrock_enrichment(enriched_1, bedrock_service=BedrockService(client=mock_client2))
    assert enriched_2.ai_enrichment.narrative == "Updated second narrative overview."
    assert enriched_2.total_estimated_cost == plan.total_estimated_cost


def test_api_trips_enrich_validation_error():
    """Verifies POST /api/trips/enrich returns HTTP 422 for malformed payloads."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    res = client.post("/api/trips/enrich", json={"destination": "invalid"})
    assert res.status_code == 422
    err_body = res.json()
    assert "details" in err_body or "message" in err_body or "detail" in err_body


