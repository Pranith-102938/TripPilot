import logging
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.models import (
    HealthResponse,
    Destination,
    TripPlanRequest,
    TripPlanResponse,
    AdaptTripRequest,
)
from app.services.trip_planner import (
    get_all_destinations,
    get_destination_by_id,
    create_trip_plan,
    adapt_trip_plan,
)
from app.services.bedrock_service import (
    BedrockService,
    BedrockStatusResponse,
    BedrockInvocationResult,
    apply_bedrock_enrichment,
)

from app.tools import (
    optimize_budget,
    adjust_trip_duration,
    adjust_travel_style,
    select_interest_activities,
    validate_trip_constraints,
    BudgetOptimizerInput,
    BudgetOptimizerOutput,
    DurationAdjusterInput,
    DurationAdjusterOutput,
    TravelStyleAdjusterInput,
    TravelStyleAdjusterOutput,
    ActivitySelectorInput,
    ActivitySelectorOutput,
    ConstraintValidatorInput,
    ConstraintValidatorOutput,
)
from app.agent import (
    StrandsAgentService,
    AgentPlanRequest,
    AgentPlanResponse,
    STRANDS_REGISTERED_TOOLS,
)


logger = logging.getLogger("trippilot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(
    title="TripPilot API",
    description="Deterministic travel planning engine for Phase 2. Integrations with Strands Decider 2B & Amazon Bedrock arrive in Phase 3.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Explicitly allowed local development origins (safe CORS configuration)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors into friendly, readable JSON."""
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid trip parameters provided.",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Prevents stack trace leaks to client for unhandled exceptions."""
    logger.error("Unhandled internal server error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your trip plan. Please try again."
        }
    )


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health():
    """Returns backend system status. Does not claim AI integration is active."""
    return HealthResponse()


@app.get("/api/destinations", response_model=List[Destination], tags=["Destinations"])
def list_destinations(search: Optional[str] = None, category: Optional[str] = None):
    """Returns curated destinations in India with optional search and category filters."""
    raw_destinations = get_all_destinations(search=search, category=category)
    return [Destination.model_validate(d) for d in raw_destinations]


@app.get("/api/destinations/{destination_id}", response_model=Destination, tags=["Destinations"])
def get_destination(destination_id: str):
    """Returns details for a single destination or 404."""
    dest = get_destination_by_id(destination_id)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination '{destination_id}' was not found in curated datasets."
        )
    return Destination.model_validate(dest)


@app.post("/api/trips/plan", response_model=TripPlanResponse, tags=["Trips"])
def plan_trip(request: TripPlanRequest, enrich: bool = False):
    """
    Constructs a validated trip itinerary and complete budget breakdown.
    Uses deterministic benchmarks and verifies mathematical integrity.
    Optionally enriches with Bedrock when enrich=True.
    """
    try:
        plan = create_trip_plan(request)
        if enrich:
            plan = apply_bedrock_enrichment(plan, bedrock_service)
        return plan
    except ValueError as e:
        err_msg = str(e)
        if "Unknown destination" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=422, detail=err_msg)


@app.post("/api/trips/enrich", response_model=TripPlanResponse, tags=["Trips"])
def enrich_trip(plan: TripPlanResponse):
    """
    Enriches an existing deterministic trip plan with Amazon Bedrock narrative,
    cultural etiquette guidance, and culinary highlights.
    Strictly preserves all deterministic costs, dates, activities, and constraints.
    """
    return apply_bedrock_enrichment(plan, bedrock_service)


@app.post("/api/trips/adapt", response_model=TripPlanResponse, tags=["Trips"])
def adapt_trip(request: AdaptTripRequest):
    """
    Applies adaptive planning actions:
    - reduce_budget
    - shorten_trip
    - change_travel_style
    """
    try:
        return adapt_trip_plan(request)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )


# =====================================================================
# Phase 3: Modular Travel Planning Tools Endpoints
# =====================================================================

@app.post("/api/tools/optimize-budget", response_model=BudgetOptimizerOutput, tags=["Tools"])
def tool_optimize_budget(payload: BudgetOptimizerInput):
    """
    Tool 1: Optimizes accommodation, food, transit, and activities to fit target budget.
    Recalculates all costs deterministically and never claims to fit if a deficit remains.
    """
    try:
        return optimize_budget(itinerary=payload.itinerary, target_budget=payload.target_budget)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/tools/adjust-duration", response_model=DurationAdjusterOutput, tags=["Tools"])
def tool_adjust_duration(payload: DurationAdjusterInput):
    """
    Tool 2: Shortens or extends trip duration (1-30 days) with non-duplicated schedules.
    """
    try:
        return adjust_trip_duration(itinerary=payload.itinerary, target_days=payload.target_days)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/tools/adjust-travel-style", response_model=TravelStyleAdjusterOutput, tags=["Tools"])
def tool_adjust_travel_style(payload: TravelStyleAdjusterInput):
    """
    Tool 3: Recalibrates accommodation class, dining, and transit tariffs across budget/balanced/comfort.
    """
    try:
        return adjust_travel_style(itinerary=payload.itinerary, target_style=payload.target_style)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/tools/select-activities", response_model=ActivitySelectorOutput, tags=["Tools"])
def tool_select_activities(payload: ActivitySelectorInput):
    """
    Tool 4: Prioritizes and selects activities matching user interests, providing full selection rationales.
    """
    try:
        return select_interest_activities(
            destination=payload.destination,
            interests=payload.interests,
            days=payload.days,
            travel_style=payload.travel_style,
            is_custom_destination=payload.is_custom_destination
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/tools/validate-constraints", response_model=ConstraintValidatorOutput, tags=["Tools"])
def tool_validate_constraints(payload: ConstraintValidatorInput):
    """
    Tool 5: Validates destination support, duration (1-30 days), and minimum feasible budget feasibility.
    """
    return validate_trip_constraints(
        destination=payload.destination,
        days=payload.days,
        budget=payload.budget,
        travel_style=payload.travel_style,
        interests=payload.interests,
        starting_city=payload.starting_city,
        is_custom_destination=payload.is_custom_destination
    )


# =====================================================================
# Phase 4: Strands Agents SDK & Decider 2B Autonomous Agent Endpoints
# =====================================================================

agent_service = StrandsAgentService()


@app.get("/api/agent/status", tags=["Agent"])
def get_agent_status():
    """
    Returns connectivity status, active model identifier (StrandsAgents/strands-decider-2B),
    and registered Strands tools available for autonomous selection.
    """
    provider_status = agent_service.client.get_provider_status()
    return {
        "status": "ok",
        "model": agent_service.client.model_name,
        "endpoint": agent_service.client.endpoint,
        "provider": provider_status,
        "registered_tools": [
            {
                "name": name,
                "description": meta["description"],
                "criteria": meta["criteria"],
            }
            for name, meta in STRANDS_REGISTERED_TOOLS.items()
        ],
    }


@app.post("/api/agent/plan", response_model=AgentPlanResponse, tags=["Agent"])
def agent_plan(payload: AgentPlanRequest):
    """
    Autonomous travel planning and adaptation using Strands Decider 2B.
    Decider 2B evaluates the user request and selects appropriate tools sequentially.
    If the inference backend is unreachable, transparently reports provider status
    without simulating or claiming that the agent ran.
    """
    return agent_service.plan(payload)


# =====================================================================
# Phase 5: Amazon Bedrock Runtime Endpoints
# =====================================================================

bedrock_service = BedrockService()


@app.get("/api/bedrock/status", response_model=BedrockStatusResponse, tags=["Bedrock"])
def get_bedrock_status():
    """Returns Amazon Bedrock Runtime availability, region, and model ID."""
    return bedrock_service.get_status()


class BedrockNarrativeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    destination: str
    duration_days: int = Field(..., alias="durationDays")
    travel_style: str = Field(default="balanced", alias="travelStyle")
    highlights: Optional[List[str]] = None


@app.post("/api/bedrock/narrative", response_model=BedrockInvocationResult, tags=["Bedrock"])
def generate_narrative(payload: BedrockNarrativeRequest):
    """Generates travel narrative and cultural tips via Bedrock Claude Converse API."""
    return bedrock_service.generate_travel_narrative(
        destination=payload.destination,
        duration_days=payload.duration_days,
        travel_style=payload.travel_style,
        highlights=payload.highlights,
    )


