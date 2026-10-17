"""Comprehensive unit tests for Phase 3 modular travel planning tools."""
import pytest
from app.models import TripPlanRequest, TravelStyleEnum
from app.services.trip_planner import calculate_trip_plan, create_trip_plan
from app.tools import (
    optimize_budget,
    adjust_trip_duration,
    adjust_travel_style,
    select_interest_activities,
    validate_trip_constraints,
    PLANNING_TOOLS_REGISTRY,
)


@pytest.fixture
def sample_hyderabad_plan():
    """Returns a standard 4-day balanced plan for Hyderabad."""
    return calculate_trip_plan(
        starting_city="Bengaluru",
        destination_id="hyderabad",
        days=4,
        budget=35000,
        interests=["culture", "food"],
        travel_style="balanced",
        budget_optimized=False
    )


@pytest.fixture
def sample_goa_plan():
    """Returns a standard 3-day comfort plan for Goa."""
    return calculate_trip_plan(
        starting_city="Mumbai",
        destination_id="goa",
        days=3,
        budget=40000,
        interests=["beaches", "food"],
        travel_style="comfort",
        budget_optimized=False
    )


@pytest.fixture
def sample_custom_plan():
    """Returns an unverified custom destination plan."""
    return calculate_trip_plan(
        starting_city="Pune",
        destination_id="custom",
        days=3,
        budget=20000,
        interests=["nature"],
        travel_style="balanced",
        budget_optimized=False,
        custom_destination_name="Chikmagalur",
        is_custom_destination=True
    )


# =====================================================================
# Test Tool 1: Budget Optimizer
# =====================================================================

def test_budget_optimizer_feasible_reduction(sample_hyderabad_plan):
    """Tests budget optimization when target budget is feasible via economy tiers."""
    initial_cost = sample_hyderabad_plan.total_estimated_cost
    target_budget = initial_cost - 4000  # Feasible deficit

    output = optimize_budget(sample_hyderabad_plan, target_budget=target_budget)

    assert output.target_budget == target_budget
    assert output.initial_cost == initial_cost
    assert output.final_cost <= target_budget
    assert output.final_deficit == 0.0
    assert output.fits_budget is True
    assert output.remaining_budget >= 0
    assert len(output.changes_made) > 0
    assert "clearing the initial deficit" in output.explanation.lower()

    # Mathematical consistency of revised itinerary
    rev = output.revised_itinerary
    assert sum(d.day_total for d in rev.active_days) == rev.total_estimated_cost
    assert sum(d.day_stay for d in rev.active_days) == rev.accommodation_cost
    assert sum(d.day_food for d in rev.active_days) == rev.food_cost
    assert sum(d.day_transit for d in rev.active_days) == rev.transport_cost
    assert sum(d.day_activities for d in rev.active_days) == rev.activities_cost


def test_budget_optimizer_below_minimum_feasible_cost(sample_goa_plan):
    """Tests that optimizer NEVER claims a plan fits the budget if it still exceeds it."""
    # ₹3,000 for 3 days in Goa is below the absolute minimum feasible stay+food rate
    unrealistic_budget = 3000.0

    output = optimize_budget(sample_goa_plan, target_budget=unrealistic_budget)

    assert output.fits_budget is False
    assert output.final_deficit > 0
    assert output.final_cost > unrealistic_budget
    assert "below the minimum feasible cost" in output.explanation.lower()
    assert "deficit of" in output.explanation.lower()
    assert output.remaining_budget < 0


def test_budget_optimizer_already_within_budget(sample_hyderabad_plan):
    """Tests that optimizer takes no intrusive action if already within budget."""
    ample_budget = 60000.0
    output = optimize_budget(sample_hyderabad_plan, target_budget=ample_budget)

    assert output.fits_budget is True
    assert output.final_deficit == 0.0
    assert output.final_cost == sample_hyderabad_plan.total_estimated_cost
    assert "already within the specified budget" in output.changes_made[0]


# =====================================================================
# Test Tool 2: Trip Duration Adjuster
# =====================================================================

def test_duration_adjuster_boundaries(sample_hyderabad_plan):
    """Tests 1-day minimum and 30-day maximum duration boundaries."""
    # 1-day boundary
    out_1 = adjust_trip_duration(sample_hyderabad_plan, target_days=1)
    assert out_1.target_days == 1
    assert out_1.action_taken == "shortened"
    assert len(out_1.revised_itinerary.active_days) == 1
    assert out_1.revised_itinerary.num_days == 1

    # 30-day boundary
    out_30 = adjust_trip_duration(sample_hyderabad_plan, target_days=30)
    assert out_30.target_days == 30
    assert out_30.action_taken == "extended"
    assert len(out_30.revised_itinerary.active_days) == 30
    assert out_30.revised_itinerary.num_days == 30

    # Invalid boundaries (<1 or >30)
    with pytest.raises(ValueError, match="out of bounds"):
        adjust_trip_duration(sample_hyderabad_plan, target_days=0)

    with pytest.raises(ValueError, match="out of bounds"):
        adjust_trip_duration(sample_hyderabad_plan, target_days=-5)

    with pytest.raises(ValueError, match="out of bounds"):
        adjust_trip_duration(sample_hyderabad_plan, target_days=31)


def test_duration_adjuster_extension_non_duplication(sample_hyderabad_plan):
    """Tests that extending to 7, 14, and 30 days generates non-duplicate thematic daily schedules."""
    for days in [7, 14, 25]:
        out = adjust_trip_duration(sample_hyderabad_plan, target_days=days)
        rev = out.revised_itinerary
        assert len(rev.active_days) == days

        # Verify all daily themes are unique
        themes = [d.theme for d in rev.active_days]
        assert len(set(themes)) == days, f"Duplicate themes found in {days}-day extended itinerary"

        # Cost recalculation integrity
        assert sum(d.day_total for d in rev.active_days) == rev.total_estimated_cost
        assert rev.accommodation_cost == rev.daily_stay * days
        assert rev.food_cost == rev.daily_food * days
        assert rev.transport_cost == rev.daily_transit * days


def test_duration_adjuster_shortening(sample_hyderabad_plan):
    """Tests shortening trip from 4 days to 2 days."""
    out = adjust_trip_duration(sample_hyderabad_plan, target_days=2)
    assert out.target_days == 2
    assert out.action_taken == "shortened"
    assert out.days_delta == -2
    assert len(out.revised_itinerary.active_days) == 2
    assert out.revised_itinerary.total_estimated_cost < sample_hyderabad_plan.total_estimated_cost


# =====================================================================
# Test Tool 3: Travel-Style Adjuster
# =====================================================================

def test_travel_style_adjuster_cost_consistency(sample_hyderabad_plan):
    """Tests switching between budget, balanced, and comfort styles."""
    out_budget = adjust_travel_style(sample_hyderabad_plan, target_style="budget")
    out_comfort = adjust_travel_style(sample_hyderabad_plan, target_style="comfort")

    # Budget < Balanced < Comfort cost ordering
    cost_budget = out_budget.revised_itinerary.total_estimated_cost
    cost_balanced = sample_hyderabad_plan.total_estimated_cost
    cost_comfort = out_comfort.revised_itinerary.total_estimated_cost

    assert cost_budget < cost_balanced < cost_comfort
    assert out_budget.cost_delta < 0
    assert out_comfort.cost_delta > 0

    # Destination and duration preserved
    assert out_budget.revised_itinerary.destination.id == sample_hyderabad_plan.destination.id
    assert out_budget.revised_itinerary.num_days == sample_hyderabad_plan.num_days

    # Mathematical consistency
    rev_b = out_budget.revised_itinerary
    assert sum(d.day_total for d in rev_b.active_days) == rev_b.total_estimated_cost


def test_travel_style_adjuster_invalid_style(sample_hyderabad_plan):
    """Tests validation error on invalid travel style."""
    with pytest.raises(ValueError, match="Invalid travel style"):
        adjust_travel_style(sample_hyderabad_plan, target_style="ultra_luxury")


# =====================================================================
# Test Tool 4: Interest-Based Activity Selector
# =====================================================================

def test_activity_selector_curated_destination():
    """Tests activity selection with user interests on a curated destination."""
    out = select_interest_activities(
        destination="hyderabad",
        interests=["food", "culture"],
        days=3
    )

    assert out.is_curated is True
    assert out.destination_id == "hyderabad"
    assert "food" in out.matched_interests or "culture" in out.matched_interests
    assert len(out.selected_activities) == 9  # 3 days * 3 slots

    for item in out.selected_activities:
        assert item.is_curated is True
        assert len(item.selection_rationale) > 0
        assert "curated" in item.selection_rationale.lower()
        assert item.activity.title is not None
        assert item.activity.duration is not None


def test_activity_selector_unverified_destination():
    """Tests activity selection on an unverified destination distinguishes generic templates."""
    out = select_interest_activities(
        destination="Tawang",
        interests=["nature", "adventure"],
        days=2,
        is_custom_destination=True
    )

    assert out.is_curated is False
    assert "Tawang" in out.destination_name
    assert "generic template" in out.rationale_summary.lower()
    assert "not fabricated" in out.rationale_summary.lower()

    for item in out.selected_activities:
        assert item.is_curated is False
        assert "generic template baseline" in item.selection_rationale.lower()
        assert item.activity.cost == 0


# =====================================================================
# Test Tool 5: Constraint Validator
# =====================================================================

def test_constraint_validator_valid_inputs():
    """Tests clean valid trip parameters pass validation."""
    out = validate_trip_constraints(
        destination="jaipur",
        days=3,
        budget=25000,
        travel_style="balanced",
        interests=["culture"]
    )

    assert out.is_valid is True
    assert len(out.errors) == 0
    assert len(out.conflicts_detected) == 0
    assert out.feasible_budget_min > 0
    assert out.feasible_budget_max >= out.feasible_budget_min


def test_constraint_validator_duration_out_of_bounds():
    """Tests duration < 1 and > 30 errors without modifying inputs."""
    out_zero = validate_trip_constraints(destination="goa", days=0, budget=20000)
    assert out_zero.is_valid is False
    assert any("below the minimum" in err for err in out_zero.errors)

    out_excess = validate_trip_constraints(destination="goa", days=35, budget=80000)
    assert out_excess.is_valid is False
    assert any("exceeds the maximum" in err for err in out_excess.errors)


def test_constraint_validator_budget_below_feasible():
    """Tests budget below minimum feasible cost reports actionable conflict."""
    out = validate_trip_constraints(
        destination="goa",
        days=5,
        budget=4000,  # Below app minimum of ₹5,000 and below feasible Goa 5-day rate
        travel_style="balanced"
    )

    assert out.is_valid is False
    assert any("below the application minimum" in err for err in out.errors)
    assert any("Budget Deficit Conflict" in c for c in out.conflicts_detected)
    assert any("Increase total budget" in r for r in out.recommendations)


def test_constraint_validator_travel_style_mismatch():
    """Tests conflict detection when budget cannot support luxury comfort style."""
    out = validate_trip_constraints(
        destination="munnar",
        days=4,
        budget=12000,  # Feasible for budget, but inadequate for comfort (~₹32,000)
        travel_style="comfort"
    )

    assert any("Travel Style Conflict" in c for c in out.conflicts_detected)
    assert any("Consider selecting 'budget'" in r for r in out.recommendations)


def test_constraint_validator_geographic_conflict():
    """Tests warning when requesting beach activities in a mountain destination."""
    out = validate_trip_constraints(
        destination="munnar",
        days=3,
        budget=20000,
        travel_style="balanced",
        interests=["beaches"]
    )

    assert any("Geographic Alignment Note" in w for w in out.warnings)
    assert any("hills" in w for w in out.warnings)


# =====================================================================
# Chained Tool Operations & Registry Tests
# =====================================================================

def test_chained_tool_pipeline(sample_goa_plan):
    """
    Tests chaining tools in sequence:
    1. Adjust duration (3 -> 5 days)
    2. Adjust travel style (Comfort -> Balanced)
    3. Optimize budget for target threshold
    Verifies data flow and mathematical integrity at every step.
    """
    # Step 1: Extend to 5 days
    step1_out = adjust_trip_duration(sample_goa_plan, target_days=5)
    assert step1_out.revised_itinerary.num_days == 5
    assert sum(d.day_total for d in step1_out.revised_itinerary.active_days) == step1_out.revised_itinerary.total_estimated_cost

    # Step 2: Switch travel style to balanced
    step2_out = adjust_travel_style(step1_out.revised_itinerary, target_style="balanced")
    assert step2_out.revised_itinerary.travel_style == "balanced"
    assert step2_out.cost_delta < 0  # Balanced is cheaper than comfort
    assert sum(d.day_total for d in step2_out.revised_itinerary.active_days) == step2_out.revised_itinerary.total_estimated_cost

    # Step 3: Optimize for a tight budget of ₹18,000
    step3_out = optimize_budget(step2_out.revised_itinerary, target_budget=18000)
    rev_final = step3_out.revised_itinerary
    assert rev_final.num_days == 5
    assert sum(d.day_total for d in rev_final.active_days) == rev_final.total_estimated_cost


def test_tools_registry_structure():
    """Verifies that all 5 tools are registered in PLANNING_TOOLS_REGISTRY for Strands."""
    expected_tools = [
        "optimize_budget",
        "adjust_trip_duration",
        "adjust_travel_style",
        "select_interest_activities",
        "validate_trip_constraints",
    ]
    for tool_name in expected_tools:
        assert tool_name in PLANNING_TOOLS_REGISTRY
        tool_meta = PLANNING_TOOLS_REGISTRY[tool_name]
        assert callable(tool_meta["callable"])
        assert tool_meta["input_schema"] is not None
        assert tool_meta["output_schema"] is not None
        assert len(tool_meta["description"]) > 0
