"""Services package for TripPilot."""
from app.services.trip_planner import (
    get_all_destinations,
    get_destination_by_id,
    create_trip_plan,
    adapt_trip_plan,
)
from app.services.bedrock_service import (
    BedrockService,
    BedrockConfig,
    BedrockStatusResponse,
    BedrockInvocationResult,
    apply_bedrock_enrichment,
    DEFAULT_BEDROCK_MODEL_ID,
    DEFAULT_AWS_REGION,
)

from app.services.route_service import (
    haversine_distance_km,
    estimate_transit_time_and_mode,
    build_route_segment,
    build_day_route_segments,
)
from app.services.routing_provider import (
    BaseRoutingProvider,
    OSRMRoutingProvider,
    get_routing_provider,
    set_routing_provider,
)

__all__ = [
    "get_all_destinations",
    "get_destination_by_id",
    "create_trip_plan",
    "adapt_trip_plan",
    "BedrockService",
    "BedrockConfig",
    "BedrockStatusResponse",
    "BedrockInvocationResult",
    "apply_bedrock_enrichment",
    "DEFAULT_BEDROCK_MODEL_ID",
    "DEFAULT_AWS_REGION",
    "haversine_distance_km",
    "estimate_transit_time_and_mode",
    "build_route_segment",
    "build_day_route_segments",
    "BaseRoutingProvider",
    "OSRMRoutingProvider",
    "get_routing_provider",
    "set_routing_provider",
]


