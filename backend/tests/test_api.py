"""Comprehensive pytest test suite for TripPilot FastAPI backend."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verifies health check response and ensures AI services are not falsely claimed."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "TripPilot Backend"
    assert data["ai_connected"] is False
    assert "Phase 2" in data["phase"]


def test_list_destinations():
    """Tests destination listing endpoint returns full curated collection (20-30 destinations)."""
    response = client.get("/api/destinations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 20
    dest_ids = [d["id"] for d in data]
    # Core destinations
    assert "hyderabad" in dest_ids
    assert "goa" in dest_ids
    assert "jaipur" in dest_ids
    assert "munnar" in dest_ids
    # Expanded diverse destinations across India
    assert "rishikesh" in dest_ids
    assert "varanasi" in dest_ids
    assert "udaipur" in dest_ids
    assert "manali" in dest_ids
    assert "andaman" in dest_ids
    assert "hampi" in dest_ids


def test_destination_search():
    """Tests destination search by name or state query."""
    # Search by state: Kerala
    kerala_res = client.get("/api/destinations?search=Kerala")
    assert kerala_res.status_code == 200
    kerala_dests = [d["name"] for d in kerala_res.json()]
    assert "Munnar" in kerala_dests
    assert "Varkala" in kerala_dests

    # Search by city name: Rishikesh
    rishi_res = client.get("/api/destinations?search=Rishikesh")
    assert rishi_res.status_code == 200
    assert len(rishi_res.json()) == 1
    assert rishi_res.json()[0]["id"] == "rishikesh"


def test_destination_category_filter():
    """Tests destination filtering by category."""
    # Beaches filter
    beaches_res = client.get("/api/destinations?category=beaches")
    assert beaches_res.status_code == 200
    beach_ids = [d["id"] for d in beaches_res.json()]
    assert "goa" in beach_ids
    assert "gokarna" in beach_ids
    assert "varkala" in beach_ids

    # Hill stations filter
    hills_res = client.get("/api/destinations?category=hills")
    assert hills_res.status_code == 200
    hills_ids = [d["id"] for d in hills_res.json()]
    assert "munnar" in hills_ids
    assert "manali" in hills_ids
    assert "darjeeling" in hills_ids



def test_get_destination_by_id_success():
    """Tests looking up a valid destination by ID."""
    response = client.get("/api/destinations/jaipur")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "jaipur"
    assert data["name"] == "Jaipur"
    assert data["state"] == "Rajasthan"
    assert "Amber Palace" in data["highlights"][0]


def test_get_destination_by_id_not_found():
    """Tests 404 for an unknown destination."""
    response = client.get("/api/destinations/atlantis")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_create_valid_trip_plan():
    """Tests valid trip planning request and budget math."""
    payload = {
        "startingCity": "Bengaluru",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 30000,
        "interests": ["culture", "food"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Destination info
    assert data["destination"]["id"] == "hyderabad"
    assert data["numDays"] == 3
    assert len(data["activeDays"]) == 3
    assert data["travelStyle"] == "balanced"
    assert data["isSample"] is True

    # Mathematical integrity check
    stay = data["accommodationCost"]
    food = data["foodCost"]
    transit = data["transportCost"]
    activities = data["activitiesCost"]
    total = data["totalEstimatedCost"]
    remaining = data["remainingBudget"]
    user_budget = data["userBudget"]

    assert stay + food + transit + activities == total
    assert user_budget - total == remaining
    assert remaining > 0
    assert data["isOverBudget"] is False
    assert data["deficit"] == 0


def test_trip_plan_budget_deficit():
    """Tests budget deficit calculation when trip cost exceeds user budget."""
    payload = {
        "startingCity": "Mumbai",
        "destinationId": "goa",
        "days": 4,
        "budget": 10000,  # Low budget for 4 days in comfort
        "interests": ["nature"],
        "travelStyle": "comfort",
        "budgetOptimized": False
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["isOverBudget"] is True
    assert data["remainingBudget"] < 0
    assert data["deficit"] == abs(data["remainingBudget"])


def test_trip_plan_invalid_budget():
    """Tests validation error when budget is below minimum threshold."""
    payload = {
        "startingCity": "Delhi",
        "destinationId": "jaipur",
        "days": 3,
        "budget": 2000,  # Below 5000 min
        "interests": ["culture"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 422


def test_trip_plan_invalid_days():
    """Tests validation error for invalid durations (0, negative, >30)."""
    for invalid_day in [0, -1, -5, 31, 100]:
        payload = {
            "startingCity": "Delhi",
            "destinationId": "jaipur",
            "days": invalid_day,
            "budget": 25000,
            "interests": ["culture"],
            "travelStyle": "balanced"
        }
        response = client.post("/api/trips/plan", json=payload)
        assert response.status_code == 422, f"Expected 422 for days={invalid_day}"


def test_trip_plan_1_day():
    """Tests 1-day trip generation, single activeDay, and daily rate derivation."""
    payload = {
        "startingCity": "Mumbai",
        "destinationId": "goa",
        "days": 1,
        "budget": 15000,
        "interests": ["beaches"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 1
    assert len(data["activeDays"]) == 1
    assert data["activeDays"][0]["dayNumber"] == 1
    assert data["accommodationCost"] == data["dailyStay"] * 1
    assert data["foodCost"] == data["dailyFood"] * 1
    assert data["transportCost"] == data["dailyTransit"] * 1
    assert data["totalEstimatedCost"] == data["accommodationCost"] + data["foodCost"] + data["transportCost"] + data["activitiesCost"]


def test_trip_plan_3_days():
    """Tests 3-day standard trip generation with full mathematical integrity."""
    payload = {
        "startingCity": "Bengaluru",
        "destinationId": "munnar",
        "days": 3,
        "budget": 25000,
        "interests": ["nature"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 3
    assert len(data["activeDays"]) == 3
    assert [d["dayNumber"] for d in data["activeDays"]] == [1, 2, 3]
    assert data["accommodationCost"] == data["dailyStay"] * 3
    assert data["foodCost"] == data["dailyFood"] * 3
    assert data["transportCost"] == data["dailyTransit"] * 3
    assert data["totalEstimatedCost"] == data["accommodationCost"] + data["foodCost"] + data["transportCost"] + data["activitiesCost"]


def test_trip_plan_7_days():
    """Tests 7-day extended trip generation with non-duplicated varied schedules."""
    payload = {
        "startingCity": "Hyderabad",
        "destinationId": "jaipur",
        "days": 7,
        "budget": 45000,
        "interests": ["culture", "food"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 7
    assert len(data["activeDays"]) == 7
    assert [d["dayNumber"] for d in data["activeDays"]] == list(range(1, 8))
    
    # Verify unique themes
    themes = [d["theme"] for d in data["activeDays"]]
    assert len(set(themes)) == 7, "All 7 daily themes must be distinct"

    # Math integrity
    assert data["accommodationCost"] == data["dailyStay"] * 7
    assert data["foodCost"] == data["dailyFood"] * 7
    assert data["transportCost"] == data["dailyTransit"] * 7
    assert data["totalEstimatedCost"] == data["accommodationCost"] + data["foodCost"] + data["transportCost"] + data["activitiesCost"]


def test_trip_plan_14_days():
    """Tests 14-day two-week trip generation with non-duplicated schedules and math integrity."""
    payload = {
        "startingCity": "Kolkata",
        "destinationId": "varanasi",
        "days": 14,
        "budget": 80000,
        "interests": ["culture", "relaxation"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 14
    assert len(data["activeDays"]) == 14
    assert [d["dayNumber"] for d in data["activeDays"]] == list(range(1, 15))

    # Verify unique themes
    themes = [d["theme"] for d in data["activeDays"]]
    assert len(set(themes)) == 14, "All 14 daily themes must be distinct"

    # Math integrity
    assert data["accommodationCost"] == data["dailyStay"] * 14
    assert data["foodCost"] == data["dailyFood"] * 14
    assert data["transportCost"] == data["dailyTransit"] * 14
    assert data["totalEstimatedCost"] == data["accommodationCost"] + data["foodCost"] + data["transportCost"] + data["activitiesCost"]


def test_adapt_shorten_trip_custom_durations():
    """Tests shortening a 7-day trip to 6 days and verifying recalculated budget."""
    base_plan = {
        "startingCity": "Bengaluru",
        "destinationId": "goa",
        "days": 7,
        "budget": 50000,
        "interests": ["beaches", "relaxation"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    response = client.post("/api/trips/adapt", json={"action": "shorten_trip", "planRequest": base_plan})
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 6
    assert len(data["activeDays"]) == 6
    assert data["accommodationCost"] == data["dailyStay"] * 6


def test_trip_plan_unknown_destination():
    """Tests 404 response when destination does not exist."""
    payload = {
        "startingCity": "Delhi",
        "destinationId": "nonexistent_city",
        "days": 3,
        "budget": 25000,
        "interests": ["culture"],
        "travelStyle": "balanced"
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 404


def test_adapt_shorten_trip():
    """Tests shortening a 3-day trip to 2 days."""
    base_plan = {
        "startingCity": "Bengaluru",
        "destinationId": "munnar",
        "days": 3,
        "budget": 25000,
        "interests": ["nature", "relaxation"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    payload = {
        "action": "shorten_trip",
        "planRequest": base_plan
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numDays"] == 2
    assert len(data["activeDays"]) == 2
    assert data["destination"]["id"] == "munnar"


def test_adapt_shorten_trip_min_days_error():
    """Tests error when attempting to shorten a 1-day trip."""
    base_plan = {
        "startingCity": "Bengaluru",
        "destinationId": "munnar",
        "days": 1,
        "budget": 25000,
        "interests": ["nature"],
        "travelStyle": "balanced"
    }
    payload = {
        "action": "shorten_trip",
        "planRequest": base_plan
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 422
    assert "minimum duration" in response.json()["detail"].lower()


def test_adapt_change_travel_style():
    """Tests changing travel style from balanced to comfort."""
    base_plan = {
        "startingCity": "Hyderabad",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 35000,
        "interests": ["culture", "food"],
        "travelStyle": "budget",
        "budgetOptimized": False
    }
    payload = {
        "action": "change_travel_style",
        "planRequest": base_plan,
        "newTravelStyle": "comfort"
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["travelStyle"] == "comfort"
    # Comfort rate for Hyderabad stay is 5800/day * 3 = 17400
    assert data["accommodationCost"] == 17400


def test_adapt_reduce_budget():
    """Tests budget optimization reduces costs by activating economy rates."""
    base_plan = {
        "startingCity": "Mumbai",
        "destinationId": "goa",
        "days": 3,
        "budget": 30000,
        "interests": ["food", "nature"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    payload = {
        "action": "reduce_budget",
        "planRequest": base_plan
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["budgetOptimized"] is True
    # With budget optimization, total must be lower than non-optimized
    non_opt_res = client.post("/api/trips/plan", json=base_plan).json()
    assert data["totalEstimatedCost"] < non_opt_res["totalEstimatedCost"]


def test_adapt_unsupported_action():
    """Tests 422 response for unsupported adaptation action."""
    base_plan = {
        "startingCity": "Mumbai",
        "destinationId": "goa",
        "days": 3,
        "budget": 30000,
        "interests": ["food"],
        "travelStyle": "balanced"
    }
    payload = {
        "action": "teleport_traveler",
        "planRequest": base_plan
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 422
    assert "unsupported adaptation action" in response.json()["detail"].lower()


def test_adapt_reduce_budget_toggle_off():
    """Tests that reduce_budget toggles back to standard rates when already active."""
    optimized_plan = {
        "startingCity": "Mumbai",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 25000,
        "interests": ["culture", "food"],
        "travelStyle": "balanced",
        "budgetOptimized": True
    }
    payload = {
        "action": "reduce_budget",
        "planRequest": optimized_plan
    }
    response = client.post("/api/trips/adapt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["budgetOptimized"] is False
    # Standard rates must be higher than economy rates
    assert data["totalEstimatedCost"] > 12850


def test_adapt_activities_cost_integrity():
    """Tests that activeDays activity costs match activitiesCost in both standard and economy modes."""
    # 1. Standard mode
    base_plan = {
        "startingCity": "Mumbai",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 25000,
        "interests": ["culture", "food"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    std_res = client.post("/api/trips/plan", json=base_plan).json()
    std_sum = sum(
        day[slot]["cost"]
        for day in std_res["activeDays"]
        for slot in ["morning", "afternoon", "evening"]
    )
    assert std_sum == std_res["activitiesCost"]

    # 2. Economy mode via adaptation
    adapt_payload = {
        "action": "reduce_budget",
        "planRequest": base_plan
    }
    opt_res = client.post("/api/trips/adapt", json=adapt_payload).json()
    opt_sum = sum(
        day[slot]["cost"]
        for day in opt_res["activeDays"]
        for slot in ["morning", "afternoon", "evening"]
    )
    assert opt_sum == opt_res["activitiesCost"]
    assert opt_res["activitiesCost"] < std_res["activitiesCost"]


def test_adapt_chained_sequence():
    """Tests sequence: plan -> reduce_budget -> shorten_trip -> change_travel_style."""
    # Step 1: Initial plan
    step1_req = {
        "startingCity": "Mumbai",
        "destinationId": "hyderabad",
        "days": 3,
        "budget": 25000,
        "interests": ["culture", "food"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    step1_res = client.post("/api/trips/plan", json=step1_req).json()
    assert step1_res["numDays"] == 3
    assert step1_res["budgetOptimized"] is False

    # Step 2: Reduce budget
    step2_res = client.post("/api/trips/adapt", json={
        "action": "reduce_budget",
        "planRequest": {
            **step1_req,
            "budgetOptimized": step1_res["budgetOptimized"]
        }
    }).json()
    assert step2_res["budgetOptimized"] is True
    assert step2_res["totalEstimatedCost"] < step1_res["totalEstimatedCost"]

    # Step 3: Shorten trip
    step3_res = client.post("/api/trips/adapt", json={
        "action": "shorten_trip",
        "planRequest": {
            **step1_req,
            "days": step2_res["numDays"],
            "budgetOptimized": step2_res["budgetOptimized"]
        }
    }).json()
    assert step3_res["numDays"] == 2
    assert step3_res["budgetOptimized"] is True
    assert len(step3_res["activeDays"]) == 2

    # Step 4: Change travel style to comfort
    step4_res = client.post("/api/trips/adapt", json={
        "action": "change_travel_style",
        "planRequest": {
            **step1_req,
            "days": step3_res["numDays"],
            "travelStyle": step3_res["travelStyle"],
            "budgetOptimized": step3_res["budgetOptimized"]
        },
        "newTravelStyle": "comfort"
    }).json()
    assert step4_res["travelStyle"] == "comfort"
    assert step4_res["numDays"] == 2
    assert step4_res["budgetOptimized"] is True


def test_create_trip_plan_custom_destination_unverified():
    """Tests manual destination entry returns unverified flag with non-fabricated activities."""
    payload = {
        "startingCity": "Pune",
        "destinationId": "custom",
        "customDestinationName": "Chikmagalur",
        "isCustomDestination": True,
        "days": 3,
        "budget": 20000,
        "interests": ["nature", "relaxation"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["isVerified"] is False
    assert data["destination"]["id"] == "custom"
    assert "Chikmagalur" in data["destination"]["name"]
    assert "Limited Information" in data["disclaimer"]

    # Verify no fabricated attraction fees (activities cost is 0)
    assert data["activitiesCost"] == 0
    for day in data["activeDays"]:
        for slot in ["morning", "afternoon", "evening"]:
            assert day[slot]["cost"] == 0
            assert "not fabricated" in day[slot]["explanation"].lower() or "independent" in day[slot]["title"].lower()

    # Mathematical integrity check
    stay = data["accommodationCost"]
    food = data["foodCost"]
    transit = data["transportCost"]
    activities = data["activitiesCost"]
    assert stay + food + transit + activities == data["totalEstimatedCost"]


def test_create_trip_plan_custom_destination_matches_curated():
    """Tests that a manual entry matching a curated destination automatically resolves to verified benchmarks."""
    payload = {
        "startingCity": "Delhi",
        "destinationId": "custom",
        "customDestinationName": "Udaipur",
        "isCustomDestination": True,
        "days": 3,
        "budget": 25000,
        "interests": ["heritage"],
        "travelStyle": "balanced",
        "budgetOptimized": False
    }
    response = client.post("/api/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["isVerified"] is True
    assert data["destination"]["id"] == "udaipur"
    assert data["destination"]["name"] == "Udaipur"


def test_detailed_itinerary_schedule_completeness():
    """Tests that daily schedules provide duration, practical tips, meal suggestions, and route notes across varied durations."""
    for days in [1, 3, 7, 14, 30]:
        payload = {
            "startingCity": "Mumbai",
            "destinationId": "goa",
            "days": days,
            "budget": 20000 + (days * 5000),
            "interests": ["beaches", "food"],
            "travelStyle": "balanced",
            "budgetOptimized": False
        }
        res = client.post("/api/trips/plan", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["activeDays"]) == days

        for day in data["activeDays"]:
            assert isinstance(day["dayNumber"], int)
            assert len(day["theme"]) > 0
            for slot_key in ["morning", "afternoon", "evening"]:
                slot = day[slot_key]
                assert len(slot["title"]) > 0
                assert len(slot["location"]) > 0
                assert len(slot["explanation"]) > 0
                assert slot["duration"] is not None and len(slot["duration"]) > 0
                assert slot["practicalTips"] is not None and len(slot["practicalTips"]) > 0
                assert slot["mealSuggestion"] is not None and len(slot["mealSuggestion"]) > 0
                assert slot["transitNote"] is not None and len(slot["transitNote"]) > 0


def test_daily_budget_breakdown_mathematical_consistency():
    """Tests that daily costs strictly add up to the total trip cost and component sums."""
    for opt in [False, True]:
        payload = {
            "startingCity": "Bengaluru",
            "destinationId": "hyderabad",
            "days": 5,
            "budget": 40000,
            "interests": ["culture", "food"],
            "travelStyle": "balanced",
            "budgetOptimized": opt
        }
        res = client.post("/api/trips/plan", json=payload)
        assert res.status_code == 200
        data = res.json()

        active_days = data["activeDays"]
        sum_day_stay = sum(d["dayStay"] for d in active_days)
        sum_day_food = sum(d["dayFood"] for d in active_days)
        sum_day_transit = sum(d["dayTransit"] for d in active_days)
        sum_day_activities = sum(d["dayActivities"] for d in active_days)
        sum_day_total = sum(d["dayTotal"] for d in active_days)

        for d in active_days:
            assert d["dayTotal"] == d["dayStay"] + d["dayFood"] + d["dayTransit"] + d["dayActivities"]
            slot_act_sum = sum(d[slot]["cost"] for slot in ["morning", "afternoon", "evening"])
            assert d["dayActivities"] == slot_act_sum

        assert sum_day_stay == data["accommodationCost"]
        assert sum_day_food == data["foodCost"]
        assert sum_day_transit == data["transportCost"]
        assert sum_day_activities == data["activitiesCost"]
        assert sum_day_total == data["totalEstimatedCost"]


def test_unverified_destination_detailed_schedule_and_budget():
    """Tests that unverified destinations retain zero activity fees and explicit transparency."""
    payload = {
        "startingCity": "Delhi",
        "destinationId": "custom",
        "customDestinationName": "Ziro Valley",
        "isCustomDestination": True,
        "days": 4,
        "budget": 30000,
        "interests": ["nature"],
        "travelStyle": "balanced"
    }
    res = client.post("/api/trips/plan", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["isVerified"] is False
    assert data["activitiesCost"] == 0

    for day in data["activeDays"]:
        assert day["isCostVerified"] is False
        assert day["dayActivities"] == 0
        assert day["dayTotal"] == day["dayStay"] + day["dayFood"] + day["dayTransit"]

        for slot_key in ["morning", "afternoon", "evening"]:
            slot = day[slot_key]
            assert slot["cost"] == 0
            assert slot["isCostEstimated"] is True
            assert "not fabricated" in slot["explanation"].lower() or "not fabricated" in slot["practicalTips"].lower()
            assert slot["duration"] is not None
            assert slot["transitNote"] is not None
            assert slot["mealSuggestion"] is not None


