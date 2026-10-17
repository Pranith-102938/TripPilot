"""Pydantic schemas for Phase 3 modular travel planning tools."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models import TripPlanResponse, TravelStyleEnum, Activity


class BudgetOptimizerInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    itinerary: TripPlanResponse
    target_budget: Optional[float] = Field(default=None, description="Target budget limit in INR. Defaults to userBudget if omitted.")


class BudgetOptimizerOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    original_budget: float
    target_budget: float
    initial_cost: int
    final_cost: int
    initial_deficit: float
    final_deficit: float
    remaining_budget: float
    fits_budget: bool
    changes_made: List[str]
    revised_itinerary: TripPlanResponse
    explanation: str


class DurationAdjusterInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    itinerary: TripPlanResponse
    target_days: int = Field(..., ge=1, le=30, description="New target duration between 1 and 30 days")


class DurationAdjusterOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    original_days: int
    target_days: int
    days_delta: int
    action_taken: str  # "extended", "shortened", "unchanged"
    changes_made: List[str]
    revised_itinerary: TripPlanResponse
    explanation: str


class TravelStyleAdjusterInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    itinerary: TripPlanResponse
    target_style: TravelStyleEnum = Field(..., description="Target travel style: budget, balanced, or comfort")


class TravelStyleAdjusterOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    original_style: str
    target_style: str
    cost_delta: int
    changes_made: List[str]
    revised_itinerary: TripPlanResponse
    explanation: str


class ActivitySelectorInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    destination: str = Field(..., description="Destination identifier or custom name")
    interests: List[str] = Field(..., min_length=1, description="List of user interest tags (e.g. nature, culture, food)")
    days: int = Field(default=3, ge=1, le=30, description="Number of days to select activities for")
    travel_style: TravelStyleEnum = Field(default=TravelStyleEnum.BALANCED)
    is_custom_destination: bool = Field(default=False)


class SelectedActivityItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    day_number: int = Field(..., alias="dayNumber")
    slot: str
    activity: Activity
    matched_interest: Optional[str] = Field(default=None, alias="matchedInterest")
    is_curated: bool = Field(..., alias="isCurated")
    selection_rationale: str = Field(..., alias="selectionRationale")


class ActivitySelectorOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    destination_id: str = Field(..., alias="destinationId")
    destination_name: str = Field(..., alias="destinationName")
    is_curated: bool = Field(..., alias="isCurated")
    matched_interests: List[str] = Field(..., alias="matchedInterests")
    unmatched_interests: List[str] = Field(..., alias="unmatchedInterests")
    selected_activities: List[SelectedActivityItem] = Field(..., alias="selectedActivities")
    rationale_summary: str = Field(..., alias="rationaleSummary")


class ConstraintValidatorInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    destination: str = Field(..., description="Destination ID or custom destination name")
    days: int = Field(..., description="Requested duration in days")
    budget: float = Field(..., description="Total proposed budget in INR")
    travel_style: Optional[str] = Field(default="balanced", alias="travelStyle")
    interests: Optional[List[str]] = Field(default=None)
    starting_city: Optional[str] = Field(default=None, alias="startingCity")
    is_custom_destination: bool = Field(default=False, alias="isCustomDestination")


class ConstraintValidatorOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    is_valid: bool = Field(..., alias="isValid")
    errors: List[str]
    warnings: List[str]
    feasible_budget_min: int = Field(..., alias="feasibleBudgetMin")
    feasible_budget_max: int = Field(..., alias="feasibleBudgetMax")
    conflicts_detected: List[str] = Field(..., alias="conflictsDetected")
    recommendations: List[str]
