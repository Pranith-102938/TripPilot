"""Pydantic schemas and models for TripPilot API."""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "TripPilot Backend"
    version: str = "1.0.0"
    phase: str = "Phase 2 - FastAPI Backend Foundation"
    ai_connected: bool = False
    message: str = "FastAPI backend running. AI integrations scheduled for Phase 3."


class IndicativeDailyCost(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    budget: int
    balanced: int
    comfort: int


class CoordinatePrecision(str, Enum):
    VERIFIED_ATTRACTION = "verified_attraction"
    CITY_CENTER = "city_center"
    APPROXIMATE = "approximate"
    UNAVAILABLE = "unavailable"


class GeoPoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    precision: CoordinatePrecision = Field(default=CoordinatePrecision.VERIFIED_ATTRACTION)
    address_label: Optional[str] = Field(default=None, alias="addressLabel")


class RouteSegment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_slot: str = Field(..., alias="fromSlot")
    to_slot: str = Field(..., alias="toSlot")
    from_title: str = Field(..., alias="fromTitle")
    to_title: str = Field(..., alias="toTitle")
    from_location: str = Field(..., alias="fromLocation")
    to_location: str = Field(..., alias="toLocation")
    distance_km: Optional[float] = Field(default=None, alias="distanceKm")
    duration_minutes: Optional[int] = Field(default=None, alias="durationMinutes")
    transit_mode: Optional[str] = Field(default="auto_rickshaw", alias="transitMode")
    is_route_calculated: bool = Field(default=False, alias="isRouteCalculated")
    geometry_source: str = Field(default="unavailable", alias="geometrySource", description="'osrm_road', 'haversine_circuity', or 'unavailable'")
    polyline: Optional[List[List[float]]] = Field(
        default=None,
        description="Array of [lat, lng] coordinates representing the straight-line/circuity-estimated path or road geometry"
    )
    route_type: str = Field(
        default="approximate_estimate",
        alias="routeType",
        description="'road', 'approximate_estimate', or 'unavailable'"
    )
    provider: Optional[str] = Field(default=None, description="Name of routing provider if used, e.g. 'osrm'")
    traffic_notice: Optional[str] = Field(default=None, alias="trafficNotice")
    fallback_reason: Optional[str] = Field(default=None, alias="fallbackReason")



class Destination(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    name: str
    state: str
    tagline: str
    description: str
    image: str
    fallback_image: str = Field(..., alias="fallbackImage")
    indicative_daily_cost: IndicativeDailyCost = Field(..., alias="indicativeDailyCost")
    indicative_range: str = Field(..., alias="indicativeRange")
    best_time_to_visit: str = Field(..., alias="bestTimeToVisit")
    primary_interests: List[str] = Field(..., alias="primaryInterests")
    highlights: List[str]
    center_coordinates: Optional[GeoPoint] = Field(default=None, alias="centerCoordinates")


class BookingResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    url: str = Field(..., description="Verified direct URL to official authority or ticketing portal")
    provider_name: str = Field(..., alias="providerName", description="Name of official authority or platform")
    resource_type: str = Field(default="official_portal", alias="resourceType", description="official_monument | official_museum | official_park | official_tourism | official_transit")
    label: str = Field(..., description="Actionable button text, e.g. 'Official ASI Monument Portal ↗'")
    description: Optional[str] = Field(default=None, description="Helpful note e.g. 'Online e-tickets via Archaeological Survey of India'")
    is_verified: bool = Field(default=True, alias="isVerified")


class Activity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    period: str
    time: str
    title: str
    location: str
    cost: int
    explanation: str
    category: str
    duration: Optional[str] = Field(default=None, description="Suggested duration of stop, e.g. '2.5 hours'")
    practical_tips: Optional[str] = Field(default=None, alias="practicalTips", description="Practical tips: attire, gear, customs, booking")
    meal_suggestion: Optional[str] = Field(default=None, alias="mealSuggestion", description="Suggested regional culinary experience")
    transit_note: Optional[str] = Field(default=None, alias="transitNote", description="Sensible route order or estimated transit note")
    is_cost_estimated: bool = Field(default=True, alias="isCostEstimated", description="Whether activity fee is an estimate")
    coordinates: Optional[GeoPoint] = Field(default=None, description="Optional physical coordinates of this stop")
    booking_resource: Optional[BookingResource] = Field(default=None, alias="bookingResource", description="Optional verified official booking or information portal")


class DayItinerary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    day_number: int = Field(..., alias="dayNumber")
    theme: str
    morning: Activity
    afternoon: Activity
    evening: Activity
    day_stay: int = Field(default=0, alias="dayStay", description="Estimated accommodation cost for this day")
    day_food: int = Field(default=0, alias="dayFood", description="Estimated food cost for this day")
    day_transit: int = Field(default=0, alias="dayTransit", description="Estimated local transport cost for this day")
    day_activities: int = Field(default=0, alias="dayActivities", description="Sum of activity fees for this day")
    day_total: int = Field(default=0, alias="dayTotal", description="Sum of all costs for this day")
    is_cost_verified: bool = Field(default=True, alias="isCostVerified", description="Whether day costs are verified regional benchmarks")
    route_segments: List[RouteSegment] = Field(default_factory=list, alias="routeSegments")
    day_route_distance_km: Optional[float] = Field(default=None, alias="dayRouteDistanceKm")
    has_road_routes: bool = Field(default=False, alias="hasRoadRoutes")



class TravelStyleEnum(str, Enum):
    BUDGET = "budget"
    BALANCED = "balanced"
    COMFORT = "comfort"


class TripPlanRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    starting_city: str = Field(..., alias="startingCity", min_length=1, description="Departure hub in India")
    destination_id: str = Field(..., alias="destinationId", min_length=1, description="Target destination ID or 'custom'")
    custom_destination_name: Optional[str] = Field(default=None, alias="customDestinationName", description="Custom destination name if manually entered")
    is_custom_destination: bool = Field(default=False, alias="isCustomDestination", description="Flag indicating destination was manually entered")
    days: int = Field(..., ge=1, le=30, description="Number of travel days (1 to 30 supported)")
    budget: float = Field(..., ge=5000, description="Total budget in INR (minimum ₹5,000)")
    interests: List[str] = Field(..., min_length=1, description="List of traveler interest tags")
    travel_style: TravelStyleEnum = Field(default=TravelStyleEnum.BALANCED, alias="travelStyle")
    budget_optimized: bool = Field(default=False, alias="budgetOptimized")

    @field_validator("starting_city", "destination_id")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Field cannot be empty")
        return s


class BudgetBreakdown(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    daily_stay: int = Field(..., alias="dailyStay")
    daily_food: int = Field(..., alias="dailyFood")
    daily_transit: int = Field(..., alias="dailyTransit")
    accommodation_cost: int = Field(..., alias="accommodationCost")
    food_cost: int = Field(..., alias="foodCost")
    transport_cost: int = Field(..., alias="transportCost")
    activities_cost: int = Field(..., alias="activitiesCost")
    total_estimated_cost: int = Field(..., alias="totalEstimatedCost")
    user_budget: float = Field(..., alias="userBudget")
    remaining_budget: float = Field(..., alias="remainingBudget")
    is_over_budget: bool = Field(..., alias="isOverBudget")
    deficit: float = Field(default=0, description="Deficit amount in INR when over budget")


class DailyEnrichment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    day_number: int = Field(..., alias="dayNumber")
    theme_note: Optional[str] = Field(default=None, alias="themeNote")
    practical_tip: Optional[str] = Field(default=None, alias="practicalTip")
    culinary_highlight: Optional[str] = Field(default=None, alias="culinaryHighlight")


class BedrockItineraryEnrichment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="'enriched', 'provider_unavailable', or 'error'")
    model_id: str = Field(..., alias="modelId")
    narrative: Optional[str] = None
    cultural_guidance: Optional[str] = Field(default=None, alias="culturalGuidance")
    local_food_guide: Optional[str] = Field(default=None, alias="localFoodGuide")
    daily_insights: List[DailyEnrichment] = Field(default_factory=list, alias="dailyInsights")
    latency_ms: Optional[float] = Field(default=None, alias="latencyMs")
    error: Optional[str] = None


class TripPlanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    destination: Destination
    starting_city: Optional[str] = Field(None, alias="startingCity")
    itinerary_title: str = Field(..., alias="itineraryTitle")
    itinerary_summary: str = Field(..., alias="itinerarySummary")
    num_days: int = Field(..., alias="numDays")
    active_days: List[DayItinerary] = Field(..., alias="activeDays")
    travel_style: str = Field(..., alias="travelStyle")
    budget_optimized: bool = Field(..., alias="budgetOptimized")
    
    # Itemized budget breakdown
    daily_stay: int = Field(..., alias="dailyStay")
    daily_food: int = Field(..., alias="dailyFood")
    daily_transit: int = Field(..., alias="dailyTransit")
    accommodation_cost: int = Field(..., alias="accommodationCost")
    food_cost: int = Field(..., alias="foodCost")
    transport_cost: int = Field(..., alias="transportCost")
    activities_cost: int = Field(..., alias="activitiesCost")
    total_estimated_cost: int = Field(..., alias="totalEstimatedCost")
    user_budget: float = Field(..., alias="userBudget")
    remaining_budget: float = Field(..., alias="remainingBudget")
    is_over_budget: bool = Field(..., alias="isOverBudget")
    deficit: float = Field(default=0)

    is_verified: bool = Field(default=True, alias="isVerified", description="False when destination was manually entered with unverified benchmarks")
    is_sample: bool = Field(default=True, alias="isSample")
    disclaimer: str = Field(
        default="Sample Itinerary & Deterministic Pricing: Displaying verified regional benchmarks. Phase 3 will introduce adaptive multi-agent reasoning with Strands Decider 2B and Amazon Bedrock."
    )
    ai_enrichment: Optional[BedrockItineraryEnrichment] = Field(
        default=None,
        alias="aiEnrichment",
        description="Amazon Bedrock AI enrichment (narrative, cultural guidance, culinary highlights) that never alters deterministic planning data"
    )
    map_center: Optional[GeoPoint] = Field(
        default=None,
        alias="mapCenter",
        description="Geographic center of the destination for map view initialization"
    )
    total_route_distance_km: Optional[float] = Field(
        default=None,
        alias="totalRouteDistanceKm",
        description="Estimated aggregate route distance in kilometers across all active days"
    )
    route_provider: Optional[str] = Field(
        default=None,
        alias="routeProvider",
        description="Active road routing provider (e.g., 'osrm') if road routes were calculated, or None"
    )
    has_road_routes: bool = Field(
        default=False,
        alias="hasRoadRoutes",
        description="True if any daily segment uses provider-calculated road routes"
    )



class AdaptActionEnum(str, Enum):
    REDUCE_BUDGET = "reduce_budget"
    SHORTEN_TRIP = "shorten_trip"
    CHANGE_TRAVEL_STYLE = "change_travel_style"


class AdaptTripRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: str = Field(..., description="Action to perform: reduce_budget, shorten_trip, or change_travel_style")
    plan_request: TripPlanRequest = Field(..., alias="planRequest")
    new_travel_style: Optional[str] = Field(None, alias="newTravelStyle", description="Required if action is change_travel_style")
