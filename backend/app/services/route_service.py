"""Route calculation and transit estimation service for TripPilot Phase 6.3.

Provides pluggable road routing using the OSRM public demo service with
graceful, deterministic fallback to Haversine great-circle circuity estimation.

IMPORTANT TRANSPARENCY PRINCIPLE:
- Provider road routes are tagged with routeType="road" and geometrySource="osrm_road".
- Fallback estimates are explicitly tagged with routeType="approximate_estimate"
  and geometrySource="haversine_circuity".
- Approximate estimates are NEVER represented as actual turn-by-turn road routes.
- OSRM calculations represent static road network geometry; real-time dynamic traffic
  congestion is not included.
"""
import math
from typing import Optional, Dict, Any, List, Union

from app.models import GeoPoint, RouteSegment, CoordinatePrecision
from app.services.routing_provider import (
    BaseRoutingProvider,
    OSRMRoutingProvider,
    get_routing_provider,
)

EARTH_RADIUS_KM = 6371.0
ROAD_CIRCUITY_FACTOR = 1.30  # Standard empirical circuity for urban/suburban Indian road networks


def haversine_distance_km(
    coord1: Union[GeoPoint, Dict[str, Any]],
    coord2: Union[GeoPoint, Dict[str, Any]]
) -> float:
    """
    Calculates great-circle distance in kilometers between two geographic coordinates
    using the Haversine formula.
    """
    lat1 = coord1.lat if isinstance(coord1, GeoPoint) else coord1["lat"]
    lng1 = coord1.lng if isinstance(coord1, GeoPoint) else coord1["lng"]
    lat2 = coord2.lat if isinstance(coord2, GeoPoint) else coord2["lat"]
    lng2 = coord2.lng if isinstance(coord2, GeoPoint) else coord2["lng"]

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def estimate_transit_time_and_mode(distance_km: float) -> Dict[str, Any]:
    """
    Derives realistic transit mode and duration estimates based on road-circuity distance.
    Applies empirical Indian transit speeds and buffer times:
      - <= 1.5 km: walking at 4.5 km/h
      - 1.5 to 8.0 km: auto-rickshaw at 20 km/h + 5 min traffic buffer
      - > 8.0 km: taxi/cab at 30 km/h + 10 min traffic buffer
    """
    road_dist = max(0.1, distance_km * ROAD_CIRCUITY_FACTOR)

    if road_dist <= 1.5:
        mode = "walking"
        duration = max(5, round((road_dist / 4.5) * 60))
    elif road_dist <= 8.0:
        mode = "auto_rickshaw"
        duration = max(8, round((road_dist / 20.0) * 60) + 5)
    else:
        mode = "taxi"
        duration = max(15, round((road_dist / 30.0) * 60) + 10)

    return {
        "estimatedDistanceKm": round(road_dist, 1),
        "durationMinutes": int(duration),
        "transitMode": mode
    }


def build_route_segment(
    from_slot: str,
    to_slot: str,
    from_act: Dict[str, Any],
    to_act: Dict[str, Any],
    routing_provider: Optional[BaseRoutingProvider] = None
) -> RouteSegment:
    """
    Constructs a RouteSegment between two consecutive itinerary activity stops.
    1. If coordinates are missing or invalid, returns an unavailable segment (no network calls).
    2. Attempts provider-calculated road routing (e.g. OSRM) with valid road geometry and metrics.
    3. If provider is disabled, times out, or errors, falls back seamlessly to Haversine circuity.
    """
    from_title = from_act.get("title", f"{from_slot.capitalize()} Activity")
    to_title = to_act.get("title", f"{to_slot.capitalize()} Activity")
    from_loc = from_act.get("location", "")
    to_loc = to_act.get("location", "")

    from_coords = from_act.get("coordinates")
    to_coords = to_act.get("coordinates")

    # Check if both coordinates are valid objects with lat and lng
    has_valid_coords = False
    f_lat, f_lng, t_lat, t_lng = None, None, None, None
    if from_coords and to_coords:
        f_lat = getattr(from_coords, "lat", None) or (from_coords.get("lat") if isinstance(from_coords, dict) else None)
        f_lng = getattr(from_coords, "lng", None) or (from_coords.get("lng") if isinstance(from_coords, dict) else None)
        t_lat = getattr(to_coords, "lat", None) or (to_coords.get("lat") if isinstance(to_coords, dict) else None)
        t_lng = getattr(to_coords, "lng", None) or (to_coords.get("lng") if isinstance(to_coords, dict) else None)
        if (
            f_lat is not None and f_lng is not None and t_lat is not None and t_lng is not None
            and isinstance(f_lat, (int, float)) and isinstance(f_lng, (int, float))
            and isinstance(t_lat, (int, float)) and isinstance(t_lng, (int, float))
            and -90.0 <= f_lat <= 90.0 and -180.0 <= f_lng <= 180.0
            and -90.0 <= t_lat <= 90.0 and -180.0 <= t_lng <= 180.0
        ):
            has_valid_coords = True

    if not has_valid_coords:
        return RouteSegment(
            from_slot=from_slot,
            to_slot=to_slot,
            from_title=from_title,
            to_title=to_title,
            from_location=from_loc,
            to_location=to_loc,
            distance_km=None,
            duration_minutes=None,
            transit_mode="auto_rickshaw",
            is_route_calculated=False,
            geometry_source="unavailable",
            polyline=None,
            route_type="unavailable",
            provider=None,
            traffic_notice=None,
            fallback_reason="missing_coordinates"
        )

    # Coordinates are valid: attempt road routing via configured provider
    active_provider = routing_provider or get_routing_provider()
    road_data: Optional[Dict[str, Any]] = None

    if active_provider:
        road_data = active_provider.get_route(f_lat, f_lng, t_lat, t_lng)

    if road_data is not None:
        # Provider road route succeeded
        dist_km = road_data["distance_km"]
        raw_duration = road_data["duration_minutes"]

        # Determine sensible transit mode based on road distance
        if dist_km <= 1.2:
            mode = "walking"
            duration = max(5, round((dist_km / 4.5) * 60))
        elif dist_km <= 8.0:
            mode = "auto_rickshaw"
            duration = max(8, raw_duration + 3)
        else:
            mode = "taxi"
            duration = max(15, raw_duration + 5)

        return RouteSegment(
            from_slot=from_slot,
            to_slot=to_slot,
            from_title=from_title,
            to_title=to_title,
            from_location=from_loc,
            to_location=to_loc,
            distance_km=dist_km,
            duration_minutes=duration,
            transit_mode=mode,
            is_route_calculated=True,
            geometry_source=road_data.get("geometry_source", "osrm_road"),
            polyline=road_data.get("polyline"),
            route_type="road",
            provider=road_data.get("provider", "osrm"),
            traffic_notice=road_data.get("traffic_notice", "Static road network calculation (OSRM). Real-time traffic congestion not included."),
            fallback_reason=None
        )

    # Provider road route failed or was disabled: fall back to Haversine circuity
    straight_km = haversine_distance_km(from_coords, to_coords)
    transit_info = estimate_transit_time_and_mode(straight_km)

    return RouteSegment(
        from_slot=from_slot,
        to_slot=to_slot,
        from_title=from_title,
        to_title=to_title,
        from_location=from_loc,
        to_location=to_loc,
        distance_km=transit_info["estimatedDistanceKm"],
        duration_minutes=transit_info["durationMinutes"],
        transit_mode=transit_info["transitMode"],
        is_route_calculated=True,
        geometry_source="haversine_circuity",
        polyline=[[round(f_lat, 5), round(f_lng, 5)], [round(t_lat, 5), round(t_lng, 5)]],
        route_type="approximate_estimate",
        provider=None,
        traffic_notice="Empirical circuity estimate (1.30x great-circle). Not an actual turn-by-turn road route.",
        fallback_reason="road_routing_unavailable_or_unreachable"
    )


def build_day_route_segments(
    day_dict: Dict[str, Any],
    routing_provider: Optional[BaseRoutingProvider] = None
) -> List[RouteSegment]:
    """
    Generates route segments for a day:
      1. morning -> afternoon
      2. afternoon -> evening
    """
    segments: List[RouteSegment] = []
    morning = day_dict.get("morning", {})
    afternoon = day_dict.get("afternoon", {})
    evening = day_dict.get("evening", {})

    if morning and afternoon:
        segments.append(build_route_segment("morning", "afternoon", morning, afternoon, routing_provider))
    if afternoon and evening:
        segments.append(build_route_segment("afternoon", "evening", afternoon, evening, routing_provider))

    return segments
