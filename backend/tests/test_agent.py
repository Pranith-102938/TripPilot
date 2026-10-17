"""Comprehensive pytest tests for Strands Agents SDK and Decider 2B integration."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from strands_decider.schema import (
    ChoiceAnswer,
    SystemOneResponse,
    Usage,
    ChoiceQuestion,
    SystemOneRequest,
)

from app.main import app
from app.agent.client import StrandsDeciderClient, StrandsDeciderProviderError
from app.agent.tools import (
    STRANDS_REGISTERED_TOOLS,
    strands_optimize_budget,
    strands_adjust_trip_duration,
    strands_adjust_travel_style,
    strands_select_interest_activities,
    strands_validate_trip_constraints,
)
from app.agent.service import StrandsAgentService
from app.agent.schemas import AgentPlanRequest, AgentPlanResponse
from app.services.trip_planner import create_trip_plan
from app.models import TripPlanRequest

client = TestClient(app)


def test_strands_tool_registration():
    """Verifies that all 5 planning tools are properly decorated as Strands SDK tools."""
    assert len(STRANDS_REGISTERED_TOOLS) == 5
    for tool_name, tool_meta in STRANDS_REGISTERED_TOOLS.items():
        tool_obj = tool_meta["tool"]
        assert hasattr(tool_obj, "tool_spec")
        assert hasattr(tool_obj, "tool_name")
        assert tool_obj.tool_name == tool_name
        spec = tool_obj.tool_spec
        assert "name" in spec
        assert "description" in spec
        assert "inputSchema" in spec
        assert "properties" in spec["inputSchema"]["json"]


def test_agent_status_endpoint():
    """Tests GET /api/agent/status returns model name and registered Strands tools."""
    response = client.get("/api/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "StrandsAgents/strands-decider-2B"
    assert "provider" in data
    assert len(data["registered_tools"]) == 5
    tool_names = [t["name"] for t in data["registered_tools"]]
    assert "optimize_budget" in tool_names
    assert "adjust_trip_duration" in tool_names
    assert "adjust_travel_style" in tool_names
    assert "select_interest_activities" in tool_names
    assert "validate_trip_constraints" in tool_names


def test_agent_plan_provider_unavailable_does_not_fake_ai():
    """Verifies that when Decider 2B endpoint is offline, agent transparently reports status."""
    payload = {
        "user_request": "Please shorten my trip to 2 days and cut costs",
        "destination_id": "jaipur",
        "duration": 4,
        "budget": 15000.0,
    }
    response = client.post("/api/agent/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "provider_unavailable"
    assert data["execution_mode"] == "provider_unavailable"
    assert data["selected_tools"] == []
    assert data["tool_traces"] == []
    assert "Strands Decider 2B model server is not connected" in data["explanation"]
    assert data["provider_status"]["available"] is False
    assert data["itinerary"] is not None
    assert data["itinerary"]["destination"]["id"] == "jaipur"


def test_agent_plan_validation_error():
    """Verifies that invalid requests return HTTP 422 with validation errors."""
    # Empty user_request
    response = client.post("/api/agent/plan", json={"user_request": "no"})
    assert response.status_code == 422


def test_agent_plan_mocked_single_tool_execution():
    """Tests Decider 2B single tool selection and execution in mock environment."""
    mock_client = MagicMock(spec=StrandsDeciderClient)
    mock_client.model_name = "StrandsAgents/strands-decider-2B"
    mock_client.get_provider_status.return_value = {
        "available": True,
        "endpoint": "http://127.0.0.1:8001/v1/systemone",
        "model": "StrandsAgents/strands-decider-2B",
        "device": "cpu",
        "error": None,
    }

    # Step 1: Decider chooses optimize_budget
    # Step 2: Decider chooses finish_planning
    mock_client.ask_choice.side_effect = [
        ChoiceAnswer(
            choice="optimize_budget",
            probabilities={"optimize_budget": 0.88, "adjust_trip_duration": 0.08, "finish_planning": 0.04},
            confidence=0.88,
        ),
        ChoiceAnswer(
            choice="finish_planning",
            probabilities={"finish_planning": 0.95, "optimize_budget": 0.05},
            confidence=0.95,
        ),
    ]

    service = StrandsAgentService(client=mock_client)
    req = AgentPlanRequest(
        user_request="Save money and optimize budget for 12000 INR",
        destination_id="jaipur",
        duration=3,
        budget=12000.0,
    )
    result = service.plan(req)

    assert result.status == "success"
    assert result.execution_mode == "strands_decider_2b_live"
    assert result.selected_tools == ["optimize_budget"]
    assert len(result.tool_traces) == 1
    assert result.tool_traces[0].tool_name == "optimize_budget"
    assert result.tool_traces[0].confidence == 0.88
    assert result.itinerary.budget_optimized is True



def test_agent_plan_mocked_sequential_multi_tool_workflow():
    """Tests Decider 2B sequential tool selection: duration adjuster -> budget optimizer -> finish."""
    mock_client = MagicMock(spec=StrandsDeciderClient)
    mock_client.model_name = "StrandsAgents/strands-decider-2B"
    mock_client.get_provider_status.return_value = {
        "available": True,
        "endpoint": "http://127.0.0.1:8001/v1/systemone",
        "model": "StrandsAgents/strands-decider-2B",
        "device": "cpu",
        "error": None,
    }

    # Step 1: Decider chooses adjust_trip_duration (shorten to 2 days)
    # Step 2: Decider chooses optimize_budget
    # Step 3: Decider chooses finish_planning
    mock_client.ask_choice.side_effect = [
        ChoiceAnswer(
            choice="adjust_trip_duration",
            probabilities={"adjust_trip_duration": 0.82, "optimize_budget": 0.12, "finish_planning": 0.06},
            confidence=0.82,
        ),
        ChoiceAnswer(
            choice="optimize_budget",
            probabilities={"optimize_budget": 0.91, "finish_planning": 0.09},
            confidence=0.91,
        ),
        ChoiceAnswer(
            choice="finish_planning",
            probabilities={"finish_planning": 0.98},
            confidence=0.98,
        ),
    ]

    service = StrandsAgentService(client=mock_client)
    req = AgentPlanRequest(
        user_request="Shorten my trip to 2 days and optimize my budget for 10000 INR",
        destination_id="goa",
        duration=4,
        budget=10000.0,
    )
    result = service.plan(req)

    assert result.status == "success"
    assert result.execution_mode == "strands_decider_2b_live"
    assert result.selected_tools == ["adjust_trip_duration", "optimize_budget"]
    assert len(result.tool_traces) == 2
    assert result.tool_traces[0].tool_name == "adjust_trip_duration"
    assert result.tool_traces[1].tool_name == "optimize_budget"
    assert result.itinerary.num_days == 2
    assert result.itinerary.budget_optimized is True
    assert "Strands Decider 2B autonomously orchestrated 2 planning tool(s)" in result.explanation


def test_agent_plan_mocked_travel_style_and_interests():
    """Tests Decider 2B tool selection for travel style adjustment and interest ranking."""
    mock_client = MagicMock(spec=StrandsDeciderClient)
    mock_client.model_name = "StrandsAgents/strands-decider-2B"
    mock_client.get_provider_status.return_value = {
        "available": True,
        "endpoint": "http://127.0.0.1:8001/v1/systemone",
        "model": "StrandsAgents/strands-decider-2B",
        "device": "cpu",
        "error": None,
    }

    mock_client.ask_choice.side_effect = [
        ChoiceAnswer(
            choice="adjust_travel_style",
            probabilities={"adjust_travel_style": 0.86, "select_interest_activities": 0.14},
            confidence=0.86,
        ),
        ChoiceAnswer(
            choice="select_interest_activities",
            probabilities={"select_interest_activities": 0.89, "finish_planning": 0.11},
            confidence=0.89,
        ),
        ChoiceAnswer(
            choice="finish_planning",
            probabilities={"finish_planning": 0.97},
            confidence=0.97,
        ),
    ]

    service = StrandsAgentService(client=mock_client)
    req = AgentPlanRequest(
        user_request="Upgrade to comfort luxury style and focus on nature and beaches",
        destination_id="goa",
        duration=3,
        budget=40000.0,
    )
    result = service.plan(req)

    assert result.status == "success"
    assert result.selected_tools == ["adjust_travel_style", "select_interest_activities"]
    assert result.itinerary.travel_style == "comfort"



def test_agent_plan_provider_error_during_loop():
    """Tests graceful handling when Decider 2B raises a provider error mid-loop."""
    mock_client = MagicMock(spec=StrandsDeciderClient)
    mock_client.model_name = "StrandsAgents/strands-decider-2B"
    mock_client.get_provider_status.return_value = {
        "available": True,
        "endpoint": "http://127.0.0.1:8001/v1/systemone",
        "model": "StrandsAgents/strands-decider-2B",
        "device": "cpu",
        "error": None,
    }
    mock_client.ask_choice.side_effect = StrandsDeciderProviderError("Connection reset by peer", endpoint="http://127.0.0.1:8001/v1/systemone")

    service = StrandsAgentService(client=mock_client)
    req = AgentPlanRequest(
        user_request="Optimize my trip",
        destination_id="hyderabad",
        duration=3,
        budget=15000.0,
    )
    result = service.plan(req)
    assert result.status == "error"
    assert "Connection reset by peer" in result.error
    assert result.itinerary is not None
