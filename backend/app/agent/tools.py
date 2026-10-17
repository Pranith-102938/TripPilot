"""Strands SDK Tool Registration for TripPilot Planning Tools.

Equips the 5 deterministic travel planning tools with the official Strands SDK
@tool decorator, extracting OpenAPI-compliant tool specifications and parameter schemas.
"""
from typing import Dict, Any, Callable
from strands import tool

from app.tools import (
    optimize_budget,
    adjust_trip_duration,
    adjust_travel_style,
    select_interest_activities,
    validate_trip_constraints,
)

# Register each planning tool with the official Strands SDK @tool decorator
strands_optimize_budget = tool(optimize_budget)
strands_adjust_trip_duration = tool(adjust_trip_duration)
strands_adjust_travel_style = tool(adjust_travel_style)
strands_select_interest_activities = tool(select_interest_activities)
strands_validate_trip_constraints = tool(validate_trip_constraints)

# Registry mapping tool names to decorated tool instances and criteria descriptions for Decider 2B
STRANDS_REGISTERED_TOOLS: Dict[str, Any] = {
    "optimize_budget": {
        "tool": strands_optimize_budget,
        "name": "optimize_budget",
        "description": "Applies deterministic cost reduction tiers (economy rates, style downshift, activity substitution) to reduce costs and clear budget deficits.",
        "criteria": "Reduces costs, applies economy rates, or lowers travel style when user asks to reduce budget, save money, cut expenses, or fix an over-budget deficit.",
    },
    "adjust_trip_duration": {
        "tool": strands_adjust_trip_duration,
        "name": "adjust_trip_duration",
        "description": "Shortens or extends the trip duration within 1-30 days while preserving highlights and avoiding duplicate daily schedules.",
        "criteria": "Shortens or extends the trip length (1-30 days) when the user asks to add days, remove days, shorten the trip, or make it longer.",
    },
    "adjust_travel_style": {
        "tool": strands_adjust_travel_style,
        "name": "adjust_travel_style",
        "description": "Recalibrates accommodation class, dining tier, and transit modes across Budget, Balanced, and Comfort styles.",
        "criteria": "Switches travel style between Budget, Balanced, and Comfort when the user requests a different comfort tier, luxury level, or travel style.",
    },
    "select_interest_activities": {
        "tool": strands_select_interest_activities,
        "name": "select_interest_activities",
        "description": "Selects and ranks daily itinerary activities matching specific user interests such as Heritage, Nature, Food, Adventure, or Relaxation.",
        "criteria": "Ranks, prioritizes, and swaps activities to match specific user interests like Heritage, Nature, Food, Adventure, Beaches, or Relaxation.",
    },
    "validate_trip_constraints": {
        "tool": strands_validate_trip_constraints,
        "name": "validate_trip_constraints",
        "description": "Validates destination feasibility, duration boundaries (1-30 days), and minimum feasible budget thresholds.",
        "criteria": "Checks whether the destination, duration, budget, and travel style are feasible, realistic, and free of constraint conflicts.",
    },
}

# The termination option presented to Decider 2B when all requested planning goals are satisfied
DECIDER_FINISH_OPTION = "finish_planning"
DECIDER_FINISH_CRITERIA = "No further tools need to be called; the current itinerary and budget satisfy all user requirements and constraints."
