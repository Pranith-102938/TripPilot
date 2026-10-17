"""TripPilot Phase 3: Modular Travel Planning Tools.

This package provides 5 independent, reusable travel planning tools designed for
deterministic execution and ready for registration with the Strands Agents SDK in Phase 4:

1. optimize_budget: Reduces stay, food, transit, and activities deterministically.
2. adjust_trip_duration: Extends or shortens itineraries (1–30 days) with non-duplicated schedules.
3. adjust_travel_style: Recalibrates tariffs across Budget, Balanced, and Comfort.
4. select_interest_activities: Aligns and prioritizes activities by user interests with full rationale.
5. validate_trip_constraints: Validates inputs, budget feasibility, and detects conflicts without silent changes.
"""

from app.tools.schemas import (
    BudgetOptimizerInput,
    BudgetOptimizerOutput,
    DurationAdjusterInput,
    DurationAdjusterOutput,
    TravelStyleAdjusterInput,
    TravelStyleAdjusterOutput,
    ActivitySelectorInput,
    ActivitySelectorOutput,
    SelectedActivityItem,
    ConstraintValidatorInput,
    ConstraintValidatorOutput,
)
from app.tools.budget_optimizer import optimize_budget
from app.tools.duration_adjuster import adjust_trip_duration
from app.tools.travel_style_adjuster import adjust_travel_style
from app.tools.activity_selector import select_interest_activities
from app.tools.constraint_validator import validate_trip_constraints

__all__ = [
    "optimize_budget",
    "adjust_trip_duration",
    "adjust_travel_style",
    "select_interest_activities",
    "validate_trip_constraints",
    "BudgetOptimizerInput",
    "BudgetOptimizerOutput",
    "DurationAdjusterInput",
    "DurationAdjusterOutput",
    "TravelStyleAdjusterInput",
    "TravelStyleAdjusterOutput",
    "ActivitySelectorInput",
    "ActivitySelectorOutput",
    "SelectedActivityItem",
    "ConstraintValidatorInput",
    "ConstraintValidatorOutput",
]

# Tool metadata registry ready for Strands Agents SDK registration in Phase 4
PLANNING_TOOLS_REGISTRY = {
    "optimize_budget": {
        "callable": optimize_budget,
        "input_schema": BudgetOptimizerInput,
        "output_schema": BudgetOptimizerOutput,
        "description": "Optimizes an itinerary's accommodation, food, transit, and activity costs to fit a target budget using deterministic reduction tiers.",
    },
    "adjust_trip_duration": {
        "callable": adjust_trip_duration,
        "input_schema": DurationAdjusterInput,
        "output_schema": DurationAdjusterOutput,
        "description": "Adjusts trip duration between 1 and 30 days without duplicating daily schedules, recalculating all affected expenses.",
    },
    "adjust_travel_style": {
        "callable": adjust_travel_style,
        "input_schema": TravelStyleAdjusterInput,
        "output_schema": TravelStyleAdjusterOutput,
        "description": "Recalibrates an itinerary between Budget, Balanced, and Comfort travel styles while preserving destination and duration.",
    },
    "select_interest_activities": {
        "callable": select_interest_activities,
        "input_schema": ActivitySelectorInput,
        "output_schema": ActivitySelectorOutput,
        "description": "Selects and prioritizes activities aligned with traveler interests, providing transparent selection rationales.",
    },
    "validate_trip_constraints": {
        "callable": validate_trip_constraints,
        "input_schema": ConstraintValidatorInput,
        "output_schema": ConstraintValidatorOutput,
        "description": "Validates destination support, duration (1–30 days), minimum feasible budget, and detects conflicting requirements without silent mutation.",
    },
}
