"""Tool 2: Trip Duration Adjuster for TripPilot Phase 3.

Safely extends or shortens an itinerary within 1 to 30 days without duplicating
daily schedules or silently truncating information, recalculating all budget
lines and daily breakdowns consistently.
"""
from typing import Union, List

from app.models import TripPlanResponse
from app.services.trip_planner import calculate_trip_plan
from app.tools.schemas import DurationAdjusterOutput


def adjust_trip_duration(
    itinerary: Union[TripPlanResponse, dict],
    target_days: int
) -> DurationAdjusterOutput:
    """
    Adjusts the trip duration to target_days (between 1 and 30 days).
    When extending, generates distinct, non-duplicated thematic daily schedules
    using destination context and regional template blueprints.
    Recalculates stay, food, transit, activities, daily cost breakdowns, and budget surplus/deficit.
    """
    if isinstance(itinerary, dict):
        plan = TripPlanResponse.model_validate(itinerary)
    else:
        plan = itinerary

    if not isinstance(target_days, int):
        try:
            target_days = int(target_days)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid duration '{target_days}'. Must be an integer between 1 and 30.")

    if target_days < 1 or target_days > 30:
        raise ValueError(
            f"Trip duration '{target_days}' is out of bounds. TripPilot supports durations between 1 and 30 days."
        )

    original_days = plan.num_days
    days_delta = target_days - original_days
    changes_made: List[str] = []

    if days_delta == 0:
        action_taken = "unchanged"
        changes_made.append("Duration remains unchanged at the requested day count.")
        explanation = f"Itinerary duration is already {target_days} day(s); no modification needed."
        return DurationAdjusterOutput(
            original_days=original_days,
            target_days=target_days,
            days_delta=0,
            action_taken=action_taken,
            changes_made=changes_made,
            revised_itinerary=plan,
            explanation=explanation
        )

    dest_id = plan.destination.id
    is_custom = not plan.is_verified
    custom_name = plan.destination.name if is_custom else None
    starting_city = plan.starting_city or "Bengaluru"

    # Regenerate plan with target duration preserving destination, budget, style, and optimization status
    revised_plan = calculate_trip_plan(
        starting_city=starting_city,
        destination_id=dest_id,
        days=target_days,
        budget=plan.user_budget,
        interests=plan.destination.primary_interests,
        travel_style=plan.travel_style,
        budget_optimized=plan.budget_optimized,
        custom_destination_name=custom_name,
        is_custom_destination=is_custom
    )

    if days_delta > 0:
        action_taken = "extended"
        changes_made.append(
            f"Extended trip by {days_delta} day(s), generating distinct non-duplicated daily themes for Day {original_days + 1} to Day {target_days}."
        )
        changes_made.append(
            f"Recalculated stay (+₹{revised_plan.accommodation_cost - plan.accommodation_cost:,}), "
            f"food (+₹{revised_plan.food_cost - plan.food_cost:,}), "
            f"transit (+₹{revised_plan.transport_cost - plan.transport_cost:,}), "
            f"and activity costs (+₹{revised_plan.activities_cost - plan.activities_cost:,})."
        )
        explanation = (
            f"Extended trip from {original_days} to {target_days} days (+{days_delta} days). "
            f"Generated {days_delta} new unique day blueprint(s) without duplicating schedules. "
            f"Total cost adjusted from ₹{plan.total_estimated_cost:,} to ₹{revised_plan.total_estimated_cost:,}."
        )
    else:
        action_taken = "shortened"
        trimmed = abs(days_delta)
        changes_made.append(
            f"Shortened trip by {trimmed} day(s), retaining the top {target_days} core days and essential highlights."
        )
        changes_made.append(
            f"Reduced accommodation expenses by ₹{plan.accommodation_cost - revised_plan.accommodation_cost:,}, "
            f"food by ₹{plan.food_cost - revised_plan.food_cost:,}, and transit by ₹{plan.transport_cost - revised_plan.transport_cost:,}."
        )
        explanation = (
            f"Shortened trip from {original_days} to {target_days} days (-{trimmed} days). "
            f"Retained core highlight days. Total cost decreased from ₹{plan.total_estimated_cost:,} to ₹{revised_plan.total_estimated_cost:,}."
        )

    return DurationAdjusterOutput(
        original_days=original_days,
        target_days=target_days,
        days_delta=days_delta,
        action_taken=action_taken,
        changes_made=changes_made,
        revised_itinerary=revised_plan,
        explanation=explanation
    )
