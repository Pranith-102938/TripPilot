"""Tool 5: Constraint Validator for TripPilot Phase 3.

Validates destination support, duration boundaries (1–30 days), budget feasibility,
and detects requirement conflicts without silently modifying user inputs.
"""
from typing import List, Optional, Dict, Any

from app.models import TravelStyleEnum
from app.services.trip_planner import get_destination_by_id, DESTINATIONS
from app.tools.schemas import ConstraintValidatorInput, ConstraintValidatorOutput

DESTINATION_ENVIRONMENT_MAP = {
    "munnar": {"environment": "hills", "unsupported_interests": ["beaches", "scuba"]},
    "manali": {"environment": "mountains", "unsupported_interests": ["beaches", "scuba"]},
    "shimla": {"environment": "mountains", "unsupported_interests": ["beaches", "scuba"]},
    "ladakh": {"environment": "high_altitude_desert", "unsupported_interests": ["beaches", "surfing"]},
    "ooty": {"environment": "hills", "unsupported_interests": ["beaches", "scuba"]},
    "coorg": {"environment": "hills", "unsupported_interests": ["beaches", "scuba"]},
    "goa": {"environment": "coastal", "unsupported_interests": ["snow", "mountaineering"]},
    "andaman": {"environment": "island_coastal", "unsupported_interests": ["snow", "high_altitude_trekking"]},
    "puri": {"environment": "coastal", "unsupported_interests": ["snow", "high_altitude_trekking"]},
}


def validate_trip_constraints(
    destination: str,
    days: int,
    budget: float,
    travel_style: Optional[str] = "balanced",
    interests: Optional[List[str]] = None,
    starting_city: Optional[str] = None,
    is_custom_destination: bool = False
) -> ConstraintValidatorOutput:
    """
    Validates all trip planning parameters against hard and soft constraints:
    - Duration boundaries: 1 to 30 days.
    - System minimum budget: ₹5,000.
    - Destination-specific minimum feasible budget.
    - Style-to-budget mismatch conflicts.
    - Geographic environment vs interest conflicts.
    - Identifies all conflicts without silently modifying the inputs.
    """
    errors: List[str] = []
    warnings: List[str] = []
    conflicts_detected: List[str] = []
    recommendations: List[str] = []

    clean_dest = destination.strip() if destination else ""
    raw_style = (travel_style or "balanced").strip().lower()
    clean_interests = [i.strip().lower() for i in (interests or []) if i.strip()]

    # 1. Destination validation
    dest_dict = get_destination_by_id(clean_dest) if clean_dest else None
    if not clean_dest:
        errors.append("Destination cannot be empty.")
        dest_name = "Unknown"
    elif dest_dict:
        dest_name = dest_dict["name"]
    else:
        dest_name = clean_dest.title()
        if not is_custom_destination:
            warnings.append(
                f"Destination '{clean_dest}' is not part of the verified curated database. "
                f"Treated as an unverified custom destination using national baseline benchmarks."
            )

    # 2. Duration validation (1 to 30 days)
    if not isinstance(days, int):
        try:
            days = int(days)
        except (ValueError, TypeError):
            errors.append(f"Duration '{days}' is invalid; must be an integer between 1 and 30 days.")
            days = 0

    if days < 1:
        errors.append(f"Duration of {days} day(s) is below the minimum allowed duration of 1 day.")
        recommendations.append("Set trip duration to at least 1 day.")
    elif days > 30:
        errors.append(f"Duration of {days} days exceeds the maximum supported duration of 30 days.")
        recommendations.append("Adjust trip duration to 30 days or fewer.")

    # 3. Minimum baseline cost calculation
    if dest_dict:
        indicative = dest_dict.get("indicativeDailyCost", {"budget": 2000, "balanced": 4200, "comfort": 8000})
        budget_daily_rate = indicative.get("budget", 2000)
        balanced_daily_rate = indicative.get("balanced", 4200)
        comfort_daily_rate = indicative.get("comfort", 8000)
    else:
        budget_daily_rate = 2000
        balanced_daily_rate = 4200
        comfort_daily_rate = 8000

    effective_days = max(1, min(days, 30)) if days > 0 else 1
    min_feasible_budget = budget_daily_rate * effective_days
    max_feasible_budget = comfort_daily_rate * effective_days

    # 4. Budget validation
    if budget < 5000:
        errors.append(f"Budget of ₹{budget:,.0f} is below the application minimum threshold of ₹5,000.")
        recommendations.append("Increase your budget to at least ₹5,000 to enable meaningful accommodation and transit.")

    if days >= 1 and budget < min_feasible_budget:
        conflicts_detected.append(
            f"Budget Deficit Conflict: User budget of ₹{budget:,.0f} is insufficient for a {days}-day trip to {dest_name}. "
            f"The minimum feasible cost under economy budget style is estimated at ₹{min_feasible_budget:,} (₹{budget_daily_rate:,}/day)."
        )
        max_days_for_budget = max(1, int(budget // budget_daily_rate))
        recommendations.append(
            f"Increase total budget to at least ₹{min_feasible_budget:,} or shorten trip duration to {max_days_for_budget} day(s)."
        )

    # 5. Travel Style vs Budget Conflict
    if raw_style not in ["budget", "balanced", "comfort"]:
        errors.append(f"Invalid travel style '{travel_style}'. Supported styles are: 'budget', 'balanced', 'comfort'.")
    else:
        style_rates = {
            "budget": budget_daily_rate,
            "balanced": balanced_daily_rate,
            "comfort": comfort_daily_rate
        }
        requested_style_min = style_rates[raw_style] * effective_days
        if budget >= min_feasible_budget and budget < requested_style_min:
            conflicts_detected.append(
                f"Travel Style Conflict: '{raw_style.title()}' style in {dest_name} requires approximately ₹{requested_style_min:,} "
                f"for {days} days, exceeding the proposed budget of ₹{budget:,.0f}."
            )
            recommendations.append(
                f"Consider selecting 'budget' travel style (feasible from ₹{min_feasible_budget:,}) or increasing budget to ₹{requested_style_min:,}."
            )

    # 6. Interest vs Geography Conflict
    if dest_dict:
        env_info = DESTINATION_ENVIRONMENT_MAP.get(dest_dict["id"].lower())
        if env_info:
            unsupported = env_info.get("unsupported_interests", [])
            for user_interest in clean_interests:
                if user_interest in unsupported:
                    warnings.append(
                        f"Geographic Alignment Note: '{dest_name}' is located in a {env_info['environment']} environment "
                        f"and may not offer traditional '{user_interest}' activities."
                    )
                    recommendations.append(
                        f"Consider focusing on {', '.join(dest_dict.get('primaryInterests', ['nature', 'culture']))} for {dest_name}."
                    )

    # A plan is valid only if there are zero blocking errors and no budget-to-minimum-cost conflict
    is_valid = len(errors) == 0 and not any("Budget Deficit Conflict" in c for c in conflicts_detected)

    return ConstraintValidatorOutput(
        isValid=is_valid,
        errors=errors,
        warnings=warnings,
        feasibleBudgetMin=min_feasible_budget,
        feasibleBudgetMax=max_feasible_budget,
        conflictsDetected=conflicts_detected,
        recommendations=recommendations
    )
