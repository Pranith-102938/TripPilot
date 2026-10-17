"""Tool 3: Travel-Style Adjuster for TripPilot Phase 3.

Recalibrates accommodation class, daily dining benchmarks, and local transit
rates across Budget, Balanced, and Comfort styles while strictly preserving
the destination, duration, and user interests.
"""
from typing import Union, List

from app.models import TripPlanResponse, TravelStyleEnum
from app.services.trip_planner import calculate_trip_plan
from app.tools.schemas import TravelStyleAdjusterOutput


def adjust_travel_style(
    itinerary: Union[TripPlanResponse, dict],
    target_style: Union[str, TravelStyleEnum]
) -> TravelStyleAdjusterOutput:
    """
    Recalibrates an itinerary's travel style to Budget, Balanced, or Comfort.
    Updates daily stay, food, and transit tariffs to destination benchmarks.
    Recalculates daily cost breakdowns and total budget surplus/deficit.
    """
    if isinstance(itinerary, dict):
        plan = TripPlanResponse.model_validate(itinerary)
    else:
        plan = itinerary

    raw_style = target_style.value if isinstance(target_style, TravelStyleEnum) else str(target_style).strip().lower()
    if raw_style not in ["budget", "balanced", "comfort"]:
        raise ValueError(
            f"Invalid travel style '{target_style}'. TripPilot supports: 'budget', 'balanced', 'comfort'."
        )

    original_style = plan.travel_style.lower()
    changes_made: List[str] = []

    if original_style == raw_style:
        changes_made.append(f"Itinerary is already calibrated to {raw_style.title()} travel style.")
        return TravelStyleAdjusterOutput(
            original_style=original_style,
            target_style=raw_style,
            cost_delta=0,
            changes_made=changes_made,
            revised_itinerary=plan,
            explanation=f"Travel style is already {raw_style.title()}; no changes required."
        )

    dest_id = plan.destination.id
    is_custom = not plan.is_verified
    custom_name = plan.destination.name if is_custom else None
    starting_city = plan.starting_city or "Bengaluru"

    revised_plan = calculate_trip_plan(
        starting_city=starting_city,
        destination_id=dest_id,
        days=plan.num_days,
        budget=plan.user_budget,
        interests=plan.destination.primary_interests,
        travel_style=raw_style,
        budget_optimized=plan.budget_optimized,
        custom_destination_name=custom_name,
        is_custom_destination=is_custom
    )

    cost_delta = revised_plan.total_estimated_cost - plan.total_estimated_cost
    stay_delta = revised_plan.accommodation_cost - plan.accommodation_cost
    food_delta = revised_plan.food_cost - plan.food_cost
    transit_delta = revised_plan.transport_cost - plan.transport_cost

    delta_sign = "+" if cost_delta > 0 else ""
    changes_made.append(f"Updated accommodation tariff to {raw_style.title()} benchmark ({delta_sign}₹{stay_delta:,}).")
    changes_made.append(f"Updated food & dining benchmark ({delta_sign}₹{food_delta:,}).")
    changes_made.append(f"Updated local transit benchmark ({delta_sign}₹{transit_delta:,}).")

    if cost_delta > 0:
        explanation = (
            f"Upgraded travel style from {original_style.title()} to {raw_style.title()}. "
            f"Total estimated cost increased by ₹{cost_delta:,} (from ₹{plan.total_estimated_cost:,} to ₹{revised_plan.total_estimated_cost:,})."
        )
    else:
        explanation = (
            f"Downgraded travel style from {original_style.title()} to {raw_style.title()}. "
            f"Total estimated cost decreased by ₹{abs(cost_delta):,} (from ₹{plan.total_estimated_cost:,} to ₹{revised_plan.total_estimated_cost:,})."
        )

    return TravelStyleAdjusterOutput(
        original_style=original_style,
        target_style=raw_style,
        cost_delta=cost_delta,
        changes_made=changes_made,
        revised_itinerary=revised_plan,
        explanation=explanation
    )
