"""Automated tests for Phase 6.2 and 6.3 Route Foundation, OSRM Road Routing, and Fallbacks."""
from unittest.mock import patch, MagicMock
import httpx
import pytest

from app.models import GeoPoint, CoordinatePrecision, RouteSegment
from app.services.route_service import (
    haversine_distance_km,
    estimate_transit_time_and_mode,
    build_route_segment,
    build_day_route_segments,
)
from app.services.routing_provider import (
    OSRMRoutingProvider,
    get_routing_provider,
    set_routing_provider,
    BaseRoutingProvider,
)
from app.services.trip_planner import (
    calculate_trip_plan,
    get_all_destinations,
    get_destination_by_id,
)


def test_haversine_distance_known_points():
    """Haversine distance between Charminar and Chowmahalla Palace in Hyderabad (~0.5 - 0.8 km)."""
    charminar = {"lat": 17.3616, "lng": 78.4747}
    chowmahalla = {"lat": 17.3578, "lng": 78.4717}

    dist_km = haversine_distance_km(charminar, chowmahalla)
    assert 0.4 <= dist_km <= 0.8, f"Expected distance between 0.4 and 0.8 km, got {dist_km}"


def test_transit_mode_and_speed_heuristics():
    """Validates transit mode assignment and duration calculations."""
    # Short distance (<= 1.5 km circuity) -> walking
    walk_info = estimate_transit_time_and_mode(0.5)
    assert walk_info["transitMode"] == "walking"
    assert walk_info["durationMinutes"] >= 5

    # Medium distance (1.5 - 8 km circuity) -> auto_rickshaw
    auto_info = estimate_transit_time_and_mode(3.0)
    assert auto_info["transitMode"] == "auto_rickshaw"
    assert auto_info["durationMinutes"] >= 8

    # Long distance (> 8 km circuity) -> taxi
    taxi_info = estimate_transit_time_and_mode(10.0)
    assert taxi_info["transitMode"] == "taxi"
    assert taxi_info["durationMinutes"] >= 15


def test_all_25_destinations_have_center_coordinates():
    """Verifies that all 25 curated destinations have valid city center coordinates."""
    destinations = get_all_destinations()
    assert len(destinations) >= 25

    for d in destinations:
        assert "centerCoordinates" in d, f"Missing centerCoordinates in {d['id']}"
        coords = d["centerCoordinates"]
        assert -90.0 <= coords["lat"] <= 90.0
        assert -180.0 <= coords["lng"] <= 180.0
        assert coords["precision"] == "city_center"


def test_curated_base_itinerary_coordinates_and_routes():
    """Verifies that curated base destinations (Hyderabad, Jaipur, Goa, Munnar) have verified coordinates and routes."""
    from app.data import SAMPLE_ITINERARIES

    # Verify all 4 base itineraries have verified coordinates attached in their data
    for dest_id in ["hyderabad", "jaipur", "goa", "munnar"]:
        assert dest_id in SAMPLE_ITINERARIES
        days = SAMPLE_ITINERARIES[dest_id]["days"]
        for day in days:
            for slot in ["morning", "afternoon", "evening"]:
                coords = day[slot].get("coordinates")
                assert coords is not None, f"Missing coordinates in {dest_id} day {day['dayNumber']} {slot}"
                assert coords["precision"] == "verified_attraction"

    # Verify full trip plan calculation on Hyderabad
    plan = calculate_trip_plan(
        starting_city="Bengaluru",
        destination_id="hyderabad",
        days=2,
        budget=20000,
        interests=["heritage"]
    )

    assert plan.map_center is not None
    assert plan.map_center.lat is not None
    assert plan.map_center.lng is not None
    assert plan.total_route_distance_km is not None
    assert plan.total_route_distance_km > 0

    # Day 1 should have verified coordinates on activities
    day1 = plan.active_days[0]
    assert day1.morning.coordinates is not None
    assert day1.morning.coordinates.precision == CoordinatePrecision.VERIFIED_ATTRACTION
    assert day1.afternoon.coordinates is not None
    assert day1.evening.coordinates is not None

    # Route segments
    assert len(day1.route_segments) == 2
    seg1 = day1.route_segments[0]
    assert seg1.from_slot == "morning"
    assert seg1.to_slot == "afternoon"
    assert seg1.is_route_calculated is True
    assert seg1.geometry_source in ["osrm_road", "haversine_circuity"]
    assert seg1.route_type in ["road", "approximate_estimate"]
    assert seg1.distance_km is not None
    assert seg1.duration_minutes is not None
    assert seg1.polyline is not None
    assert len(seg1.polyline) >= 2



def test_unverified_custom_destination_handles_missing_coordinates_honestly():
    """Custom unverified destinations must NOT invent coordinates or route distances."""
    plan = calculate_trip_plan(
        starting_city="Bengaluru",
        destination_id="custom",
        custom_destination_name="Hidden Valley XYZ",
        days=2,
        budget=15000,
        interests=["nature"],
        is_custom_destination=True
    )

    assert plan.map_center is None
    assert plan.total_route_distance_km is None

    for day in plan.active_days:
        assert day.morning.coordinates is None
        assert day.afternoon.coordinates is None
        assert day.evening.coordinates is None
        assert day.day_route_distance_km is None

        for seg in day.route_segments:
            assert seg.is_route_calculated is False
            assert seg.geometry_source == "unavailable"
            assert seg.route_type == "unavailable"
            assert seg.distance_km is None
            assert seg.duration_minutes is None
            assert seg.polyline is None


def test_budget_immutability_with_routes():
    """Attaching route calculations must never change any line item or total budget amount."""
    plan_with_routes = calculate_trip_plan(
        starting_city="Bengaluru",
        destination_id="hyderabad",
        days=3,
        budget=30000,
        interests=["culture"]
    )

    # Sum of categories strictly equals total_estimated_cost
    cat_sum = (
        plan_with_routes.accommodation_cost
        + plan_with_routes.food_cost
        + plan_with_routes.transport_cost
        + plan_with_routes.activities_cost
    )
    assert plan_with_routes.total_estimated_cost == cat_sum
    assert plan_with_routes.remaining_budget == plan_with_routes.user_budget - plan_with_routes.total_estimated_cost

    # Sum of day totals strictly equals total_estimated_cost
    day_total_sum = sum(d.day_total for d in plan_with_routes.active_days)
    assert day_total_sum == plan_with_routes.total_estimated_cost


# ==============================================================================
# Phase 6.3 Road Routing Provider & Fallback Tests
# ==============================================================================

def test_osrm_provider_successful_road_routing():
    """Simulates a successful OSRM road routing response with detailed turn geometry."""
    mock_osrm_payload = {
        "code": "Ok",
        "routes": [
            {
                "distance": 2400.0,  # 2.4 km
                "duration": 360.0,   # 6.0 minutes
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [78.4747, 17.3616],
                        [78.4740, 17.3620],
                        [78.4735, 17.3639],
                    ]
                }
            }
        ]
    }

    provider = OSRMRoutingProvider(enabled=True)
    provider.clear_cache()

    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_osrm_payload
        mock_get.return_value = mock_resp

        result = provider.get_route(17.3616, 78.4747, 17.3639, 78.4735)

        assert result is not None
        assert result["distance_km"] == 2.4
        assert result["duration_minutes"] == 6
        assert result["route_type"] == "road"
        assert result["geometry_source"] == "osrm_road"
        assert result["provider"] == "osrm"
        # GeoJSON [lng, lat] converted to Leaflet [lat, lng]
        assert result["polyline"] == [
            [17.3616, 78.4747],
            [17.3620, 78.4740],
            [17.3639, 78.4735]
        ]
        assert "Real-time traffic congestion not included" in result["traffic_notice"]


def test_osrm_provider_timeout_fallback_to_circuity():
    """When OSRM times out, provider returns None and route_service cleanly falls back to circuity."""
    provider = OSRMRoutingProvider(enabled=True, timeout_seconds=1.0)
    provider.clear_cache()

    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timeout")):
        route = provider.get_route(17.3616, 78.4747, 17.3639, 78.4735)
        assert route is None

    # Now verify build_route_segment falls back to circuity
    from_act = {
        "title": "Charminar",
        "location": "Old City",
        "coordinates": {"lat": 17.3616, "lng": 78.4747}
    }
    to_act = {
        "title": "Shadab",
        "location": "Madina",
        "coordinates": {"lat": 17.3639, "lng": 78.4735}
    }

    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timeout")):
        seg = build_route_segment("morning", "afternoon", from_act, to_act, routing_provider=provider)
        assert seg.is_route_calculated is True
        assert seg.geometry_source == "haversine_circuity"
        assert seg.route_type == "approximate_estimate"
        assert seg.provider is None
        assert seg.fallback_reason == "road_routing_unavailable_or_unreachable"
        assert seg.distance_km is not None
        assert seg.polyline is not None
        assert len(seg.polyline) == 2


def test_osrm_provider_error_and_malformed_response_fallback():
    """HTTP errors (e.g. 500) or non-Ok codes return None and fallback smoothly."""
    provider = OSRMRoutingProvider(enabled=True)
    provider.clear_cache()

    # 1. HTTP 502
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_get.return_value = mock_resp

        result = provider.get_route(17.3616, 78.4747, 17.3639, 78.4735)
        assert result is None

    # 2. OSRM code: "NoRoute"
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": "NoRoute", "message": "Impossible route"}
        mock_get.return_value = mock_resp

        result = provider.get_route(17.3616, 78.4747, 17.3639, 78.4735)
        assert result is None


def test_routing_skips_network_calls_for_missing_or_invalid_coordinates():
    """Missing or out-of-range coordinates must never trigger network routing requests."""
    provider = OSRMRoutingProvider(enabled=True)

    with patch("httpx.Client.get") as mock_get:
        # None coords
        assert provider.get_route(None, None, 17.0, 78.0) is None
        # Out-of-bounds latitude (> 90.0)
        assert provider.get_route(95.0, 78.0, 17.0, 78.0) is None
        # Out-of-bounds longitude (> 180.0)
        assert provider.get_route(17.0, 195.0, 17.0, 78.0) is None

        # Verify no network call was attempted
        mock_get.assert_not_called()

    # Segment test for missing coordinates
    from_act = {"title": "Unknown Stop 1", "location": "Unknown", "coordinates": None}
    to_act = {"title": "Unknown Stop 2", "location": "Unknown", "coordinates": None}
    seg = build_route_segment("morning", "afternoon", from_act, to_act, routing_provider=provider)
    assert seg.is_route_calculated is False
    assert seg.geometry_source == "unavailable"
    assert seg.route_type == "unavailable"
    assert seg.distance_km is None
    assert seg.duration_minutes is None
    assert seg.polyline is None
    assert seg.fallback_reason == "missing_coordinates"


def test_osrm_provider_in_memory_caching():
    """Repeated queries with identical coordinates use the in-memory cache and make only 1 request."""
    provider = OSRMRoutingProvider(enabled=True)
    provider.clear_cache()

    mock_osrm_payload = {
        "code": "Ok",
        "routes": [{"distance": 1500.0, "duration": 180.0, "geometry": {"coordinates": [[78.47, 17.36], [78.48, 17.37]]}}]
    }

    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_osrm_payload
        mock_get.return_value = mock_resp

        r1 = provider.get_route(17.3616, 78.4747, 17.3713, 78.4804)
        r2 = provider.get_route(17.3616, 78.4747, 17.3713, 78.4804)

        assert r1 is not None
        assert r2 is not None
        assert r1 == r2
        # Exactly one network invocation
        assert mock_get.call_count == 1


def test_provider_disabled_flag():
    """When ROUTING_PROVIDER_ENABLED=false, provider returns None without any network call."""
    disabled_provider = OSRMRoutingProvider(enabled=False)

    with patch("httpx.Client.get") as mock_get:
        res = disabled_provider.get_route(17.3616, 78.4747, 17.3639, 78.4735)
        assert res is None
        mock_get.assert_not_called()
