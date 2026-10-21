"""Comprehensive tests for FastAPI CORS middleware and origin resolution."""
import pytest
from fastapi.testclient import TestClient

from app.main import app, DEFAULT_ALLOWED_ORIGINS, resolve_cors_origins

client = TestClient(app)

PRODUCTION_ORIGIN = "https://trippilot-web.onrender.com"


def test_default_allowed_origins_includes_production_and_localhost():
    """Verifies that the exact production frontend origin and local dev ports are in defaults."""
    assert PRODUCTION_ORIGIN in DEFAULT_ALLOWED_ORIGINS
    assert "http://localhost:3000" in DEFAULT_ALLOWED_ORIGINS
    assert "http://127.0.0.1:3000" in DEFAULT_ALLOWED_ORIGINS
    assert "http://localhost:5173" in DEFAULT_ALLOWED_ORIGINS
    assert "http://127.0.0.1:5173" in DEFAULT_ALLOWED_ORIGINS


def test_resolve_cors_origins_parsing():
    """Verifies parsing, trimming, trailing slash removal, wildcard exclusion, and deduplication."""
    input_str = "https://preview.onrender.com/,  https://custom-domain.com , *, https://trippilot-web.onrender.com"
    resolved = resolve_cors_origins(input_str)

    # Added items are cleaned
    assert "https://preview.onrender.com" in resolved
    assert "https://custom-domain.com" in resolved

    # Wildcard is strictly excluded
    assert "*" not in resolved

    # Production and local origins remain present
    assert PRODUCTION_ORIGIN in resolved
    assert "http://localhost:3000" in resolved

    # No duplicates
    assert len(resolved) == len(set(resolved))


def test_preflight_trips_plan_from_production_origin():
    """Tests OPTIONS preflight request to /api/trips/plan from production frontend origin."""
    headers = {
        "Origin": PRODUCTION_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type, accept",
    }
    response = client.options("/api/trips/plan", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PRODUCTION_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods
    assert "OPTIONS" in allowed_methods
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed_headers


def test_preflight_agent_status_from_production_origin():
    """Tests OPTIONS preflight request to /api/agent/status from production frontend origin."""
    headers = {
        "Origin": PRODUCTION_ORIGIN,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "accept",
    }
    response = client.options("/api/agent/status", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PRODUCTION_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_preflight_health_from_production_origin():
    """Tests OPTIONS preflight request to /api/health from production frontend origin."""
    headers = {
        "Origin": PRODUCTION_ORIGIN,
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PRODUCTION_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_get_health_with_production_origin():
    """Tests simple GET request to /api/health with Origin header."""
    response = client.get("/api/health", headers={"Origin": PRODUCTION_ORIGIN})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PRODUCTION_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_post_trips_plan_with_production_origin():
    """Tests actual POST request to /api/trips/plan with Origin header."""
    payload = {
        "startingCity": "Delhi",
        "destinationId": "jaipur",
        "days": 3,
        "budget": 20000,
        "interests": ["heritage"],
        "travelStyle": "balanced",
    }
    response = client.post(
        "/api/trips/plan",
        json=payload,
        headers={"Origin": PRODUCTION_ORIGIN},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PRODUCTION_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.parametrize("dev_origin", [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
])
def test_preflight_from_localhost_origins(dev_origin):
    """Verifies that all local development origins continue to pass preflight."""
    headers = {
        "Origin": dev_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/trips/plan", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == dev_origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_unauthorized_origin_rejected():
    """Verifies that an unknown / arbitrary origin does not receive Access-Control-Allow-Origin."""
    unauthorized = "https://unauthorized-attacker.com"
    headers = {
        "Origin": unauthorized,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    # In Starlette CORSMiddleware, disallowed origin in preflight returns 400 Bad Request
    response = client.options("/api/trips/plan", headers=headers)
    assert response.headers.get("access-control-allow-origin") is None

    # Disallowed origin on regular GET returns response without CORS header
    get_res = client.get("/api/health", headers={"Origin": unauthorized})
    assert get_res.status_code == 200
    assert get_res.headers.get("access-control-allow-origin") is None
