"""Trip planning and deterministic budget calculation service."""
from typing import List, Optional, Dict, Any, Tuple
from copy import deepcopy

from app.data import DESTINATIONS, SAMPLE_ITINERARIES
from app.models import (
    Destination,
    TripPlanRequest,
    TripPlanResponse,
    AdaptTripRequest,
    AdaptActionEnum,
    TravelStyleEnum,
)
from app.services.route_service import build_day_route_segments


HILL_STATION_IDS = {
    "munnar", "manali", "leh-ladakh", "ooty", "darjeeling", "coorg", "shillong", "kodaikanal"
}


def get_all_destinations(
    search: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns curated Indian destinations, with optional search and category filters.
    """
    results = DESTINATIONS

    if search:
        q = search.strip().lower()
        results = [
            d for d in results
            if q in d.get("name", "").lower()
            or q in d.get("state", "").lower()
            or q in d.get("tagline", "").lower()
        ]

    if category and category.strip().lower() not in ["all", ""]:
        cat = category.strip().lower()
        if cat in ["hills", "hill_stations", "hill station", "hill stations"]:
            results = [d for d in results if d.get("id") in HILL_STATION_IDS]
        elif cat in ["heritage", "culture"]:
            results = [
                d for d in results
                if "heritage" in [x.lower() for x in d.get("primaryInterests", [])]
                or "culture" in [x.lower() for x in d.get("primaryInterests", [])]
            ]
        else:
            results = [
                d for d in results
                if cat in [x.lower() for x in d.get("primaryInterests", [])]
            ]

    return results


def get_destination_by_id(destination_id: str) -> Optional[Dict[str, Any]]:
    """Finds a single destination by its ID or exact name."""
    clean_id = destination_id.strip().lower()
    for dest in DESTINATIONS:
        if dest["id"].lower() == clean_id or dest["name"].lower() == clean_id:
            return dest
    return None


EXTENDED_DAY_TEMPLATES = [
    # Day 5 (index 0)
    {
        "theme": "Excursions to Countryside & Historic Enclaves",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Scenic Countryside Drive & Outskirts Walk",
            "location": "Regional Outskirts, {name}",
            "cost": 120,
            "explanation": "Venture past the city perimeter to observe rural agrarian landscapes, traditional irrigation groves, and quiet scenic hillocks.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Farmstead Luncheon & Rural Culinary Tasting",
            "location": "Outskirts Farmstead, {name}",
            "cost": 350,
            "explanation": "Sample farm-fresh regional cooking prepared using indigenous ingredients, fresh herbs, and traditional wood-fire clay hearths.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "High Ridge Sunset Panorama",
            "location": "Valley Lookout, {name}",
            "cost": 0,
            "explanation": "Enjoy panoramic twilight vistas across the horizon before heading back to your accommodation.",
            "category": "relaxation"
        }
    },
    # Day 6 (index 1)
    {
        "theme": "Artisanal Enclaves & Generational Craft Discovery",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Traditional Craft Workshops & Weavers Walk",
            "location": "Artisan Quarter, {name}",
            "cost": 150,
            "explanation": "Visit generational craft studios, potters, or handloom weavers preserving regional heritage arts.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:30 PM – 03:30 PM",
            "title": "Heritage Café & Regional Confectionery Tasting",
            "location": "Old Bazaar, {name}",
            "cost": 250,
            "explanation": "Pause at a long-standing local café for authentic regional confectionery, freshly ground snacks, and tea.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Central Promenade Twilight Stroll",
            "location": "Civic Center / Promenade, {name}",
            "cost": 0,
            "explanation": "Walk along the lively central town square or promenade observing evening local life and street music.",
            "category": "relaxation"
        }
    },
    # Day 7 (index 2)
    {
        "theme": "Mid-Trip Slow Travel, Rest & Wellness Day",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 11:30 AM",
            "title": "Shaded Botanical Garden Walk & Morning Reflection",
            "location": "Botanical Gardens, {name}",
            "cost": 0,
            "explanation": "Take an unhurried morning to recharge, journal, or practice mindful meditation under ancient banyans and flowering canopies.",
            "category": "relaxation"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Slow Courtyard Brunch & Literature Browsing",
            "location": "Courtyard Café, {name}",
            "cost": 300,
            "explanation": "Relax over an unhurried brunch, browse local literature, and read in a quiet shaded heritage courtyard.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Waterfront Walk & Evening Breeze",
            "location": "Lakeside / Waterfront Walkway, {name}",
            "cost": 50,
            "explanation": "A calm sunset walk beside local water bodies or tree-lined riverside promenades.",
            "category": "nature"
        }
    },
    # Day 8 (index 3)
    {
        "theme": "Nature Reserves & Botanical Trails",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Protected Flora & Birdwatching Sanctuary Trail",
            "location": "Nature Sanctuary, {name}",
            "cost": 160,
            "explanation": "Explore protected native flora, ancient trees, and native bird habitats along a guided regional nature trail.",
            "category": "nature"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Open-Air Shaded Picnic Lunch",
            "location": "Forest Clearing, {name}",
            "cost": 220,
            "explanation": "Enjoy an outdoor packed picnic featuring local fresh flatbreads, seasonal fruits, and savory bites.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Elevated Plateau Stargazing & Crisp Breeze",
            "location": "Elevated Ridge Point, {name}",
            "cost": 0,
            "explanation": "Unwind away from city light glare enjoying open night skies and refreshing evening air.",
            "category": "relaxation"
        }
    },
    # Day 9 (index 4)
    {
        "theme": "Hidden Architecture & Sacred Shrines",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Secluded Heritage Shrines & Stone Carvings",
            "location": "Historic Precinct, {name}",
            "cost": 100,
            "explanation": "Discover less-frequented stone-carved shrines, ancient stepwells, and historic architectural masonry.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Regional Traditional Thali at Heritage Precinct",
            "location": "Old Town Eatery, {name}",
            "cost": 280,
            "explanation": "Experience authentic local multi-course culinary combinations served on traditional plantain leaves.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Ambient Twilight Bells & Acoustic Devotional Chimes",
            "location": "Sacred Steps / Courtyard, {name}",
            "cost": 0,
            "explanation": "Witness ambient evening oil-lamp ceremonies and soothing acoustic prayer chimes.",
            "category": "culture"
        }
    },
    # Day 10 (index 5)
    {
        "theme": "Bazaar Gastronomy & Local Produce Deep-Dive",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Historic Spice & Fresh Produce Mandi Walk",
            "location": "Central Mandi Bazaars, {name}",
            "cost": 100,
            "explanation": "Walk through vibrant morning stalls loaded with indigenous seasonal produce, wild honey, and aromatic whole spices.",
            "category": "food"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Regional Street Food & Savory Delicacies Trail",
            "location": "Culinary Lanes, {name}",
            "cost": 300,
            "explanation": "Taste regional specialty street snacks, steamed savory cakes, and hand-churned dairy refreshments.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Terrace Sunset Chai & Rooftop Vistas",
            "location": "Terrace Overlook, {name}",
            "cost": 120,
            "explanation": "Savor spiced cardamom tea while gazing across the panoramic sunset cityscape or valley.",
            "category": "relaxation"
        }
    },
    # Day 11 (index 6)
    {
        "theme": "Panoramic Ridges & Valley Overlooks",
        "morning": {
            "period": "Morning",
            "time": "08:00 AM – 11:30 AM",
            "title": "Country Trail & Elevated Ridge Trek",
            "location": "Ridge Outskirts, {name}",
            "cost": 150,
            "explanation": "A moderate morning hike across natural paths offering scenic vantage points over the plains or valley.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Hillside Lunch with Panoramic Valley Views",
            "location": "Viewpoint Dhaba, {name}",
            "cost": 320,
            "explanation": "Refuel with hearty regional lentils, fresh flatbreads, and warm seasonal soups.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Golden Hour Landscape Photography",
            "location": "Sunset Point, {name}",
            "cost": 0,
            "explanation": "Capture golden-hour landscape photography as shadows lengthen across the natural horizon.",
            "category": "nature"
        }
    },
    # Day 12 (index 7)
    {
        "theme": "Cultural Museums & Archival Treasures",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Regional History & Folk Artifacts Exhibition",
            "location": "Museum Complex, {name}",
            "cost": 120,
            "explanation": "Inspect indigenous textiles, folk instruments, and historical documents chronicling regional history.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:30 PM – 03:30 PM",
            "title": "Garden Pavilion Dining & Arts Café",
            "location": "Cultural Center Café, {name}",
            "cost": 380,
            "explanation": "Explore contemporary regional art installations followed by lunch in a shaded garden pavilion.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Evening Folk Recital & Traditional Music",
            "location": "Amphitheatre, {name}",
            "cost": 200,
            "explanation": "Enjoy an authentic regional folk music or classical instrumental recital.",
            "category": "culture"
        }
    },
    # Day 13 (index 8)
    {
        "theme": "Waterfront Serenity & Riverine Breezes",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Traditional Wooden Boat Ride or Shoreline Drift",
            "location": "Waterfront Pier, {name}",
            "cost": 250,
            "explanation": "Glide across peaceful waterways or along the shoreline accompanied by morning mist and gentle reflections.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Catch-of-the-Day / Coastal Spice Lunch",
            "location": "Waterfront Diner, {name}",
            "cost": 420,
            "explanation": "Fresh seasonal produce or local river/coastal catch spiced with regional aromatics.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Harbor Pier Walk & Fisherman's Twilight",
            "location": "Waterfront Jetty, {name}",
            "cost": 0,
            "explanation": "Breathe in crisp evening air as local boats dock for the night under sunset hues.",
            "category": "relaxation"
        }
    },
    # Day 14 (index 9)
    {
        "theme": "Two-Week Milestone & Restorative Living",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Unhurried Alleyway Stroll & Architecture Sketching",
            "location": "Old Quarter Nooks, {name}",
            "cost": 0,
            "explanation": "An open morning to wander unscripted alleyways, photograph doorways, or rest in quiet nooks.",
            "category": "relaxation"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Traditional Herbal Wellness & Body Rejuvenation",
            "location": "Wellness Center, {name}",
            "cost": 500,
            "explanation": "Rejuvenating traditional massage using fragrant herbal botanical oils and centuries-old wellness techniques.",
            "category": "relaxation"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:30 PM",
            "title": "Celebratory Heritage Terrace Dining",
            "location": "Rooftop Restaurant, {name}",
            "cost": 450,
            "explanation": "Two-week milestone celebratory dinner observing regional culinary craft from an open-air rooftop.",
            "category": "food"
        }
    },
    # Day 15 (index 10)
    {
        "theme": "Village Immersion & Rural Community Crafts",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Excursion to Neighboring Rural Craft Hamlet",
            "location": "Artisan Village, near {name}",
            "cost": 180,
            "explanation": "Observe pottery wheels turning, clay-oven baking, and traditional village craftsmanship.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Homestyle Millet Flatbreads & Farmstead Feast",
            "location": "Homestead Kitchen, {name}",
            "cost": 280,
            "explanation": "Share home-cooked seasonal flatbreads, churned butter, and slow-simmered spiced lentil stew.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Pastoral Countryside Stroll through Farmland Trails",
            "location": "Farmland Perimeter, {name}",
            "cost": 0,
            "explanation": "Golden light illuminating agricultural terraces and peaceful tree lines.",
            "category": "nature"
        }
    },
    # Day 16 (index 11)
    {
        "theme": "Geological Marvels & Natural Rock Enclaves",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Natural Caves, Boulders & Rock Formations Walk",
            "location": "Geological Area, {name}",
            "cost": 100,
            "explanation": "Explore ancient granite boulders, limestone caves, or canyon crevices sculpted by time.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Roadside Clay-Oven Dhaba Feast",
            "location": "Highway Route, Outskirts of {name}",
            "cost": 250,
            "explanation": "Eat authentic butter-drenched tandoori rotis, seasonal curry, and slow-brewed lentils.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Sunset Watch from Elevated Boulder Ridge",
            "location": "Boulder Ridge, {name}",
            "cost": 0,
            "explanation": "Panoramic 360-degree views across the countryside as twilight falls.",
            "category": "nature"
        }
    },
    # Day 17 (index 12)
    {
        "theme": "Literary Quarters & Indo-Saracenic Avenues",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Historic Stone Arches & Heritage Library Walk",
            "location": "Academic Quarter, {name}",
            "cost": 50,
            "explanation": "Walk through majestic stone arches, historic library halls, and leafy colonial avenues.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:30 PM – 03:30 PM",
            "title": "Classic Coffeehouse & Regional Savory Bites",
            "location": "Heritage Coffeehouse, {name}",
            "cost": 160,
            "explanation": "Classic filter coffee and savory snacks in a buzzing historic establishment frequented by locals.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Shaded Canopy Walk under Century-Old Trees",
            "location": "Heritage Boulevard, {name}",
            "cost": 0,
            "explanation": "Quiet residential avenues flanked by century-old shade trees and fragrant blossoms.",
            "category": "relaxation"
        }
    },
    # Day 18 (index 13)
    {
        "theme": "Antique Curios & Vintage Textile Exploration",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Hidden Curio Shops & Heirloom Textile Discovery",
            "location": "Old Market Alleys, {name}",
            "cost": 0,
            "explanation": "Admire vintage brass lamps, carved wooden boxes, and timeless hand-woven tapestries.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Restored Haveli Courtyard Lunch",
            "location": "Haveli Courtyard, {name}",
            "cost": 360,
            "explanation": "Sip fragrant herbal coolers and sample light regional recipes in a quiet restored courtyard.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Evening Rooftop Conversations & City Lights",
            "location": "Terrace Viewpoint, {name}",
            "cost": 80,
            "explanation": "Chat over spiced tea about local history as warm city lights begin to glow.",
            "category": "relaxation"
        }
    },
    # Day 19 (index 14)
    {
        "theme": "Canopy Trails & Eco-Forest Reserves",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Dense Forest Trail & Butterfly Habitat Trek",
            "location": "Eco-Forest Reserve, {name}",
            "cost": 160,
            "explanation": "Trek under lush green tree canopies searching for woodpeckers, hornbills, and native butterflies.",
            "category": "nature"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Riverside Packed Picnic & Stream Rest",
            "location": "Stream Bank, {name}",
            "cost": 200,
            "explanation": "Cool off near bubbling stream rivulets enjoying packed flatbreads and crisp fruit.",
            "category": "relaxation"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Forest Lodge Twilight Calm & Nocturnal Ambience",
            "location": "Forest Edge, {name}",
            "cost": 0,
            "explanation": "Enjoy peaceful silence listening to evening cicadas and nocturnal birds.",
            "category": "nature"
        }
    },
    # Day 20 (index 15)
    {
        "theme": "Slow Transport & Scenic Route Journey",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Scenic Train Viaduct or Country Ferry Crossing",
            "location": "Country Crossing, {name}",
            "cost": 120,
            "explanation": "Enjoy a nostalgic slow-travel journey through scenic tunnels, bridge viaducts, or river bends.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Station-side Chaat & Regional Snacks",
            "location": "Junction Eateries, {name}",
            "cost": 180,
            "explanation": "Sample hot savory snacks, roasted corn on the cob with lime, and clay-cup tea.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Pier Sunset & Waterway Reflection",
            "location": "Town Pier, {name}",
            "cost": 0,
            "explanation": "Peaceful journey back watching village life unfold beside the tracks or riverbank.",
            "category": "relaxation"
        }
    },
    # Day 21 (index 16)
    {
        "theme": "Subterranean Stepwells & Ancient Ramparts",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Historic Stepwell & Geometry Exploration",
            "location": "Ancient Baoli / Stepwell, {name}",
            "cost": 80,
            "explanation": "Descend geometric stone stairs into subterranean cool architectural wonders built centuries ago.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Earthen-Pot Simmered Regional Specialty Feast",
            "location": "Heritage Diner, {name}",
            "cost": 350,
            "explanation": "Traditional slow-cooked earthen-pot delicacies infused with whole aromatic spices.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Citadel Wall Twilight Walk & Distant Vistas",
            "location": "Fort Bastions, {name}",
            "cost": 50,
            "explanation": "Look out over the sprawling landscape from ancient stone watchtowers as day turns to night.",
            "category": "adventure"
        }
    },
    # Day 22 (index 17)
    {
        "theme": "Multi-Faith Heritage & Spiritual Harmony",
        "morning": {
            "period": "Morning",
            "time": "09:00 AM – 12:00 PM",
            "title": "Historic Multi-Faith Architectural Trail",
            "location": "Old Enclave, {name}",
            "cost": 0,
            "explanation": "Walk through peaceful multi-century coexisting sacred places displaying diverse decorative arts.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Simple Organic Vegetarian Dining",
            "location": "Community Dining Hall, {name}",
            "cost": 150,
            "explanation": "Simple, balanced, nutrient-rich vegetarian meal served in calm, contemplative surroundings.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Twilight Silence & Sunset Contemplation",
            "location": "Peace Pavilion, {name}",
            "cost": 0,
            "explanation": "Quiet reflection as temple bells and evening chimes echo softly across the city.",
            "category": "relaxation"
        }
    },
    # Day 23 (index 18)
    {
        "theme": "Hands-on Masterclass & Creative Arts",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Traditional Pottery or Hand-Block Printing Session",
            "location": "Artisan Guild, {name}",
            "cost": 250,
            "explanation": "Learn the basics of throwing clay on a wheel or printing intricate hand-carved wooden blocks.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:30 PM – 03:30 PM",
            "title": "Artisan Guild Garden Café & Refreshments",
            "location": "Guild Courtyard, {name}",
            "cost": 220,
            "explanation": "Celebrate your handmade creation over fresh fruit coolers and regional steamed snacks.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Community Art Gallery Walk & Artists Meetup",
            "location": "Community Art Gallery, {name}",
            "cost": 0,
            "explanation": "View contemporary paintings and photography capturing the region's living culture.",
            "category": "relaxation"
        }
    },
    # Day 24 (index 19)
    {
        "theme": "Agrarian Plantations & Sustainable Groves",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Fragrant Orchard Walk & Soil Ecology Tour",
            "location": "Plantation Outskirts, {name}",
            "cost": 150,
            "explanation": "Walk amidst fragrant flowering trees and learn about sustainable soil stewardship and heritage varietals.",
            "category": "nature"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Farm-to-Table Organic Harvest Lunch",
            "location": "Plantation Diner, {name}",
            "cost": 380,
            "explanation": "Savor seasonal vegetables, artisanal honey, and freshly picked regional greens.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Regional Coffee or Tea Cupping Tasting Session",
            "location": "Tasting Room, {name}",
            "cost": 120,
            "explanation": "Discover subtle flavor notes and traditional roasting profiles.",
            "category": "food"
        }
    },
    # Day 25 (index 20)
    {
        "theme": "Wilderness Trails & Horizon Solitude",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Lesser-Trodden Wilderness Trail Hike",
            "location": "Wilderness Boundary, {name}",
            "cost": 120,
            "explanation": "Peaceful hike along lesser-trodden trails surrounded by natural serenity and wildlife tracks.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "High-Meadow Rest & Mountain / Coastal Overlook",
            "location": "High Meadow, {name}",
            "cost": 200,
            "explanation": "Rest against ancient stone boulders while admiring the untouched horizon.",
            "category": "nature"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Golden Hour Journaling & Twilight Stillness",
            "location": "Scenic Bluff, {name}",
            "cost": 0,
            "explanation": "Capture personal impressions of your extended journey in your travel journal.",
            "category": "relaxation"
        }
    },
    # Day 26 (index 21)
    {
        "theme": "Living Oral Lore & Generational Confectionery",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Storytelling Heritage Walk through Historic Quarters",
            "location": "Old Bastion Quarters, {name}",
            "cost": 200,
            "explanation": "Listen to local storytellers recount medieval folklore and historical neighborhood heritage.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:30 PM – 03:30 PM",
            "title": "Centennial Confectionery Sweets Tasting",
            "location": "Historic Sweetshop, {name}",
            "cost": 180,
            "explanation": "Sample generational specialty sweets and warm milk delicacies.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Clocktower Plaza Leisure Walk & People Watching",
            "location": "Clocktower Plaza, {name}",
            "cost": 0,
            "explanation": "Watch vibrant daily life, evening family strolls, and neighborhood chatter.",
            "category": "relaxation"
        }
    },
    # Day 27 (index 22)
    {
        "theme": "Interactive Culinary Masterclass with Local Hosts",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Home Cooking Workshop: Spices & Breadmaking",
            "location": "Homestay Kitchen, {name}",
            "cost": 350,
            "explanation": "Learn to balance tempering seeds, grind fresh spices, and bake soft flatbreads from scratch.",
            "category": "food"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:00 PM",
            "title": "Shared Family Feast of Home-Cooked Specialties",
            "location": "Host Residence, {name}",
            "cost": 0,
            "explanation": "Enjoy the multi-course meal you cooked together in an intimate, warm setting.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Shaded Garden Walk & Digestive Twilight Stroll",
            "location": "Parklands, {name}",
            "cost": 0,
            "explanation": "Gentle digestive stroll beneath ancient leafy canopies.",
            "category": "relaxation"
        }
    },
    # Day 28 (index 23)
    {
        "theme": "Forgotten Citadels & Rural Horizons",
        "morning": {
            "period": "Morning",
            "time": "08:30 AM – 11:30 AM",
            "title": "Excursion to Ancient Overlook Citadel",
            "location": "Hilltop Citadel (20km), {name}",
            "cost": 100,
            "explanation": "Explore secluded stone ramparts and forgotten towers overlooking rural valleys.",
            "category": "adventure"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:00 PM",
            "title": "Clay-Oven Flatbreads & Village Stew",
            "location": "Village Dhaba, {name}",
            "cost": 220,
            "explanation": "Hearty, unpretentious, slow-simmered regional stews and crisp flatbreads.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Vast Horizon Sunset Watch from Citadel Bastion",
            "location": "Citadel Flagstaff, {name}",
            "cost": 0,
            "explanation": "Breathtaking sunset casting long amber shadows across ancient valleys.",
            "category": "nature"
        }
    },
    # Day 29 (index 24)
    {
        "theme": "Curated Bazaars & Meaningful Souvenirs",
        "morning": {
            "period": "Morning",
            "time": "09:30 AM – 12:30 PM",
            "title": "Gathering Loose Teas, Handwoven Textiles & Spices",
            "location": "Main Bazaars, {name}",
            "cost": 0,
            "explanation": "Gather meaningful gifts: loose-leaf teas, raw spices, silk scarves, brass curios, and handicrafts.",
            "category": "culture"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "01:00 PM – 03:30 PM",
            "title": "Celebratory Retrospective Feast at Landmark Restaurant",
            "location": "Iconic Heritage Restaurant, {name}",
            "cost": 500,
            "explanation": "Revisit your favorite dishes from the entire journey in an opulent festive spread.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:30 PM – 08:00 PM",
            "title": "Packing Mementos & Neighborhood Farewell Walk",
            "location": "Central Promenade, {name}",
            "cost": 0,
            "explanation": "A quiet stroll savoring the sights and sounds of the place you have called home.",
            "category": "relaxation"
        }
    },
    # Day 30 (index 25)
    {
        "theme": "Summit Sunrise Celebration & Grand Farewell",
        "morning": {
            "period": "Morning",
            "time": "06:00 AM – 09:30 AM",
            "title": "Sunrise Vista at Highest Regional Viewpoint",
            "location": "Summit Vista Point, {name}",
            "cost": 0,
            "explanation": "Greet dawn breaking over the land, celebrating 30 days of transformative travel.",
            "category": "nature"
        },
        "afternoon": {
            "period": "Afternoon",
            "time": "12:30 PM – 03:30 PM",
            "title": "Concluding 30-Day Celebratory Luncheon",
            "location": "Panoramic Restaurant, {name}",
            "cost": 450,
            "explanation": "Toast to 30 days of deep cultural discovery, restful days, and memorable hospitality.",
            "category": "food"
        },
        "evening": {
            "period": "Evening",
            "time": "05:00 PM – 07:30 PM",
            "title": "Twilight City Heart Farewell Promenade",
            "location": "City Heart, {name}",
            "cost": 0,
            "explanation": "Final farewell walk through warm streets as evening lanterns flicker to life.",
            "category": "relaxation"
        }
    }
]


def _generate_extended_days(
    dest_dict: Dict[str, Any],
    raw_style: str,
    start_day: int,
    end_day: int,
    is_verified: bool = True
) -> List[Dict[str, Any]]:
    """Generates non-duplicate, sensible extended days (up to Day 30) using destination context."""
    name = dest_dict.get("name", "Regional Hub")
    state = dest_dict.get("state", "India")
    generated = []

    slot_defaults = {
        "morning": {
            "duration": "3 hours",
            "transitNote": f"Start from base stay; ~20–30 min auto/cab to {name} outskirts activity site.",
            "practicalTips": f"Wear comfortable walking shoes and light cotton clothing. Carry water and sun protection.",
            "mealSuggestion": f"Begin with traditional breakfast specialties and hot filter coffee or chai near your stay in {name}."
        },
        "afternoon": {
            "duration": "2.5 hours",
            "transitNote": f"Sensible route pairing: ~10–15 min transfer from morning venue to lunch and afternoon activity in {name}.",
            "practicalTips": f"Midday can be sunny; carry sun protection and take your time over an unhurried regional lunch.",
            "mealSuggestion": f"Savor authentic regional thali with seasonal ingredients and traditional breads in {name}."
        },
        "evening": {
            "duration": "2.5 hours",
            "transitNote": f"Convenient ~15 min transfer to evening viewpoint or promenade; easy return to base accommodation.",
            "practicalTips": f"Evenings offer cooler breezes; carry a light layer and camera for golden hour photography.",
            "mealSuggestion": f"Enjoy evening street savories, regional confectionery, and fresh cutting chai in {name}."
        }
    }

    for day_num in range(start_day, end_day + 1):
        tpl_idx = (day_num - 5) % len(EXTENDED_DAY_TEMPLATES)
        tpl = EXTENDED_DAY_TEMPLATES[tpl_idx]

        theme = f"Day {day_num} • {tpl['theme']}"

        # Deep copy slots
        morning = deepcopy(tpl["morning"])
        afternoon = deepcopy(tpl["afternoon"])
        evening = deepcopy(tpl["evening"])

        # Format location, title, explanation with destination info
        for slot_key, slot in [("morning", morning), ("afternoon", afternoon), ("evening", evening)]:
            slot["location"] = slot["location"].format(name=name, state=state)
            slot["title"] = slot["title"].format(name=name, state=state)
            slot["explanation"] = slot["explanation"].format(name=name, state=state)
            defs = slot_defaults[slot_key]
            if "duration" not in slot or not slot["duration"]:
                slot["duration"] = defs["duration"]
            if "practicalTips" not in slot or not slot["practicalTips"]:
                slot["practicalTips"] = defs["practicalTips"]
            else:
                slot["practicalTips"] = slot["practicalTips"].format(name=name, state=state)
            if "mealSuggestion" not in slot or not slot["mealSuggestion"]:
                slot["mealSuggestion"] = defs["mealSuggestion"]
            else:
                slot["mealSuggestion"] = slot["mealSuggestion"].format(name=name, state=state)
            if "transitNote" not in slot or not slot["transitNote"]:
                slot["transitNote"] = defs["transitNote"]
            else:
                slot["transitNote"] = slot["transitNote"].format(name=name, state=state)
            slot["isCostEstimated"] = True

            if not is_verified:
                slot["cost"] = 0
                if not slot["title"].lower().startswith("independent"):
                    slot["title"] = f"Independent {slot['title']}"
                slot["explanation"] += " (Independent exploration; attraction details and costs are not fabricated)."
                slot["practicalTips"] = "Unverified destination: confirm local customs, dress guidelines, and opening timings locally; admission fees are not fabricated."
                slot["transitNote"] = "Estimated travel route; verify local taxi/auto availability and fares upon arrival."
                slot["mealSuggestion"] = f"Inquire with local guesthouse hosts or residents in {name} for authentic regional dining."

        generated.append({
            "dayNumber": day_num,
            "theme": theme,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening
        })

    return generated


def _build_curated_dynamic_itinerary(dest_dict: Dict[str, Any], raw_style: str, num_days: int) -> Dict[str, Any]:
    """Generates an authentic verified itinerary for curated destinations without pre-stored static templates."""
    name = dest_dict["name"]
    highlights = dest_dict.get("highlights", [])
    indicative_costs = dest_dict.get("indicativeDailyCost", {"budget": 2200, "balanced": 4500, "comfort": 8500})
    daily_budget = indicative_costs.get(raw_style, indicative_costs.get("balanced", 4500))

    # Base rates: stay (55%), food (25%), transit (20%)
    stay_rate = round(daily_budget * 0.55)
    food_rate = round(daily_budget * 0.25)
    transit_rate = round(daily_budget * 0.20)

    h0 = highlights[0] if len(highlights) > 0 else f"{name} Center Walk"
    h1 = highlights[1] if len(highlights) > 1 else f"{name} Cultural Landmark"
    h2 = highlights[2] if len(highlights) > 2 else f"{name} Scenic Viewpoint"
    h3 = highlights[3] if len(highlights) > 3 else f"{name} Traditional Market"

    all_days = [
        {
            "dayNumber": 1,
            "theme": f"Arrival & Signature {name} Highlights",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "duration": "3 hours",
                "title": f"{h0} Exploration",
                "location": f"{name}",
                "cost": 150,
                "isCostEstimated": True,
                "explanation": f"Explore {h0}, one of {name}'s quintessential regional highlights and architectural landmarks.",
                "practicalTips": f"Check opening hours for {h0} on arrival. Wear comfortable shoes suitable for walking and respect local photography guidelines.",
                "mealSuggestion": f"Pick up fresh regional breakfast snacks or hot chai from tea stalls near {h0}.",
                "transitNote": f"Depart from central {name}; convenient access via local auto-rickshaw or taxi (~15–20 min).",
                "category": "culture"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "duration": "2.5 hours",
                "title": f"Regional Dining & Market Walk",
                "location": f"Central {name}",
                "cost": 350,
                "isCostEstimated": True,
                "explanation": f"Savour authentic regional cuisine and browse indigenous handicrafts in {name}'s local market quarters.",
                "practicalTips": f"Bazaars around central {name} are vibrant; carry small cash denominations for handicrafts and street vendors.",
                "mealSuggestion": f"Sample authentic regional thali featuring traditional curries, fresh flatbreads, and indigenous sweets in {name}.",
                "transitNote": f"Sensible route pairing: located ~10 min from morning stop to avoid backtracking across the city.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "duration": "2.5 hours",
                "title": f"{h1} Experience",
                "location": f"{name}",
                "cost": 180,
                "isCostEstimated": True,
                "explanation": f"Visit {h1} during evening hours for atmospheric vistas and cultural heritage.",
                "practicalTips": f"Arrive at {h1} before sunset for optimal natural lighting and atmospheric evening views.",
                "mealSuggestion": f"Evening street-food stalls offer roasted corn, spicy savories, and hot beverage stalls along the promenade.",
                "transitNote": f"Short ~15 min auto ride from central market to {h1}; easy cab return to accommodation.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 2,
            "theme": f"Landmarks, Scenic Vistas & Craft Traditions",
            "morning": {
                "period": "Morning",
                "time": "08:30 AM – 11:30 AM",
                "duration": "3 hours",
                "title": f"{h2} Visit",
                "location": f"{name}",
                "cost": 200,
                "isCostEstimated": True,
                "explanation": f"Experience {h2}, enjoying panoramic views and guided regional background.",
                "practicalTips": f"Early morning start at {h2} provides cooler weather and unobstructed panoramic photography.",
                "mealSuggestion": f"Hydrate with fresh coconut water or fruit juice available near the trailhead/entrance.",
                "transitNote": f"~20–25 min direct ride from central {name} to {h2} overlook.",
                "category": "adventure"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "12:30 PM – 03:00 PM",
                "duration": "2.5 hours",
                "title": f"Traditional Lunch & Artisan Workshop",
                "location": f"Old Town, {name}",
                "cost": 300,
                "isCostEstimated": True,
                "explanation": f"Sample authentic culinary specialties and witness generational craft traditions.",
                "practicalTips": f"Support local generational artisans directly; workshops welcome polite observers and offer verified authentic crafts.",
                "mealSuggestion": f"Traditional lunch in Old Town {name} featuring generational recipes and slow-cooked local delicacies.",
                "transitNote": f"~15 min transit descending from the scenic viewpoint to the historic Old Town quarter.",
                "category": "culture"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 08:00 PM",
                "duration": "3 hours",
                "title": f"{h3} Sunset Stroll",
                "location": f"{name}",
                "cost": 120,
                "isCostEstimated": True,
                "explanation": f"Unwind at {h3} as dusk settles, enjoying ambient lighting and cool evening breezes.",
                "practicalTips": f"Relaxed sunset walk around {h3}; keep a light scarf or windbreaker handy as dusk temperatures cool.",
                "mealSuggestion": f"Taste local specialty tea or sweets from century-old shops around {h3}.",
                "transitNote": f"Direct walking distance or ~5 min auto within the Old Town perimeter.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 3,
            "theme": f"Nature Trails & Hidden Enclaves",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "duration": "3 hours",
                "title": f"Scenic Nature Trail & Viewpoints",
                "location": f"Outskirts of {name}",
                "cost": 100,
                "isCostEstimated": True,
                "explanation": f"Gentle morning trek or nature walk through regional flora, orchards, or heritage trails.",
                "practicalTips": f"Nature trails require sturdy grip shoes and sun protection. Stay on marked paths and respect protected flora.",
                "mealSuggestion": f"Carry energy snacks and water; pack local fruits for trail refreshments.",
                "transitNote": f"~25 min drive from town center to scenic outskirts nature area.",
                "category": "nature"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "duration": "2.5 hours",
                "title": f"Local Specialties & Culinary Souvenirs",
                "location": f"{name} Bazaars",
                "cost": 250,
                "isCostEstimated": True,
                "explanation": f"Pick up indigenous spices, teas, textiles, or craft keepsakes from verified local vendors.",
                "practicalTips": f"Browse certified spice, tea, or craft vendors. Ask for receipts and origin provenance for keepsake items.",
                "mealSuggestion": f"Sit-down lunch at a heritage cafe serving regional grain staples and spiced curries.",
                "transitNote": f"~20 min transfer from outskirts trail back towards the main market district.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:30 PM – 08:00 PM",
                "duration": "2.5 hours",
                "title": f"Promenade Leisure & Twilight Reflections",
                "location": f"Waterfront / Town Center, {name}",
                "cost": 0,
                "isCostEstimated": True,
                "explanation": f"Concluding evening with a relaxed stroll along the main promenade or town square.",
                "practicalTips": f"Promenade walk is family-friendly and illuminated; perfect for evening unwinding.",
                "mealSuggestion": f"Cafes and ice cream / sweet parlors bordering the waterfront.",
                "transitNote": f"Centrally situated along the town waterfront; walkable from nearby hotels.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 4,
            "theme": f"Deep Cultural Heritage & Farewell Walk",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "duration": "3 hours",
                "title": f"Historic Enclave & Temple Walk",
                "location": f"{name}",
                "cost": 150,
                "isCostEstimated": True,
                "explanation": f"Discover secluded shrines and colonial or princely architectural details.",
                "practicalTips": f"Temples and heritage shrines require shoe removal and modest attire covering knees and shoulders.",
                "mealSuggestion": f"Traditional temple prasad or fresh morning snacks at nearby heritage food stalls.",
                "transitNote": f"~15 min auto-rickshaw across the historic heritage quarter.",
                "category": "culture"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "duration": "2.5 hours",
                "title": f"Farewell Feast & Cafe Visit",
                "location": f"{name}",
                "cost": 400,
                "isCostEstimated": True,
                "explanation": f"A memorable farewell lunch featuring multi-course regional recipes.",
                "practicalTips": f"Reserve your table in advance for a leisurely farewell dining experience.",
                "mealSuggestion": f"Elaborate multi-course celebratory regional feast showcasing the full range of {name}'s culinary heritage.",
                "transitNote": f"Located in {name}'s premier dining district; 10 min cab from heritage precinct.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "duration": "2.5 hours",
                "title": f"Sunset Panorama & Departure Preparation",
                "location": f"Sunset Point, {name}",
                "cost": 0,
                "isCostEstimated": True,
                "explanation": f"Final sunset vistas over the valley, coast, or cityscape.",
                "practicalTips": f"Final sunset vista; allow ample time to pack and verify tomorrow's departure arrangements.",
                "mealSuggestion": f"Sunset chai, fresh baked biscuits, and savory appetizers.",
                "transitNote": f"Scenic hilltop or lake overlook; ~20 min ride from dining district.",
                "category": "nature"
            }
        }
    ]

    if num_days <= len(all_days):
        selected_days = all_days[:num_days]
    else:
        extended = _generate_extended_days(dest_dict, raw_style, start_day=len(all_days) + 1, end_day=num_days, is_verified=True)
        selected_days = all_days + extended

    return {
        "title": f"{name}: {num_days}-Day Curated Journey" if num_days > 4 else f"{name}: Curated Discovery & Cultural Trail",
        "summary": f"A {num_days}-day itinerary exploring {name}'s verified highlights, regional hospitality, and distinctive heritage.",
        "baseDailyRates": {
            raw_style: {"stay": stay_rate, "food": food_rate, "transit": transit_rate}
        },
        "days": selected_days
    }


def _build_unverified_custom_plan(custom_name: str, raw_style: str, num_days: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Constructs an unverified plan for manually entered destinations up to 30 days.
    Strictly avoids fabricating attraction details, ticket fees, or travel distances.
    Uses standard national benchmark averages and varied non-duplicate day themes.
    """
    clean_name = custom_name.strip().title()
    dest_dict = {
        "id": "custom",
        "name": clean_name,
        "state": "India (Manual Entry)",
        "tagline": "Independent exploration with baseline travel benchmarks",
        "description": (
            f"This destination was manually entered and is not part of the verified regional benchmarks dataset. "
            f"Planning estimates use standard national baseline averages; specific attractions, travel distances, and entry tickets are not fabricated."
        ),
        "image": "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?auto=format&fit=crop&w=1000&q=80",
        "fallbackImage": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1000&q=80",
        "indicativeDailyCost": {
            "budget": 2000,
            "balanced": 4200,
            "comfort": 8000
        },
        "indicativeRange": "₹3,000 – ₹5,500 / day (Indicative Baseline)",
        "bestTimeToVisit": "Check local weather advisory",
        "primaryInterests": ["nature", "culture", "relaxation"],
        "highlights": [
            "Self-guided neighborhood & market walk",
            "Regional culinary discovery",
            "Independent sightseeing at your own pace",
            "Flexible daily exploration"
        ]
    }

    style_rates = {
        "budget": {"stay": 1100, "food": 550, "transit": 350},
        "balanced": {"stay": 2400, "food": 1050, "transit": 750},
        "comfort": {"stay": 5000, "food": 1900, "transit": 1500},
    }
    rates = style_rates.get(raw_style, style_rates["balanced"])

    # Initial 4 core days for unverified destinations
    core_unverified_days = [
        {
            "dayNumber": 1,
            "theme": f"Arrival & Area Orientation in {clean_name}",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "title": "Town Arrival & Central Area Orientation",
                "location": f"Central {clean_name}",
                "cost": 0,
                "explanation": f"Independent morning arrival and orientation in {clean_name}. Attractions and entrance fees are not fabricated for unverified locations.",
                "category": "culture"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "title": "Local Market & Food Quarter Discovery",
                "location": f"Market Lanes, {clean_name}",
                "cost": 0,
                "explanation": f"Independent exploration of central market lanes and casual dining at your own pace.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "title": "Town Square Twilight Stroll",
                "location": f"Promenade, {clean_name}",
                "cost": 0,
                "explanation": f"Relaxed evening walk observing local sunset ambiance without fabricated activities.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 2,
            "theme": f"Regional Heritage & Old Quarter Exploration",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "title": "Old Town Walk & Architectural Scenery",
                "location": f"Old Quarter, {clean_name}",
                "cost": 0,
                "explanation": f"Self-guided morning walk admiring regional architectural styles and historic neighborhood layout.",
                "category": "culture"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "title": "Traditional Cuisine at Local Eatery",
                "location": f"Local Eateries, {clean_name}",
                "cost": 0,
                "explanation": f"Sample authentic regional cooking at locally popular eateries without fabricated attraction costs.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "title": "Viewpoint Walk & Sunset Watch",
                "location": f"Scenic Overlook, {clean_name}",
                "cost": 0,
                "explanation": f"Walk to an elevated viewpoint or town park to watch the evening sunset.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 3,
            "theme": f"Natural Landscapes & Surrounding Scenery",
            "morning": {
                "period": "Morning",
                "time": "08:30 AM – 11:30 AM",
                "title": "Morning Scenery & Nature Exploration",
                "location": f"Outskirts of {clean_name}",
                "cost": 0,
                "explanation": f"Gentle morning exploration of regional natural surroundings, orchards, or rural trails.",
                "category": "nature"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "12:30 PM – 03:00 PM",
                "title": "Picnic Lunch or Neighborhood Café",
                "location": f"Café / Shaded Grove, {clean_name}",
                "cost": 0,
                "explanation": f"Independent lunch break at a neighborhood café or outdoor shaded park.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "title": "Waterside Promenade or Park Walk",
                "location": f"Public Gardens, {clean_name}",
                "cost": 0,
                "explanation": f"Enjoy a calm evening stroll through local gardens or waterfront avenues.",
                "category": "relaxation"
            }
        },
        {
            "dayNumber": 4,
            "theme": f"Artisan Quarters & Local Living",
            "morning": {
                "period": "Morning",
                "time": "09:00 AM – 12:00 PM",
                "title": "Local Craft Lanes & Guild Workshops",
                "location": f"Artisan Enclave, {clean_name}",
                "cost": 0,
                "explanation": f"Observe regional craft traditions, small family workshops, and handloom or pottery stores.",
                "category": "culture"
            },
            "afternoon": {
                "period": "Afternoon",
                "time": "01:00 PM – 03:30 PM",
                "title": "Neighborhood Specialty Tasting",
                "location": f"Town Bazaars, {clean_name}",
                "cost": 0,
                "explanation": f"Independent sampling of local street delicacies and regional tea.",
                "category": "food"
            },
            "evening": {
                "period": "Evening",
                "time": "05:00 PM – 07:30 PM",
                "title": "Breezy Dusk Promenade",
                "location": f"Town Square, {clean_name}",
                "cost": 0,
                "explanation": f"Concluding evening walk savoring the local neighborhood atmosphere.",
                "category": "relaxation"
            }
        }
    ]

    for day_obj in core_unverified_days:
        for slot_key in ["morning", "afternoon", "evening"]:
            s = day_obj[slot_key]
            s["cost"] = 0
            s["isCostEstimated"] = True
            if "duration" not in s or not s["duration"]:
                s["duration"] = "3 hours" if slot_key == "morning" else "2.5 hours"
            if "practicalTips" not in s or not s["practicalTips"]:
                s["practicalTips"] = "Unverified destination: confirm local customs, dress guidelines, and opening timings locally; admission fees are not fabricated."
            if "mealSuggestion" not in s or not s["mealSuggestion"]:
                s["mealSuggestion"] = f"Inquire with local guesthouse hosts or residents in {clean_name} for authentic regional dining."
            if "transitNote" not in s or not s["transitNote"]:
                s["transitNote"] = "Estimated travel route; verify local taxi/auto availability and fares upon arrival."
            if "not fabricated" not in s["explanation"].lower():
                s["explanation"] += " (Attraction details and costs are not fabricated for unverified locations)."

    if num_days <= len(core_unverified_days):
        selected_days = core_unverified_days[:num_days]
    else:
        extended = _generate_extended_days(dest_dict, raw_style, start_day=len(core_unverified_days) + 1, end_day=num_days, is_verified=False)
        selected_days = core_unverified_days + extended

    itin_data = {
        "title": f"{clean_name}: {num_days}-Day Independent Plan",
        "summary": (
            f"A {num_days}-day planning baseline for {clean_name}. "
            f"Information is limited because verified regional benchmarks are not on file. "
            f"Standard national hospitality rates have been applied without fabricated attraction fees."
        ),
        "baseDailyRates": {raw_style: rates},
        "days": selected_days
    }

    return dest_dict, itin_data


def calculate_trip_plan(
    starting_city: str,
    destination_id: str,
    days: int,
    budget: float,
    interests: List[str],
    travel_style: str = "balanced",
    budget_optimized: bool = False,
    custom_destination_name: Optional[str] = None,
    is_custom_destination: bool = False
) -> TripPlanResponse:
    """
    Core deterministic planning engine.
    Calculates itemized costs for stay, food, transit, and experiences for 1 to 30 days.
    Guarantees strict mathematical integrity:
      total_estimated_cost = accommodation_cost + food_cost + transport_cost + activities_cost
      remaining_budget = user_budget - total_estimated_cost
    """
    raw_style = travel_style.lower() if isinstance(travel_style, str) else travel_style.value
    if raw_style not in ["budget", "balanced", "comfort"]:
        raw_style = "balanced"

    clean_dest_id = destination_id.strip().lower()
    is_verified = True
    dest_dict = None

    num_days = max(1, min(days, 30))

    # Handle manual / custom destination entry
    if is_custom_destination or clean_dest_id == "custom" or (custom_destination_name and custom_destination_name.strip()):
        custom_name = (custom_destination_name or destination_id).strip()
        matched = get_destination_by_id(custom_name)
        if matched:
            dest_dict = matched
            clean_dest_id = matched["id"]
        else:
            dest_dict, itinerary_data = _build_unverified_custom_plan(custom_name, raw_style, num_days)
            is_verified = False

    if is_verified and not dest_dict:
        dest_dict = get_destination_by_id(clean_dest_id)
        if not dest_dict:
            raise ValueError(f"Unknown destination identifier: '{destination_id}'")

    # Determine itinerary data
    if is_verified:
        if clean_dest_id in SAMPLE_ITINERARIES:
            base_itin = SAMPLE_ITINERARIES[clean_dest_id]
            base_days = deepcopy(base_itin["days"])
            if num_days <= len(base_days):
                chosen_days = base_days[:num_days]
            else:
                extra = _generate_extended_days(dest_dict, raw_style, start_day=len(base_days) + 1, end_day=num_days, is_verified=True)
                chosen_days = base_days + extra

            itinerary_data = {
                "title": base_itin["title"] if num_days <= 4 else f"{dest_dict['name']}: {num_days}-Day Curated Journey",
                "summary": base_itin["summary"] if num_days <= 4 else f"A {num_days}-day itinerary exploring {dest_dict['name']}'s signature highlights, scenic regional outskirts, and authentic cultural living.",
                "baseDailyRates": base_itin["baseDailyRates"],
                "days": chosen_days
            }
        else:
            itinerary_data = _build_curated_dynamic_itinerary(dest_dict, raw_style, num_days)

    raw_active_days = deepcopy(itinerary_data["days"][:num_days])

    # 1. Activities Cost calculation
    raw_activities_cost = 0
    for day in raw_active_days:
        raw_activities_cost += day["morning"].get("cost", 0)
        raw_activities_cost += day["afternoon"].get("cost", 0)
        raw_activities_cost += day["evening"].get("cost", 0)

    if budget_optimized:
        # Reflect optimized costs in the day activity models
        for day in raw_active_days:
            for slot in ["morning", "afternoon", "evening"]:
                slot_data = day[slot]
                if slot_data.get("cost", 0) > 0:
                    slot_data["cost"] = round(slot_data["cost"] * 0.85)

    # Calculate actual sum of slot costs
    activities_cost = sum(
        day[slot].get("cost", 0)
        for day in raw_active_days
        for slot in ["morning", "afternoon", "evening"]
    )

    # 2. Base daily rates for accommodation, food, transit
    base_rates = itinerary_data["baseDailyRates"].get(raw_style)
    if not base_rates:
        base_rates = list(itinerary_data["baseDailyRates"].values())[0]

    daily_stay = base_rates["stay"]
    daily_food = base_rates["food"]
    daily_transit = base_rates["transit"]

    if budget_optimized:
        # Economy homestays (-25%), community dining (-20%), public metro/autos (-25%)
        daily_stay = round(daily_stay * 0.75)
        daily_food = round(daily_food * 0.80)
        daily_transit = round(daily_transit * 0.75)

    # Calculate daily breakdowns ensuring exact mathematical consistency
    for day in raw_active_days:
        day_act_sum = sum(day[slot].get("cost", 0) for slot in ["morning", "afternoon", "evening"])
        day["dayStay"] = daily_stay
        day["dayFood"] = daily_food
        day["dayTransit"] = daily_transit
        day["dayActivities"] = day_act_sum
        day["dayTotal"] = daily_stay + daily_food + daily_transit + day_act_sum
        day["isCostVerified"] = is_verified

        # Phase 6.3: Build route segments with road routing or Haversine fallback
        route_segs = build_day_route_segments(day)
        day["routeSegments"] = [seg.model_dump(by_alias=True) for seg in route_segs]
        calc_dists = [seg.distance_km for seg in route_segs if seg.is_route_calculated and seg.distance_km is not None]
        day["dayRouteDistanceKm"] = round(sum(calc_dists), 1) if calc_dists else None
        day["hasRoadRoutes"] = any(seg.route_type == "road" for seg in route_segs)

    # Calculate aggregate route distance across all active days
    all_day_dists = [d["dayRouteDistanceKm"] for d in raw_active_days if d.get("dayRouteDistanceKm") is not None]
    total_route_distance_km = round(sum(all_day_dists), 1) if all_day_dists else None
    has_road_routes_trip = any(d.get("hasRoadRoutes") for d in raw_active_days)
    route_provider = "osrm" if has_road_routes_trip else None

    accommodation_cost = daily_stay * num_days
    food_cost = daily_food * num_days
    transport_cost = daily_transit * num_days

    total_estimated_cost = accommodation_cost + food_cost + transport_cost + activities_cost
    remaining_budget = budget - total_estimated_cost
    is_over_budget = remaining_budget < 0
    deficit = abs(remaining_budget) if is_over_budget else 0.0

    disclaimer_text = (
        "Sample Itinerary & Deterministic Pricing: Displaying verified regional benchmarks. Phase 3 will introduce adaptive multi-agent reasoning with Strands Decider 2B and Amazon Bedrock."
        if is_verified
        else "Limited Information Notice: Verified regional benchmarks are not on file for this manually entered location. Daily estimates use national baseline averages without fabricated attractions or costs."
    )

    map_center = dest_dict.get("centerCoordinates") or dest_dict.get("center_coordinates")

    return TripPlanResponse(
        destination=Destination.model_validate(dest_dict),
        starting_city=starting_city,
        itinerary_title=itinerary_data["title"],
        itinerary_summary=itinerary_data["summary"],
        num_days=num_days,
        active_days=raw_active_days,
        travel_style=raw_style,
        budget_optimized=budget_optimized,
        daily_stay=daily_stay,
        daily_food=daily_food,
        daily_transit=daily_transit,
        accommodation_cost=accommodation_cost,
        food_cost=food_cost,
        transport_cost=transport_cost,
        activities_cost=activities_cost,
        total_estimated_cost=total_estimated_cost,
        user_budget=budget,
        remaining_budget=remaining_budget,
        is_over_budget=is_over_budget,
        deficit=deficit,
        is_verified=is_verified,
        is_sample=True,
        disclaimer=disclaimer_text,
        map_center=map_center,
        total_route_distance_km=total_route_distance_km,
        route_provider=route_provider,
        has_road_routes=has_road_routes_trip
    )


def create_trip_plan(plan_req: TripPlanRequest) -> TripPlanResponse:
    """Wrapper to create a trip plan from a validated request model."""
    return calculate_trip_plan(
        starting_city=plan_req.starting_city,
        destination_id=plan_req.destination_id,
        days=plan_req.days,
        budget=plan_req.budget,
        interests=plan_req.interests,
        travel_style=plan_req.travel_style.value if isinstance(plan_req.travel_style, TravelStyleEnum) else plan_req.travel_style,
        budget_optimized=plan_req.budget_optimized,
        custom_destination_name=plan_req.custom_destination_name,
        is_custom_destination=plan_req.is_custom_destination
    )


def adapt_trip_plan(adapt_req: AdaptTripRequest) -> TripPlanResponse:
    """
    Applies adaptive planning actions deterministically:
    - reduce_budget: Toggles or activates budget economy rates
    - shorten_trip: Reduces trip days by 1 (minimum 1 day)
    - change_travel_style: Recalibrates accommodation & transit to target style
    """
    action = adapt_req.action.strip().lower()
    base_plan = adapt_req.plan_request

    # Create mutable copy of parameters
    starting_city = base_plan.starting_city
    destination_id = base_plan.destination_id
    custom_destination_name = base_plan.custom_destination_name
    is_custom_destination = base_plan.is_custom_destination
    days = base_plan.days
    budget = base_plan.budget
    interests = base_plan.interests
    travel_style = base_plan.travel_style.value if isinstance(base_plan.travel_style, TravelStyleEnum) else base_plan.travel_style
    budget_optimized = base_plan.budget_optimized

    if action == AdaptActionEnum.REDUCE_BUDGET.value:
        # Toggle or enable budget optimization
        budget_optimized = not budget_optimized

    elif action == AdaptActionEnum.SHORTEN_TRIP.value:
        if days <= 1:
            raise ValueError("Cannot shorten trip below the 1-day minimum duration.")
        days = max(1, days - 1)

    elif action == AdaptActionEnum.CHANGE_TRAVEL_STYLE.value:
        if not adapt_req.new_travel_style:
            raise ValueError("Field 'newTravelStyle' is required when action is 'change_travel_style'.")
        new_style = adapt_req.new_travel_style.strip().lower()
        if new_style not in ["budget", "balanced", "comfort"]:
            raise ValueError(f"Invalid travel style: '{adapt_req.new_travel_style}'. Must be one of: budget, balanced, comfort.")
        travel_style = new_style

    else:
        raise ValueError(
            f"Unsupported adaptation action '{adapt_req.action}'. "
            f"Supported actions are: {', '.join([a.value for a in AdaptActionEnum])}."
        )

    return calculate_trip_plan(
        starting_city=starting_city,
        destination_id=destination_id,
        days=days,
        budget=budget,
        interests=interests,
        travel_style=travel_style,
        budget_optimized=budget_optimized,
        custom_destination_name=custom_destination_name,
        is_custom_destination=is_custom_destination
    )
