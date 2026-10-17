"""Tool 1: Budget Optimizer for TripPilot Phase 3.

Applies explicit, deterministic cost reduction rules across stay, food, transit,
and activities. Recalculates daily and trip-wide costs consistently, and never
claims a plan fits the budget if it still exceeds it.
"""
from copy import deepcopy
from typing import Optional, List, Union

from app.models import TripPlanResponse, TravelStyleEnum
from app.services.trip_planner import calculate_trip_plan
from app.tools.schemas import BudgetOptimizerInput, BudgetOptimizerOutput


def optimize_budget(
    itinerary: Union[TripPlanResponse, dict],
    target_budget: Optional[float] = None
) -> BudgetOptimizerOutput:
    """
    Optimizes an itinerary's costs to meet a target budget using explicit deterministic tiers:
    Tier 1: Economy tariffs (stay -25%, transit -25%, food -20%, activities -15%).
    Tier 2: Travel style downshift (Comfort -> Balanced -> Budget) if deficit persists.
    Tier 3: Discretionary activity fee substitution with free self-guided alternatives.

    Guarantees strict mathematical integrity and honesty: never marks fits_budget=True
    if a deficit remains.
    """
    if isinstance(itinerary, dict):
        plan = TripPlanResponse.model_validate(itinerary)
    else:
        plan = itinerary

    eff_target_budget = float(target_budget) if target_budget is not None else float(plan.user_budget)
    initial_cost = plan.total_estimated_cost
    initial_deficit = max(0.0, float(initial_cost - eff_target_budget))
    changes_made: List[str] = []

    # If already within budget and not currently in deficit, verify if any action is needed
    if initial_deficit == 0.0 and plan.remaining_budget >= 0:
        return BudgetOptimizerOutput(
            original_budget=plan.user_budget,
            target_budget=eff_target_budget,
            initial_cost=initial_cost,
            final_cost=plan.total_estimated_cost,
            initial_deficit=0.0,
            final_deficit=0.0,
            remaining_budget=float(eff_target_budget - plan.total_estimated_cost),
            fits_budget=True,
            changes_made=["Itinerary is already within the specified budget threshold; no reductions required."],
            revised_itinerary=plan,
            explanation=f"Trip cost of ₹{plan.total_estimated_cost:,} is fully within the target budget of ₹{eff_target_budget:,.0f}."
        )

    current_style = plan.travel_style.lower()
    dest_id = plan.destination.id
    is_custom = not plan.is_verified
    custom_name = plan.destination.name if is_custom else None
    days = plan.num_days
    starting_city = plan.starting_city or "Bengaluru"

    # Step 1: Apply Tier 1 (Economy optimization)
    candidate_plan = calculate_trip_plan(
        starting_city=starting_city,
        destination_id=dest_id,
        days=days,
        budget=eff_target_budget,
        interests=plan.destination.primary_interests,
        travel_style=current_style,
        budget_optimized=True,
        custom_destination_name=custom_name,
        is_custom_destination=is_custom
    )
    changes_made.append("Applied Tier 1 economy tariffs: accommodation reduced by 25%, transit by 25%, food by 20%, and activities by 15%.")

    # Step 2: If deficit remains, apply Tier 2 (Style downgrade: comfort -> balanced -> budget)
    if candidate_plan.total_estimated_cost > eff_target_budget:
        downgrade_map = {"comfort": "balanced", "balanced": "budget"}
        target_style = downgrade_map.get(current_style)
        if target_style:
            candidate_plan = calculate_trip_plan(
                starting_city=starting_city,
                destination_id=dest_id,
                days=days,
                budget=eff_target_budget,
                interests=plan.destination.primary_interests,
                travel_style=target_style,
                budget_optimized=True,
                custom_destination_name=custom_name,
                is_custom_destination=is_custom
            )
            changes_made.append(f"Applied Tier 2 travel style recalibration: shifted from {current_style.title()} to {target_style.title()} class.")
            current_style = target_style

    # Step 3: If deficit still remains, check if shifting to budget style helps
    if candidate_plan.total_estimated_cost > eff_target_budget and current_style == "balanced":
        candidate_plan = calculate_trip_plan(
            starting_city=starting_city,
            destination_id=dest_id,
            days=days,
            budget=eff_target_budget,
            interests=plan.destination.primary_interests,
            travel_style="budget",
            budget_optimized=True,
            custom_destination_name=custom_name,
            is_custom_destination=is_custom
        )
        changes_made.append("Applied Tier 2 minimum baseline: shifted travel style to Budget class.")
        current_style = "budget"

    # Step 4: If deficit still remains, apply Tier 3 (Substitute paid discretionary activities with free alternatives)
    if candidate_plan.total_estimated_cost > eff_target_budget and candidate_plan.activities_cost > 0:
        active_days_copy = deepcopy(candidate_plan.active_days)
        substituted_count = 0
        for day in active_days_copy:
            for slot_key in ["morning", "afternoon", "evening"]:
                slot = getattr(day, slot_key)
                if slot.cost > 0:
                    slot.cost = 0
                    slot.is_cost_estimated = True
                    slot.title = f"Self-Guided {slot.title}"
                    slot.explanation += " (Substituted with free self-guided exploration to reduce budget deficit)."
                    substituted_count += 1
                if sum(getattr(d, s).cost for d in active_days_copy for s in ["morning", "afternoon", "evening"]) + (candidate_plan.accommodation_cost + candidate_plan.food_cost + candidate_plan.transport_cost) <= eff_target_budget:
                    break
        
        # Recalculate activities and daily breakdown
        revised_act_cost = sum(getattr(d, s).cost for d in active_days_copy for s in ["morning", "afternoon", "evening"])
        for day in active_days_copy:
            day_act = sum(getattr(day, s).cost for s in ["morning", "afternoon", "evening"])
            day.day_activities = day_act
            day.day_total = day.day_stay + day.day_food + day.day_transit + day_act

        revised_total = candidate_plan.accommodation_cost + candidate_plan.food_cost + candidate_plan.transport_cost + revised_act_cost
        revised_rem = eff_target_budget - revised_total
        candidate_plan = candidate_plan.model_copy(update={
            "active_days": active_days_copy,
            "activities_cost": revised_act_cost,
            "total_estimated_cost": revised_total,
            "user_budget": eff_target_budget,
            "remaining_budget": revised_rem,
            "is_over_budget": revised_rem < 0,
            "deficit": abs(revised_rem) if revised_rem < 0 else 0.0
        })
        changes_made.append(f"Applied Tier 3 activity substitutions: converted {substituted_count} admission activities to free self-guided explorations.")

    final_cost = candidate_plan.total_estimated_cost
    final_deficit = max(0.0, float(final_cost - eff_target_budget))
    fits_budget = final_deficit == 0.0
    remaining_budget = float(eff_target_budget - final_cost)

    if fits_budget:
        explanation = (
            f"Successfully optimized itinerary cost from ₹{initial_cost:,} down to ₹{final_cost:,}, "
            f"clearing the initial deficit of ₹{initial_deficit:,.0f} and leaving a ₹{remaining_budget:,.0f} surplus."
        )
    else:
        explanation = (
            f"Target budget of ₹{eff_target_budget:,.0f} is below the minimum feasible cost of ₹{final_cost:,} "
            f"for a {days}-day trip to {candidate_plan.destination.name} under economy rates. "
            f"An unavoidable deficit of ₹{final_deficit:,.0f} remains. Consider shortening the duration."
        )

    return BudgetOptimizerOutput(
        original_budget=plan.user_budget,
        target_budget=eff_target_budget,
        initial_cost=initial_cost,
        final_cost=final_cost,
        initial_deficit=initial_deficit,
        final_deficit=final_deficit,
        remaining_budget=remaining_budget,
        fits_budget=fits_budget,
        changes_made=changes_made,
        revised_itinerary=candidate_plan,
        explanation=explanation
    )
