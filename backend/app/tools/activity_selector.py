"""Tool 4: Interest-Based Activity Selector for TripPilot Phase 3.

Prioritizes suitable activities from verified destination datasets based on user
interests, provides clear selection rationales, and distinguishes curated destination
facts from generic baseline templates.
"""
from typing import List, Optional, Union

from app.models import TravelStyleEnum
from app.services.trip_planner import (
    calculate_trip_plan,
    get_destination_by_id,
    DESTINATIONS,
    SAMPLE_ITINERARIES
)
from app.tools.schemas import (
    ActivitySelectorInput,
    ActivitySelectorOutput,
    SelectedActivityItem
)

# Common category mapping for flexible interest matching
INTEREST_CATEGORY_MAP = {
    "culture": ["culture", "heritage", "history", "spiritual", "art"],
    "heritage": ["culture", "heritage", "history"],
    "history": ["culture", "heritage", "history"],
    "food": ["food", "culinary", "dining", "tea", "coffee"],
    "culinary": ["food", "culinary", "dining"],
    "nature": ["nature", "wildlife", "botanical", "scenic", "mountains", "hills"],
    "wildlife": ["nature", "wildlife"],
    "adventure": ["adventure", "trekking", "kayaking", "hiking", "safari"],
    "relaxation": ["relaxation", "wellness", "beaches", "leisure", "slow travel"],
    "beaches": ["relaxation", "beaches", "nature"],
    "wellness": ["relaxation", "wellness"]
}


def select_interest_activities(
    destination: str,
    interests: List[str],
    days: int = 3,
    travel_style: Union[str, TravelStyleEnum] = "balanced",
    is_custom_destination: bool = False
) -> ActivitySelectorOutput:
    """
    Selects and prioritizes activities aligned with traveler interests.
    Explains the selection rationale for every slot and explicitly indicates
    whether activities stem from verified curated regional facts or generic templates.
    """
    clean_dest = destination.strip()
    clean_interests = [i.strip().lower() for i in interests if i.strip()]
    if not clean_interests:
        clean_interests = ["culture", "nature"]

    raw_style = travel_style.value if isinstance(travel_style, TravelStyleEnum) else str(travel_style).lower()
    days_clamped = max(1, min(days, 30))

    dest_dict = get_destination_by_id(clean_dest)
    is_curated = dest_dict is not None and not is_custom_destination

    # Generate complete itinerary framework for the requested duration
    plan = calculate_trip_plan(
        starting_city="Bengaluru",
        destination_id=clean_dest if is_curated else "custom",
        days=days_clamped,
        budget=50000,
        interests=clean_interests,
        travel_style=raw_style,
        budget_optimized=False,
        custom_destination_name=clean_dest if not is_curated else None,
        is_custom_destination=not is_curated
    )

    dest_name = plan.destination.name
    selected_items: List[SelectedActivityItem] = []
    matched_interests_set = set()

    for day in plan.active_days:
        for slot_key in ["morning", "afternoon", "evening"]:
            activity = getattr(day, slot_key)
            cat = activity.category.lower()

            # Find matching interest
            matched_interest = None
            for user_interest in clean_interests:
                mapped_categories = INTEREST_CATEGORY_MAP.get(user_interest, [user_interest])
                if cat in mapped_categories or any(term in activity.title.lower() or term in activity.explanation.lower() for term in mapped_categories):
                    matched_interest = user_interest
                    matched_interests_set.add(user_interest)
                    break

            if is_curated:
                if matched_interest:
                    rationale = (
                        f"Curated selection: Activity '{activity.title}' categorised as '{activity.category}' directly "
                        f"fulfils traveler interest in '{matched_interest}' based on verified {dest_name} regional landmarks."
                    )
                else:
                    rationale = (
                        f"Curated balance: Activity '{activity.title}' included as a verified signature experience "
                        f"to provide a well-rounded regional schedule in {dest_name}."
                    )
            else:
                rationale = (
                    f"Generic template baseline: Activity '{activity.title}' provided as self-guided structure. "
                    f"Verified landmark data is unavailable for {dest_name}; attractions and entrance fees are not fabricated."
                )

            selected_items.append(SelectedActivityItem(
                dayNumber=day.day_number,
                slot=slot_key,
                activity=activity,
                matchedInterest=matched_interest,
                isCurated=is_curated,
                selectionRationale=rationale
            ))

    matched_list = sorted(list(matched_interests_set))
    unmatched_list = sorted(list(set(clean_interests) - matched_interests_set))

    if is_curated:
        rationale_summary = (
            f"Selected {len(selected_items)} activities across {days_clamped} day(s) for {dest_name} using verified regional benchmarks. "
            f"Successfully aligned activities with interest(s): {', '.join(matched_list) if matched_list else 'general'}. "
            f"Curated landmarks and genuine pricing have been prioritized."
        )
    else:
        rationale_summary = (
            f"Applied generic template baseline activities across {days_clamped} day(s) for manually entered location '{dest_name}'. "
            f"Activities are structured around self-guided exploration; specific attractions, ticket fees, and travel times are not fabricated."
        )

    return ActivitySelectorOutput(
        destinationId=plan.destination.id,
        destinationName=dest_name,
        isCurated=is_curated,
        matchedInterests=matched_list,
        unmatchedInterests=unmatched_list,
        selectedActivities=selected_items,
        rationaleSummary=rationale_summary
    )
