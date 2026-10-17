"""Unit and integration tests for Phase 6.4 verified booking resources and admission links."""
import pytest
from app.models import BookingResource, Activity, TripPlanRequest, AdaptTripRequest, AdaptActionEnum
from app.data import SAMPLE_ITINERARIES, VERIFIED_BOOKING_RESOURCES
from app.services.trip_planner import calculate_trip_plan, adapt_trip_plan


def test_booking_resource_model_validation():
    """Validates that BookingResource adheres to required Pydantic constraints."""
    res = BookingResource(
        url="https://asi.nic.in/",
        provider_name="Archaeological Survey of India (ASI)",
        resource_type="official_monument",
        label="Official ASI Monument Portal ↗",
        description="Centrally protected monument ticketing and visitor information via ASI.",
        is_verified=True,
    )
    assert res.url.startswith("https://")
    assert res.provider_name == "Archaeological Survey of India (ASI)"
    assert res.is_verified is True

    dumped = res.model_dump(by_alias=True)
    assert dumped["providerName"] == "Archaeological Survey of India (ASI)"
    assert dumped["resourceType"] == "official_monument"
    assert dumped["isVerified"] is True


def test_verified_booking_resources_presence():
    """Ensures verified landmarks have authoritative, genuine booking links."""
    # Hyderabad Charminar (Day 1, morning)
    hyd_day1_morning = SAMPLE_ITINERARIES["hyderabad"]["days"][0]["morning"]
    assert "bookingResource" in hyd_day1_morning
    assert hyd_day1_morning["bookingResource"]["url"] == "https://asi.nic.in/"
    assert "Archaeological Survey of India" in hyd_day1_morning["bookingResource"]["providerName"]

    # Salar Jung Museum (Day 3, morning)
    hyd_day3_morning = SAMPLE_ITINERARIES["hyderabad"]["days"][2]["morning"]
    assert "bookingResource" in hyd_day3_morning
    assert hyd_day3_morning["bookingResource"]["url"] == "https://salarjungmuseum.in/"

    # Eravikulam National Park (Munnar Day 2, morning)
    mun_day2_morning = SAMPLE_ITINERARIES["munnar"]["days"][1]["morning"]
    assert "bookingResource" in mun_day2_morning
    assert mun_day2_morning["bookingResource"]["url"] == "https://www.eravikulamnationalpark.in/"

    # The City Palace Jaipur (Jaipur Day 2, morning)
    jp_day2_morning = SAMPLE_ITINERARIES["jaipur"]["days"][1]["morning"]
    assert "bookingResource" in jp_day2_morning
    assert jp_day2_morning["bookingResource"]["url"] == "https://thecitypalacejaipur.com/"


def test_unverified_stops_do_not_fabricate_booking_urls():
    """Verifies that activities without verified online booking do NOT fabricate booking resources."""
    # Miramar Beach (Goa Day 1 evening) - public beach
    goa_day1_evening = SAMPLE_ITINERARIES["goa"]["days"][0]["evening"]
    assert goa_day1_evening.get("bookingResource") is None

    # Shadab Restaurant (Hyderabad Day 1 afternoon) - walk-in dining
    hyd_day1_noon = SAMPLE_ITINERARIES["hyderabad"]["days"][0]["afternoon"]
    assert hyd_day1_noon.get("bookingResource") is None

    # Pothamedu Viewpoint (Munnar Day 1 evening) - scenic overlook
    mun_day1_eve = SAMPLE_ITINERARIES["munnar"]["days"][0]["evening"]
    assert mun_day1_eve.get("bookingResource") is None


def test_all_booking_urls_are_secure_https():
    """Guarantees every single verified booking URL uses secure HTTPS protocol."""
    for (dest, day, slot), res in VERIFIED_BOOKING_RESOURCES.items():
        assert res["url"].startswith("https://"), f"Insecure URL found for {dest}:{day}:{slot}: {res['url']}"
        assert res["isVerified"] is True
        assert len(res["providerName"]) > 3
        assert len(res["label"]) > 3


from app.services.trip_planner import create_trip_plan, adapt_trip_plan


def test_trip_plan_api_response_includes_booking_resources():
    """Tests that calculate_trip_plan includes bookingResource on activeDays."""
    req = TripPlanRequest(
        destination_id="hyderabad",
        days=3,
        budget=35000,
        travel_style="balanced",
        starting_city="Mumbai",
        interests=["culture"]
    )
    plan = create_trip_plan(req)
    active_days = plan.active_days

    # Day 1 morning (Charminar)
    day1_morn = active_days[0].morning if hasattr(active_days[0], "morning") else active_days[0]["morning"]
    booking_res = day1_morn.booking_resource if hasattr(day1_morn, "booking_resource") else day1_morn.get("bookingResource")
    assert booking_res is not None
    url = booking_res.url if hasattr(booking_res, "url") else booking_res["url"]
    assert url == "https://asi.nic.in/"

    # Day 1 afternoon (Shadab) should have None
    day1_noon = active_days[0].afternoon if hasattr(active_days[0], "afternoon") else active_days[0]["afternoon"]
    booking_res_noon = day1_noon.booking_resource if hasattr(day1_noon, "booking_resource") else day1_noon.get("bookingResource")
    assert booking_res_noon is None


def test_budget_immutability_with_booking_resources():
    """Verifies that adding booking resources does NOT mutate any costs or calculations."""
    req = TripPlanRequest(
        destination_id="hyderabad",
        days=3,
        budget=30000,
        travel_style="balanced",
        starting_city="Mumbai",
        interests=["culture"]
    )
    plan = create_trip_plan(req)

    # Base daily rates for Hyderabad balanced: stay=2800, food=1200, transit=800 -> 4800/day
    assert plan.daily_stay == 2800
    assert plan.daily_food == 1200
    assert plan.daily_transit == 800
    assert plan.accommodation_cost == 8400
    assert plan.food_cost == 3600
    assert plan.transport_cost == 2400

    # Activity sum
    total_acts = sum(d.day_activities if hasattr(d, "day_activities") else d["dayActivities"] for d in plan.active_days)
    assert plan.activities_cost == total_acts
    assert plan.total_estimated_cost == plan.accommodation_cost + plan.food_cost + plan.transport_cost + total_acts


def test_adapt_trip_preserves_booking_resources():
    """Tests that adapting an itinerary preserves booking resources on remaining days."""
    req = TripPlanRequest(
        destination_id="hyderabad",
        days=3,
        budget=35000,
        travel_style="balanced",
        starting_city="Mumbai",
        interests=["culture"]
    )
    initial_plan = create_trip_plan(req)
    assert initial_plan.num_days == 3

    adapt_req = AdaptTripRequest(
        plan_request=req,
        action=AdaptActionEnum.SHORTEN_TRIP.value,
    )
    adapted = adapt_trip_plan(adapt_req)

    assert adapted.num_days == 2
    # Day 1 morning still has Charminar booking resource
    day1_morn = adapted.active_days[0].morning if hasattr(adapted.active_days[0], "morning") else adapted.active_days[0]["morning"]
    booking_res = day1_morn.booking_resource if hasattr(day1_morn, "booking_resource") else day1_morn.get("bookingResource")
    assert booking_res is not None
    url = booking_res.url if hasattr(booking_res, "url") else booking_res["url"]
    assert url == "https://asi.nic.in/"
