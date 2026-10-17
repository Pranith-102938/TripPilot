"""Pydantic schemas for Strands Agent service and Decider 2B integration."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models import TripPlanResponse


class AgentPlanRequest(BaseModel):
    """User request payload for autonomous agent planning and adaptation."""
    user_request: str = Field(
        ...,
        min_length=3,
        description="Natural-language planning instruction, constraint adjustment, or travel preference."
    )
    destination_id: Optional[str] = Field(
        None,
        description="Destination ID if planning for a specific destination."
    )
    destination_name: Optional[str] = Field(
        None,
        description="Destination display name or unverified custom destination."
    )
    starting_city: Optional[str] = Field(
        None,
        description="Starting origin city in India."
    )
    duration: Optional[int] = Field(
        None,
        ge=1,
        le=30,
        description="Requested trip duration (1-30 days)."
    )
    budget: Optional[float] = Field(
        None,
        ge=0,
        description="User budget in INR."
    )
    travel_style: Optional[str] = Field(
        None,
        description="Travel style: budget, balanced, or comfort."
    )
    interests: Optional[List[str]] = Field(
        None,
        description="User travel interests (Heritage, Nature, Food, Adventure, Relaxation)."
    )
    current_itinerary: Optional[TripPlanResponse] = Field(
        None,
        description="Current trip plan when adapting an existing itinerary."
    )


class ToolSelectionTrace(BaseModel):
    """Detailed trace of an individual tool selected and executed by Decider 2B."""
    step: int
    tool_name: str
    confidence: float
    probabilities: Dict[str, float]
    rationale: str
    inputs: Dict[str, Any]
    output_summary: str
    is_success: bool = True


class AgentPlanResponse(BaseModel):
    """Structured response returned by the Strands Decider 2B Agent."""
    status: str = Field(
        ...,
        description="'success', 'provider_unavailable', or 'error'"
    )
    model: str = Field(
        default="StrandsAgents/strands-decider-2B",
        description="Official Strands Decider 2B model identifier used for tool selection."
    )
    execution_mode: str = Field(
        ...,
        description="'strands_decider_2b_live' or 'provider_unavailable'"
    )
    explanation: str = Field(
        ...,
        description="Explanation of actions selected by Strands Decider 2B and plan adjustments."
    )
    selected_tools: List[str] = Field(
        default_factory=list,
        description="List of tool names selected sequentially by Strands Decider 2B."
    )
    tool_traces: List[ToolSelectionTrace] = Field(
        default_factory=list,
        description="Step-by-step tool selection probabilities, confidence, and execution results."
    )
    itinerary: Optional[TripPlanResponse] = Field(
        None,
        description="The resulting updated trip itinerary."
    )
    provider_status: Dict[str, Any] = Field(
        default_factory=dict,
        description="Health and connectivity details for the Strands Decider 2B inference backend."
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the agent encountered provider or validation failure."
    )
