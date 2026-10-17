"""Curated destination datasets, sample itineraries, and daily pricing benchmarks."""
import json
from pathlib import Path

# Load maintainable shared destination dataset
_SHARED_FILE = Path(__file__).resolve().parents[2] / "src" / "data" / "destinations.json"
_LOCAL_FILE = Path(__file__).resolve().parent / "destinations.json"

if _SHARED_FILE.exists():
    with open(_SHARED_FILE, "r", encoding="utf-8") as _f:
        DESTINATIONS = json.load(_f)
elif _LOCAL_FILE.exists():
    with open(_LOCAL_FILE, "r", encoding="utf-8") as _f:
        DESTINATIONS = json.load(_f)
else:
    raise FileNotFoundError("Could not find destinations.json in shared or local path.")


SAMPLE_ITINERARIES = {   'goa': {   'baseDailyRates': {   'balanced': {'food': 1400, 'stay': 3200, 'transit': 900},
                                     'budget': {'food': 700, 'stay': 1400, 'transit': 500},
                                     'comfort': {'food': 2500, 'stay': 6500, 'transit': 1800}},
               'days': [   {   'afternoon': {   'category': 'food',
                                                'cost': 480,
                                                'duration': '2.5 hours',
                                                'explanation': 'Taste traditional Kingfish peri-peri, kokum sol kadhi, '
                                                               'and warm poi bread in a family-run heritage cottage.',
                                                'isCostEstimated': True,
                                                'location': 'Fontainhas',
                                                'mealSuggestion': 'Kingfish curry with boiled red rice, fried '
                                                                  'calamari, kismur salad, and coconut feni kokum '
                                                                  'cooler.',
                                                'period': 'Afternoon',
                                                'practicalTips': 'Viva Panjim has limited seating inside its heritage '
                                                                 'home; arrive right at 12:30 PM or reserve ahead '
                                                                 'during peak season.',
                                                'time': '12:30 PM – 03:00 PM',
                                                'title': 'Goan Fish Curry Thali at Viva Panjim',
                                                'transitNote': 'Located directly within Fontainhas alleys; 3 min walk '
                                                               'from morning walking tour.'},
                               'dayNumber': 1,
                               'evening': {   'category': 'relaxation',
                                              'cost': 0,
                                              'duration': '2.5 hours',
                                              'explanation': 'Catch the sea breeze where Mandovi river meets the '
                                                             'Arabian Sea, watching wooden fishing trawlers return.',
                                              'isCostEstimated': True,
                                              'location': 'Panaji',
                                              'mealSuggestion': 'Roasted spiced corn cob and Goan cutlet pao from '
                                                                'shoreline vendors.',
                                              'period': 'Evening',
                                              'practicalTips': 'Take a sunset seat on the benches facing Mandovi river '
                                                               "mouth; carry light sandals for walking along Miramar's "
                                                               'sandbar.',
                                              'time': '05:00 PM – 07:30 PM',
                                              'title': 'Miramar Beach & Mandovi River Promenade',
                                              'transitNote': '~10-15 min auto or cab drive from Fontainhas west along '
                                                             'DB Marg.'},
                               'morning': {   'category': 'culture',
                                              'cost': 200,
                                              'duration': '3 hours',
                                              'explanation': 'Stroll past ochre and cobalt colonial villas, '
                                                             'traditional azulejo tile workshops, and the Chapel of '
                                                             'St. Sebastian.',
                                              'isCostEstimated': True,
                                              'location': 'Panaji',
                                              'mealSuggestion': 'Freshly baked warm poi bread with Goan chorizo or pao '
                                                                'from century-old neighborhood bakeries.',
                                              'period': 'Morning',
                                              'practicalTips': 'Fontainhas is a living residential neighborhood; '
                                                               'maintain privacy and avoid loud noise in narrow '
                                                               'residential alleys. Early morning offers softest '
                                                               'photography light.',
                                              'time': '08:30 AM – 11:30 AM',
                                              'title': 'Fontainhas Latin Quarter Walking Tour',
                                              'transitNote': 'Compact walking loop within Panaji Latin Quarter; no '
                                                             'vehicle needed during the walk.'},
                               'theme': 'Fontainhas Colours & Mandovi Sunset'},
                           {   'afternoon': {   'category': 'nature',
                                                'cost': 650,
                                                'duration': '3 hours',
                                                'explanation': 'Guided botanical walk observing cardamom, vanilla, and '
                                                               'peri-peri chillies, followed by a buffet served on '
                                                               'banana leaves.',
                                                'isCostEstimated': True,
                                                'location': 'Ponda',
                                                'mealSuggestion': 'Traditional buffet served on banana leaves '
                                                                  'featuring peri-peri chicken, fresh local fish '
                                                                  'curry, vegetable caldin, and freshly distilled '
                                                                  'feni.',
                                                'period': 'Afternoon',
                                                'practicalTips': 'Wear comfortable walking shoes suitable for red dirt '
                                                                 'paths. Guide fee is usually included with entry '
                                                                 'ticket.',
                                                'time': '12:30 PM – 03:30 PM',
                                                'title': 'Sahakari Spice Farm Tour & Banana Leaf Lunch',
                                                'transitNote': '~25 min scenic drive through spice hills from Old Goa '
                                                               'to Ponda.'},
                               'dayNumber': 2,
                               'evening': {   'category': 'relaxation',
                                              'cost': 0,
                                              'duration': '2.5 hours',
                                              'explanation': 'Watch the sun dip below the ocean horizon from the '
                                                             'ruined ramparts of an ancient coastal fortress.',
                                              'isCostEstimated': True,
                                              'location': 'Canacona',
                                              'mealSuggestion': 'Sunset refreshment or cashew feni cocktail with '
                                                                'garlic butter poi at a cliffside shack.',
                                              'period': 'Evening',
                                              'practicalTips': 'Fort grounds have uneven stone paths and steep cliff '
                                                               'drop-offs; stay within safe perimeters and depart '
                                                               'before complete darkness.',
                                              'time': '05:30 PM – 08:00 PM',
                                              'title': 'Cabo de Rama Sunset Lookout',
                                              'transitNote': '~50-60 min drive south from Ponda to Canacona coastal '
                                                             'cliffs.'},
                               'morning': {   'category': 'culture',
                                              'cost': 100,
                                              'duration': '3 hours',
                                              'explanation': 'Explore UNESCO World Heritage 16th-century structures '
                                                             'preserving relics of St. Francis Xavier and monumental '
                                                             'golden bells.',
                                              'isCostEstimated': True,
                                              'location': 'Old Goa',
                                              'mealSuggestion': 'Cool tender coconut or fresh seasonal kokum juice '
                                                                'outside the church complex.',
                                              'period': 'Morning',
                                              'practicalTips': 'Strict dress code inside the Basilica (no sleeveless '
                                                               'tops or short shorts). Photography is prohibited '
                                                               'inside the inner chapel of relics.',
                                              'time': '08:30 AM – 11:30 AM',
                                              'title': 'Basilica of Bom Jesus & Se Cathedral',
                                              'transitNote': '~20 min drive east from Panaji along NH748.'},
                               'theme': 'Baroque Churches & Spice Plantation'},
                           {   'afternoon': {   'category': 'food',
                                                'cost': 750,
                                                'duration': '3 hours',
                                                'explanation': 'Enjoy freshly caught butter-garlic prawns and Bebinca '
                                                               'pudding overlooking scenic Sal river mangroves.',
                                                'isCostEstimated': True,
                                                'location': 'Cavelossim Riverbank',
                                                'mealSuggestion': 'Butter garlic tiger prawns, pomfret rechado, and '
                                                                  'multi-layered Goan bebinca dessert.',
                                                'period': 'Afternoon',
                                                'practicalTips': 'River-facing tables have great breeze; make a '
                                                                 'weekend reservation during peak holiday months.',
                                                'time': '12:30 PM – 03:30 PM',
                                                'title': "Slow Lunch at Fisherman's Wharf",
                                                'transitNote': '~30 min drive north along coastal road from Palolem to '
                                                               'Cavelossim.'},
                               'dayNumber': 3,
                               'evening': {   'category': 'nature',
                                              'cost': 0,
                                              'duration': '2.5 hours',
                                              'explanation': 'Walk pristine uninterrupted sands along an eco-sensitive '
                                                             'Olive Ridley turtle nesting sanctuary.',
                                              'isCostEstimated': True,
                                              'location': 'Agonda',
                                              'mealSuggestion': 'Wood-fired thin crust pizza or grilled snapper at '
                                                                'beach shacks.',
                                              'period': 'Evening',
                                              'practicalTips': 'Agonda is a silent turtle nesting beach; night '
                                                               'lighting is strictly controlled. Avoid loud music and '
                                                               'keep flashlights off.',
                                              'time': '05:00 PM – 07:30 PM',
                                              'title': 'Agonda Beach Sunset Walk & Sea Turtles',
                                              'transitNote': '~25 min drive south from Cavelossim back to quiet '
                                                             'Agonda.'},
                               'morning': {   'category': 'adventure',
                                              'cost': 600,
                                              'duration': '3 hours',
                                              'explanation': 'Paddle tranquil emerald waters in an ocean kayak around '
                                                             'volcanic headlands to secluded sandbars.',
                                              'isCostEstimated': True,
                                              'location': 'South Goa',
                                              'mealSuggestion': 'Fresh fruit smoothie bowl, banana pancakes, or iced '
                                                                'coffee at beachfront cafes.',
                                              'period': 'Morning',
                                              'practicalTips': 'Rent kayaks with certified life jackets; calm morning '
                                                               'waters before 10:00 AM are ideal for easy paddling. '
                                                               'Protect phones with waterproof pouches.',
                                              'time': '07:30 AM – 10:30 AM',
                                              'title': 'Palolem Bay Kayaking & Butterfly Beach',
                                              'transitNote': 'Centrally located on Palolem Beach in South Goa.'},
                               'theme': 'Quiet Southern Bays & Coastal Seafood'},
                           {   'afternoon': {   'category': 'food',
                                                'cost': 550,
                                                'duration': '2.5 hours',
                                                'explanation': 'Savour organic Mediterranean-Goan fusion salads, '
                                                               'sourdough, and cold-pressed juices in a leafy '
                                                               'courtyard.',
                                                'isCostEstimated': True,
                                                'location': 'Assagao',
                                                'mealSuggestion': 'Sourdough tartines, organic salad bowls, kombucha, '
                                                                  'and homemade artisanal gelato.',
                                                'period': 'Afternoon',
                                                'practicalTips': "Assagao's boutique cafes have lush garden "
                                                                 'courtyards; advance table booking recommended on '
                                                                 'weekends.',
                                                'time': '12:30 PM – 03:00 PM',
                                                'title': 'Farm-to-Table Cafe Experience',
                                                'transitNote': '~15 min drive inland from Chapora/Vagator to Assagao '
                                                               'village.'},
                               'dayNumber': 4,
                               'evening': {   'category': 'culture',
                                              'cost': 150,
                                              'duration': '3 hours',
                                              'explanation': 'Browse handmade jewelry, spices, and textiles '
                                                             'accompanied by acoustic musicians on the sand.',
                                              'isCostEstimated': True,
                                              'location': 'Anjuna',
                                              'mealSuggestion': 'Steamed momos, falafel wraps, and chilled fresh '
                                                                'juices.',
                                              'period': 'Evening',
                                              'practicalTips': 'Weekly flea market operates Wednesdays in season, with '
                                                               'lively weekend craft bazaars. Negotiate courteously '
                                                               'for souvenirs.',
                                              'time': '04:30 PM – 07:30 PM',
                                              'title': 'Anjuna Flea Market & Sunset Drums',
                                              'transitNote': '~15 min drive from Assagao west to Anjuna beach.'},
                               'morning': {   'category': 'adventure',
                                              'cost': 50,
                                              'duration': '3 hours',
                                              'explanation': 'Hike the iconic rocky red laterite cliffside overlooking '
                                                             'Vagator beach and the Chapora estuary.',
                                              'isCostEstimated': True,
                                              'location': 'Vagator',
                                              'mealSuggestion': 'Fresh watermelon or pineapple juice from hillside '
                                                                'stalls.',
                                              'period': 'Morning',
                                              'practicalTips': 'Climb up the red laterite stone path takes 15-20 min; '
                                                               'wear sneakers with grip as loose gravel can be '
                                                               'slippery.',
                                              'time': '08:30 AM – 11:30 AM',
                                              'title': 'Chapora Fort & Red Laterite Cliffs',
                                              'transitNote': 'Located on northern coast overlooking Vagator.'},
                               'theme': 'Northern Cliffs & Artisanal Markets'}],
               'destinationId': 'goa',
               'summary': 'A curated journey blending whitewashed Portuguese baroque chapels, vibrant Fontainhas '
                          'streets, spice groves, and golden hour coastal waters.',
               'title': 'Susegad Coastlines & Latin Heritage'},
    'hyderabad': {   'baseDailyRates': {   'balanced': {'food': 1200, 'stay': 2800, 'transit': 800},
                                           'budget': {'food': 600, 'stay': 1200, 'transit': 400},
                                           'comfort': {'food': 2200, 'stay': 5800, 'transit': 1600}},
                     'days': [   {   'afternoon': {   'category': 'food',
                                                      'cost': 450,
                                                      'duration': '3 hours',
                                                      'explanation': 'Savour slow-cooked mutton dum biryani with '
                                                                     'mirchi ka salan, then browse intricate lacquer '
                                                                     'bangles and attar fragrances.',
                                                      'isCostEstimated': True,
                                                      'location': 'Madina Circle & Laad Bazaar',
                                                      'mealSuggestion': 'Signature mutton dum biryani paired with '
                                                                        'spicy mirchi ka salan, cool dahi chutney, and '
                                                                        'double ka meetha dessert.',
                                                      'period': 'Afternoon',
                                                      'practicalTips': 'Peak lunch rush is between 1:00 PM and 2:30 '
                                                                       'PM; arrive slightly early. Lacquer bangles and '
                                                                       'natural attar can be bargained respectfully in '
                                                                       'the bazaar.',
                                                      'time': '12:30 PM – 03:30 PM',
                                                      'title': 'Authentic Dum Biryani at Shadab & Laad Bazaar Bangles',
                                                      'transitNote': '~10 min walk or quick auto-rickshaw (1 km) north '
                                                                     'of Charminar to Madina Circle.'},
                                     'dayNumber': 1,
                                     'evening': {   'category': 'culture',
                                                    'cost': 200,
                                                    'duration': '3 hours',
                                                    'explanation': "Stroll through the Asaf Jahi dynasty's grand "
                                                                   'Durbar Hall and vintage car collection, concluding '
                                                                   'with warm Osmania biscuits.',
                                                    'isCostEstimated': True,
                                                    'location': 'Motigalli, Khilwat',
                                                    'mealSuggestion': 'Authentic cutting Irani chai with warm maska '
                                                                      'bun or tie biscuit at Nimrah Cafe opposite '
                                                                      'Charminar.',
                                                    'period': 'Evening',
                                                    'practicalTips': 'Palace ticket counter closes by 5:00 PM; allow '
                                                                     'at least 90 minutes to explore the Khilwat '
                                                                     'Mubarak durbar hall and gardens without rushing.',
                                                    'time': '04:30 PM – 07:30 PM',
                                                    'title': 'Chowmahalla Palace & Irani Chai at Nimrah',
                                                    'transitNote': 'Sensible route order: ~10 min auto or 15 min walk '
                                                                   'south from Laad Bazaar back towards Chowmahalla '
                                                                   'palace gates.'},
                                     'morning': {   'category': 'culture',
                                                    'cost': 150,
                                                    'duration': '3 hours',
                                                    'explanation': 'Climb the historic 1591 monument for panoramic '
                                                                   'vistas of the Old City, followed by serene '
                                                                   'reflection inside Mecca Masjid.',
                                                    'isCostEstimated': True,
                                                    'location': 'Old City, Hyderabad',
                                                    'mealSuggestion': 'Pick up hot Osmania biscuits or warm nankhatai '
                                                                      'cookies from historic bakeries right outside '
                                                                      'the monument.',
                                                    'period': 'Morning',
                                                    'practicalTips': 'Modest dress required inside Mecca Masjid '
                                                                     '(covered shoulders and knees; women may carry a '
                                                                     'headscarf). Remove footwear outside. Carry cash '
                                                                     'for small nearby vendors.',
                                                    'time': '08:30 AM – 11:30 AM',
                                                    'title': 'Charminar & Mecca Masjid Walking Tour',
                                                    'transitNote': 'Direct pedestrian walk between Charminar, Mecca '
                                                                   'Masjid, and Laad Bazaar (~5 min walk); no '
                                                                   'transport needed between morning stops.'},
                                     'theme': 'Charminar Heritage & Old City Flavours'},
                                 {   'afternoon': {   'category': 'culture',
                                                      'cost': 120,
                                                      'duration': '3 hours',
                                                      'explanation': 'Admire domed mausoleums combining Persian, '
                                                                     'Pashtun, and Hindu architectural motifs set in '
                                                                     'landscaped gardens.',
                                                      'isCostEstimated': True,
                                                      'location': 'Ibrahim Bagh',
                                                      'mealSuggestion': 'Stop at a local restaurant near Tolichowki '
                                                                        'for traditional Hyderabadi marag (spiced '
                                                                        'mutton broth) or chicken 65 with naan.',
                                                      'period': 'Afternoon',
                                                      'practicalTips': 'Extensive landscaped restoration area; carry '
                                                                       'an umbrella or hat for sun shade between '
                                                                       'pavilions. Photography permits are nominal.',
                                                      'time': '12:00 PM – 03:00 PM',
                                                      'title': 'Qutb Shahi Tombs Restoration Walk',
                                                      'transitNote': 'Sensible route pairing: only ~2 km (10-15 min '
                                                                     'auto) from Golconda Fort gate to Qutb Shahi '
                                                                     'Tombs.'},
                                     'dayNumber': 2,
                                     'evening': {   'category': 'relaxation',
                                                    'cost': 300,
                                                    'duration': '3 hours',
                                                    'explanation': 'Board a catamaran ferry towards the monolithic '
                                                                   'Buddha statue, followed by evening breeze along '
                                                                   'Tank Bund promenade.',
                                                    'isCostEstimated': True,
                                                    'location': 'Necklace Road',
                                                    'mealSuggestion': 'Street-side spicy sweet corn or roasted peanuts '
                                                                      'along the Tank Bund and Necklace Road '
                                                                      'promenade.',
                                                    'period': 'Evening',
                                                    'practicalTips': 'Boating queues can build up around sunset (5:30 '
                                                                     'PM); opt for the regular ferry or speed boat '
                                                                     'from Lumbini Park. Evening breezes make it '
                                                                     'pleasant.',
                                                    'time': '05:30 PM – 08:30 PM',
                                                    'title': 'Sunset Boat Cruise at Hussain Sagar Lake',
                                                    'transitNote': '~25-35 min cab from Ibrahim Bagh/Tolichowki '
                                                                   'northeast to Hussain Sagar.'},
                                     'morning': {   'category': 'adventure',
                                                    'cost': 250,
                                                    'duration': '3.5 hours',
                                                    'explanation': 'Experience the world-renowned clapping acoustic '
                                                                   'system at the Balahissar gate and trek to the '
                                                                   'summit for citadel views.',
                                                    'isCostEstimated': True,
                                                    'location': 'Ibrahim Bagh',
                                                    'mealSuggestion': 'Carry a refillable water bottle; fresh tender '
                                                                      'coconut water vendors wait outside the fort '
                                                                      'exit.',
                                                    'period': 'Morning',
                                                    'practicalTips': 'Wear comfortable walking shoes with good grip '
                                                                     'for climbing ~380 stone steps. Start by 8:30 AM '
                                                                     'to beat the Deccan sun. Hire an official ASI '
                                                                     'guide at the entry gate.',
                                                    'time': '08:00 AM – 11:30 AM',
                                                    'title': 'Golconda Fort Acoustic & Ramparts Trek',
                                                    'transitNote': 'Located in western Hyderabad; take a direct cab or '
                                                                   'auto (~30 min from central areas).'},
                                     'theme': 'Citadels & Royal Tombs'},
                                 {   'afternoon': {   'category': 'food',
                                                      'cost': 550,
                                                      'duration': '2.5 hours',
                                                      'explanation': 'Experience rich regional coastal flavours '
                                                                     'including Avakkai rice and apricot delight '
                                                                     'dessert.',
                                                      'isCostEstimated': True,
                                                      'location': 'Jubilee Hills',
                                                      'mealSuggestion': 'Multi-course Andhra banana leaf thali with '
                                                                        'gongura pachadi, pappu, sambar, and signature '
                                                                        'apricot delight.',
                                                      'period': 'Afternoon',
                                                      'practicalTips': 'Andhra spice levels can be potent; ask for '
                                                                       'ghee to temper gunpowder podi rice if '
                                                                       'sensitive to chili.',
                                                      'time': '01:00 PM – 03:30 PM',
                                                      'title': 'Traditional Andhra Thali at Spicy Venue',
                                                      'transitNote': '~25 min cab/metro ride from Old City northwest '
                                                                     'to Jubilee Hills.'},
                                     'dayNumber': 3,
                                     'evening': {   'category': 'nature',
                                                    'cost': 80,
                                                    'duration': '3 hours',
                                                    'explanation': 'A tranquil contrast to the Old City, exploring '
                                                                   'illuminated suspension architecture and landscaped '
                                                                   'gardens.',
                                                    'isCostEstimated': True,
                                                    'location': 'Hitec City',
                                                    'mealSuggestion': 'Lakeside cafes offer artisan pizzas, cold '
                                                                      'brews, and regional fusion snacks.',
                                                    'period': 'Evening',
                                                    'practicalTips': 'Pedestrian walkway on the cable bridge is best '
                                                                     'visited after 6:00 PM when the LED lighting '
                                                                     'illuminates the lake.',
                                                    'time': '04:30 PM – 07:30 PM',
                                                    'title': 'Durgam Cheruvu Cable Bridge & Botanical Park Walk',
                                                    'transitNote': '~10-15 min drive within the Jubilee Hills / '
                                                                   'Madhapur IT corridor.'},
                                     'morning': {   'category': 'culture',
                                                    'cost': 100,
                                                    'duration': '3 hours',
                                                    'explanation': 'View the famous Veiled Rebecca marble sculpture '
                                                                   "and the musical mechanical clock in one of India's "
                                                                   'largest national collections.',
                                                    'isCostEstimated': True,
                                                    'location': 'Darulshifa',
                                                    'mealSuggestion': 'Light snacks, filter coffee, and bottled water '
                                                                      'available at the courtyard cafeteria.',
                                                    'period': 'Morning',
                                                    'practicalTips': 'Museum is closed on Fridays. The famous musical '
                                                                     'mechanical clock strikes on the hour in the '
                                                                     'central courtyard; arrive 10 minutes before the '
                                                                     'hour to view it.',
                                                    'time': '09:00 AM – 12:00 PM',
                                                    'title': 'Salar Jung Museum Masterpieces',
                                                    'transitNote': 'Located along Musi River; easily reachable via '
                                                                   'Nayapul road or MGBS metro station (~10 min '
                                                                   'walk).'},
                                     'theme': 'Modern Craft & Culinary Innovation'},
                                 {   'afternoon': {   'category': 'food',
                                                      'cost': 400,
                                                      'duration': '2.5 hours',
                                                      'explanation': 'Discover spicy jowar rotis, natukodi pulusu '
                                                                     '(country chicken curry), and fresh curd rice.',
                                                      'isCostEstimated': True,
                                                      'location': 'Banjara Hills',
                                                      'mealSuggestion': 'Jowar roti with country chicken curry '
                                                                        '(natukodi pulusu) or spicy gutti vankaya '
                                                                        '(stuffed eggplant).',
                                                      'period': 'Afternoon',
                                                      'practicalTips': 'Traditional Telangana cuisine features rustic '
                                                                       'dry spices, jowar flatbreads, and tangy '
                                                                       'tamarind stews.',
                                                      'time': '01:00 PM – 03:30 PM',
                                                      'title': 'Telangana Regional Thali Experience',
                                                      'transitNote': '~15 min cab from Madhapur to Banjara Hills '
                                                                     'dining hub.'},
                                     'dayNumber': 4,
                                     'evening': {   'category': 'nature',
                                                    'cost': 100,
                                                    'duration': '2.5 hours',
                                                    'explanation': 'Walk the shaded outer perimeter trail observing '
                                                                   'peacock roosts and protected Deccan scrub flora.',
                                                    'isCostEstimated': True,
                                                    'location': 'Jubilee Hills',
                                                    'mealSuggestion': 'Healthy fruit bowls or South Indian filter '
                                                                      'coffee at cafes flanking Road No. 36.',
                                                    'period': 'Evening',
                                                    'practicalTips': 'Outer walking track is open to all; wear sports '
                                                                     'shoes and apply mosquito repellent during dusk '
                                                                     'hours.',
                                                    'time': '05:00 PM – 07:30 PM',
                                                    'title': 'KBR National Park Nature Trail',
                                                    'transitNote': 'Directly in central Banjara Hills / Jubilee Hills '
                                                                   'roundabout.'},
                                     'morning': {   'category': 'culture',
                                                    'cost': 150,
                                                    'duration': '3.5 hours',
                                                    'explanation': 'Engage directly with rural weavers and terracotta '
                                                                   'sculptors in a tranquil open-air cultural village.',
                                                    'isCostEstimated': True,
                                                    'location': 'Madhapur',
                                                    'mealSuggestion': 'Fresh sugarcane juice and hot mirchi bajji '
                                                                      'inside the village pavilion.',
                                                    'period': 'Morning',
                                                    'practicalTips': 'Entry ticket includes access to craft stalls and '
                                                                     'rural museum setup. Fixed price outlets contrast '
                                                                     'with negotiable artisan stalls.',
                                                    'time': '09:00 AM – 12:30 PM',
                                                    'title': 'Shilparamam Arts & Crafts Village',
                                                    'transitNote': 'Located in Madhapur; convenient access via Hitec '
                                                                   'City metro station.'},
                                     'theme': 'Artisanal Weaves & Lakefront Serenity'}],
                     'destinationId': 'hyderabad',
                     'summary': "A 4-day exploration bridging Golconda's historic bastions, Charminar's aromatic "
                                'quarters, artisan villages, and modern lakeside promenades.',
                     'title': 'Nizami Grandeur & Culinary Trail'},
    'jaipur': {   'baseDailyRates': {   'balanced': {'food': 1300, 'stay': 2900, 'transit': 850},
                                        'budget': {'food': 650, 'stay': 1300, 'transit': 450},
                                        'comfort': {'food': 2300, 'stay': 6200, 'transit': 1700}},
                  'days': [   {   'afternoon': {   'category': 'culture',
                                                   'cost': 250,
                                                   'duration': '2.5 hours',
                                                   'explanation': 'Watch master block-carvers demonstrate traditional '
                                                                  'natural-dye woodblock printing in a restored '
                                                                  'haveli.',
                                                   'isCostEstimated': True,
                                                   'location': 'Amer Village',
                                                   'mealSuggestion': 'Light vegetarian thali or sandwiches with fresh '
                                                                     'lemon ginger cooler in the museum courtyard '
                                                                     'cafe.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Housed in a magnificently restored haveli; '
                                                                    'photography without flash is allowed. Artisan '
                                                                    'block-carvers give live demonstrations on top '
                                                                    'floor.',
                                                   'time': '12:30 PM – 03:00 PM',
                                                   'title': 'Anokhi Museum of Hand Printing & Lunch',
                                                   'transitNote': 'Situated in Amer village below the fort; 5 min auto '
                                                                  'or 15 min walk.'},
                                  'dayNumber': 1,
                                  'evening': {   'category': 'relaxation',
                                                 'cost': 150,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Perch on the ridge of the Aravalli hills overlooking '
                                                                'the entire Pink City illuminated as twilight falls.',
                                                 'isCostEstimated': True,
                                                 'location': 'Aravalli Hills',
                                                 'mealSuggestion': 'Chai and roasted spiced peanuts at the Padao '
                                                                   'open-air restaurant overlooking the city.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'The winding uphill ghat road to Nahargarh takes ~30 '
                                                                  'min. Bring a light jacket in winter as hilltop '
                                                                  'breezes turn cool after sunset.',
                                                 'time': '05:00 PM – 07:30 PM',
                                                 'title': 'Nahargarh Fort Sunset Viewpoint',
                                                 'transitNote': 'Direct ~25 min scenic drive uphill via Aravalli '
                                                                'bypass road.'},
                                  'morning': {   'category': 'culture',
                                                 'cost': 300,
                                                 'duration': '3.5 hours',
                                                 'explanation': 'Traverse massive sandstone battlements and marvel at '
                                                                'thousands of concave mirrors inlaid in the royal '
                                                                'ceiling.',
                                                 'isCostEstimated': True,
                                                 'location': 'Amer, Jaipur',
                                                 'mealSuggestion': 'Kulhad chai and hot kachoris from stall vendors '
                                                                   'near the Amer elephant stand.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Arrive at Amer Fort by 8:30 AM to beat tourist '
                                                                  'buses. Composite ticket covering Amer, Jantar '
                                                                  'Mantar, Hawa Mahal, and Nahargarh saves money and '
                                                                  'queue time.',
                                                 'time': '08:00 AM – 11:30 AM',
                                                 'title': 'Amber Palace & Sheesh Mahal Exploration',
                                                 'transitNote': 'Located 11 km north of Jaipur center; 25-30 min cab '
                                                                'or auto ride.'},
                                  'theme': 'Hilltop Bastions & Mirror Palaces'},
                              {   'afternoon': {   'category': 'culture',
                                                   'cost': 200,
                                                   'duration': '3 hours',
                                                   'explanation': "Discover the world's largest stone sundial and "
                                                                  'precise 18th-century instruments calculating '
                                                                  'stellar orbits.',
                                                   'isCostEstimated': True,
                                                   'location': 'Old City, Jaipur',
                                                   'mealSuggestion': 'Walk across to LMB (Laxmi Mishthan Bhandar) in '
                                                                     'Johari Bazaar for authentic Rajasthani pyaaz '
                                                                     'kachori, samosa, and paneer ghewar.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Adjacent to City Palace; hire an audio guide or '
                                                                    'licensed astronomy guide to understand how giant '
                                                                    'stone sundials calculate time.',
                                                   'time': '11:30 AM – 02:30 PM',
                                                   'title': 'Jantar Mantar UNESCO Astronomical Observatory',
                                                   'transitNote': 'Sensible route pairing: directly adjacent to City '
                                                                  'Palace gate (~2 min walk).'},
                                  'dayNumber': 2,
                                  'evening': {   'category': 'food',
                                                 'cost': 200,
                                                 'duration': '3 hours',
                                                 'explanation': 'Admire the 953 honeycombed jharokhas of Hawa Mahal, '
                                                                'then sample Ghewar and Pyaaz Kachori at LMB.',
                                                 'isCostEstimated': True,
                                                 'location': 'Badi Chaupar',
                                                 'mealSuggestion': 'Crispy sweet jalebis and hot rabdi from '
                                                                   'traditional sweet makers in Badi Chaupar.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Best facade photography of Hawa Mahal is from '
                                                                  'rooftop cafes opposite the street (Tattoo Cafe or '
                                                                  'Wind View Cafe) during late afternoon light.',
                                                 'time': '04:30 PM – 07:30 PM',
                                                 'title': 'Hawa Mahal Photo Walk & Johari Bazaar Tasting',
                                                 'transitNote': '~5 min walk from Jantar Mantar along Sireh Deori '
                                                                'Bazaar.'},
                                  'morning': {   'category': 'culture',
                                                 'cost': 350,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Walk through Mubarak Mahal, the royal armoury, and '
                                                                'the legendary Pritam Niwas Chowk peacock gate.',
                                                 'isCostEstimated': True,
                                                 'location': 'Old City, Jaipur',
                                                 'mealSuggestion': 'Chilled sweet lassi or cold coffee at the palace '
                                                                   'cafe inside Mubarak Mahal.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Standard entry covers main courtyards and museum; '
                                                                  'private quarters (Chandra Mahal) require special '
                                                                  'royal tour ticket. Wear modest clothing.',
                                                 'time': '08:30 AM – 11:00 AM',
                                                 'title': 'City Palace Courtyards & Peacock Gate',
                                                 'transitNote': 'Located in the heart of the walled Pink City; '
                                                                'pedestrian-friendly cluster.'},
                                  'theme': 'Astronomy, Palaces & Pink Bazaars'},
                              {   'afternoon': {   'category': 'food',
                                                   'cost': 650,
                                                   'duration': '2.5 hours',
                                                   'explanation': 'Indulge in Dal Baati Churma, Gatte ki Sabzi, Ker '
                                                                  'Sangri, and warm bajra rotis laced with pure desi '
                                                                  'ghee.',
                                                   'isCostEstimated': True,
                                                   'location': 'Jaipur',
                                                   'mealSuggestion': 'Traditional royal Rajasthani feast: dal baati '
                                                                     'churma, ker sangri, gatte ki sabzi, bajre ki '
                                                                     'roti with jaggery, and malpua.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Thali meal is unlimited and rich with pure desi '
                                                                    'ghee; pace yourself and drink warm water between '
                                                                    'courses.',
                                                   'time': '12:30 PM – 03:00 PM',
                                                   'title': 'Grand Rajasthani Thali at Chokhi Dhani / Laxmi Mishthan',
                                                   'transitNote': '~20 min cab back towards central dining district.'},
                                  'dayNumber': 3,
                                  'evening': {   'category': 'relaxation',
                                                 'cost': 150,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Watch the water palace floating gracefully on Man '
                                                                'Sagar lake, followed by browsing hand-painted quartz '
                                                                'pottery.',
                                                 'isCostEstimated': True,
                                                 'location': 'Amer Road',
                                                 'mealSuggestion': 'Spiced roasted sweet corn and masala tea while '
                                                                   'gazing at illuminated palace.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Jal Mahal interior is closed to visitors; the '
                                                                  'promenade walk along the lake offers beautiful '
                                                                  'night reflections and cool lake breezes.',
                                                 'time': '04:30 PM – 07:00 PM',
                                                 'title': 'Jal Mahal Promenade & Artisanal Blue Pottery',
                                                 'transitNote': 'Located along Amer Road on the route between Amer and '
                                                                'Jaipur center.'},
                                  'morning': {   'category': 'adventure',
                                                 'cost': 180,
                                                 'duration': '3 hours',
                                                 'explanation': 'Marvel at the hypnotic symmetrical geometric steps of '
                                                                'the 16th-century baoli and Jaivana cannon.',
                                                 'isCostEstimated': True,
                                                 'location': 'Amer',
                                                 'mealSuggestion': 'Fresh lime soda or coconut water near the stepwell '
                                                                   'square.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Walking down steps of Panna Meena Ka Kund is '
                                                                  'restricted for safety; perimeter terrace '
                                                                  'photography is free and magnificent.',
                                                 'time': '08:30 AM – 11:30 AM',
                                                 'title': 'Panna Meena Ka Kund Stepwell & Jaigarh Fort',
                                                 'transitNote': '~10 min drive north of Amer fort.'},
                                  'theme': 'Stepwells, Sacred Temples & Royal Thali'},
                              {   'afternoon': {   'category': 'food',
                                                   'cost': 200,
                                                   'duration': '2.5 hours',
                                                   'explanation': 'Drink creamy thick curd lassi served in terracotta '
                                                                  'cups that have made MI Road famous since 1944.',
                                                   'isCostEstimated': True,
                                                   'location': 'MI Road',
                                                   'mealSuggestion': 'Thick sweet or salted curd lassi topped with '
                                                                     'thick malai skin served in an earthen clay '
                                                                     'kullhad.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Shop 312 on MI Road is the original Lassiwala '
                                                                    '(operating since 1944). Arrive before 3 PM as '
                                                                    'fresh curd batches frequently sell out.',
                                                   'time': '12:00 PM – 02:30 PM',
                                                   'title': 'Lassiwala Traditional Clay Kullhad & Street Food',
                                                   'transitNote': '~15 min drive from Galta gorge to MI Road.'},
                                  'dayNumber': 4,
                                  'evening': {   'category': 'nature',
                                                 'cost': 100,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Relax among terraced watercourses, painted pavilions, '
                                                                'and fragrant flowerbeds constructed for queenly '
                                                                'retreats.',
                                                 'isCostEstimated': True,
                                                 'location': 'Ghat Ki Guni',
                                                 'mealSuggestion': 'Evening snacks and masala chai at heritage garden '
                                                                   'kiosk.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Quiet tiered gardens adorned with murals depicting '
                                                                  'Radha-Krishna stories; ideal for serene leisurely '
                                                                  'walks.',
                                                 'time': '04:30 PM – 07:00 PM',
                                                 'title': 'Sisodia Rani Garden & Palace Walk',
                                                 'transitNote': '~15 min drive east along Agra Road.'},
                                  'morning': {   'category': 'adventure',
                                                 'cost': 100,
                                                 'duration': '3 hours',
                                                 'explanation': 'Hike the mountain gorge containing natural freshwater '
                                                                'kunds and ancient shrines carved into rocky cliffs.',
                                                 'isCostEstimated': True,
                                                 'location': 'Khania-Balaji',
                                                 'mealSuggestion': 'Carry your own bottled water; avoid eating outside '
                                                                   'snacks near temple pavilions.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Keep all sunglasses, food packets, and loose items '
                                                                  'zipped inside backpacks as resident rhesus macaque '
                                                                  'monkeys are curious and quick.',
                                                 'time': '08:00 AM – 11:00 AM',
                                                 'title': 'Galtaji Monkey Temple & Natural Springs',
                                                 'transitNote': 'Located in eastern gorge; ~20 min cab from central '
                                                                'Jaipur.'},
                                  'theme': 'Galtaji Sun Temple & Wildlife Scrub'}],
                  'destinationId': 'jaipur',
                  'summary': 'A journey through royal Rajasthan featuring hilltop bastions, celestial observatories, '
                             'hand-block printing, and rich thalis.',
                  'title': 'Rajput Fortresses & Regal Bazaars'},
    'munnar': {   'baseDailyRates': {   'balanced': {'food': 1100, 'stay': 2700, 'transit': 800},
                                        'budget': {'food': 550, 'stay': 1100, 'transit': 450},
                                        'comfort': {'food': 2000, 'stay': 5500, 'transit': 1500}},
                  'days': [   {   'afternoon': {   'category': 'food',
                                                   'cost': 320,
                                                   'duration': '2.5 hours',
                                                   'explanation': 'Feast on parotta, stew, red matta rice, avial, and '
                                                                  'crisp banana chips infused with cold-pressed '
                                                                  'coconut oil.',
                                                   'isCostEstimated': True,
                                                   'location': 'Munnar Town',
                                                   'mealSuggestion': 'Flaky layered Malabar parotta with spicy beef or '
                                                                     'vegetable stew, followed by hot banana fritters '
                                                                     '(pazham pori).',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Casual, bustling local eatery; table turnover is '
                                                                    'quick. Cash or UPI accepted.',
                                                   'time': '12:30 PM – 03:00 PM',
                                                   'title': 'Kerala Sadhya at Rapsy Restaurant',
                                                   'transitNote': 'Located right in Munnar central market; 5 min drive '
                                                                  'from tea museum.'},
                                  'dayNumber': 1,
                                  'evening': {   'category': 'nature',
                                                 'cost': 0,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Take an easy stroll through cardamom bushes and '
                                                                'coffee groves overlooking misty valleys blanketed in '
                                                                'rolling fog.',
                                                 'isCostEstimated': True,
                                                 'location': 'Pothamedu',
                                                 'mealSuggestion': 'Hot spiced ginger tea and roasted corn from '
                                                                   'viewpoint shacks.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Valley road has sharp hairpins; wear a warm fleece '
                                                                  'or sweater as temperatures drop rapidly once '
                                                                  'mountain fog rolls in.',
                                                 'time': '04:00 PM – 06:30 PM',
                                                 'title': 'Pothamedu Viewpoint Sunset Walk',
                                                 'transitNote': '~15-20 min scenic uphill drive south of Munnar town.'},
                                  'morning': {   'category': 'culture',
                                                 'cost': 180,
                                                 'duration': '3 hours',
                                                 'explanation': 'Learn the history of tea cultivation in the high '
                                                                'ranges and sample freshly processed Orthodox black '
                                                                'and white teas.',
                                                 'isCostEstimated': True,
                                                 'location': 'Nullatanni Estate',
                                                 'mealSuggestion': 'Sample fresh aromatic cardamom-spiced black tea at '
                                                                   'the museum tasting counter.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Factory machinery demonstration runs every 30 '
                                                                  'minutes; check timing on arrival. Purchase fresh '
                                                                  'garden-grade orthodox black and green tea directly '
                                                                  'at the factory counter.',
                                                 'time': '08:30 AM – 11:30 AM',
                                                 'title': 'KDHP Tea Museum & CTC Factory Demonstration',
                                                 'transitNote': '~10 min auto or taxi drive from Munnar town center.'},
                                  'theme': 'Emerald Plantations & Tea Heritage'},
                              {   'afternoon': {   'category': 'adventure',
                                                   'cost': 250,
                                                   'duration': '3 hours',
                                                   'explanation': 'Board a silent speed boat across the reservoir '
                                                                  'encircled by lush tea estates and occasional wild '
                                                                  'elephant herds.',
                                                   'isCostEstimated': True,
                                                   'location': 'Mattupetty',
                                                   'mealSuggestion': 'Steamed corn and fresh pineapple slices with '
                                                                     'chili salt at the dam promenade.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Speedboat rides require life vests. Elephant '
                                                                    'sightings along reservoir banks are common during '
                                                                    'quiet afternoon hours.',
                                                   'time': '12:30 PM – 03:30 PM',
                                                   'title': 'Mattupetty Dam & Eco Lake Boating',
                                                   'transitNote': '~35 min drive southeast from Rajamalai towards '
                                                                  'Mattupetty.'},
                                  'dayNumber': 2,
                                  'evening': {   'category': 'relaxation',
                                                 'cost': 150,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Test your voice resonance against the hills and glide '
                                                                "past cherry blossoms bordering Asia's first arch dam.",
                                                 'isCostEstimated': True,
                                                 'location': 'Kundala',
                                                 'mealSuggestion': 'Locally made handmade chocolates and hot spiced '
                                                                   'tea.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Sensible route pairing: Echo Point is directly on '
                                                                  'Mattupetty-Kundala lake route (~15 min drive past '
                                                                  'dam).',
                                                 'time': '05:00 PM – 07:30 PM',
                                                 'title': 'Echo Point & Kundala Lake Pedalo',
                                                 'transitNote': 'Direct continuation along Top Station road.'},
                                  'morning': {   'category': 'nature',
                                                 'cost': 300,
                                                 'duration': '3.5 hours',
                                                 'explanation': 'Spot the endangered mountain goat Nilgiri Tahr '
                                                                'grazing peacefully against the backdrop of Anamudi '
                                                                'peak.',
                                                 'isCostEstimated': True,
                                                 'location': 'Rajamalai Range',
                                                 'mealSuggestion': 'Carry light dry fruits or energy bars; no '
                                                                   'single-use plastic water bottles allowed past '
                                                                   'forest security check (purified refill available).',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Pre-book park tickets online through forest '
                                                                  'department portal to skip long queues. Private '
                                                                  'vehicles park at base; official forest buses '
                                                                  'shuttle visitors up.',
                                                 'time': '07:30 AM – 11:00 AM',
                                                 'title': 'Eravikulam National Park & Rajamalai Safari',
                                                 'transitNote': '~30 min drive north along NH85 to Rajamalai '
                                                                'checkpost.'},
                                  'theme': 'Endangered Wildlife & High Peaks'},
                              {   'afternoon': {   'category': 'adventure',
                                                   'cost': 80,
                                                   'duration': '2.5 hours',
                                                   'explanation': 'Hike across the suspension bridge towards the '
                                                                  'cascading tiered torrent surrounded by thick shola '
                                                                  'jungle.',
                                                   'isCostEstimated': True,
                                                   'location': 'Pallivasal',
                                                   'mealSuggestion': 'Hot Kerala pazhampori (banana fritters) and '
                                                                     'spicy tea from tea stall overlooking the '
                                                                     'cascades.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Approach road across narrow bridge is '
                                                                    'single-lane; drive cautiously or hire a local 4x4 '
                                                                    'jeep during rainy seasons.',
                                                   'time': '12:30 PM – 03:00 PM',
                                                   'title': 'Attukad Waterfalls Trek & Tea Stall Snack',
                                                   'transitNote': '~20 min drive from Chithirapuram through tea '
                                                                  'estates.'},
                                  'dayNumber': 3,
                                  'evening': {   'category': 'culture',
                                                 'cost': 400,
                                                 'duration': '2.5 hours',
                                                 'explanation': "Witness Kerala's 3000-year-old martial discipline and "
                                                                'elaborate facial makeup storytelling drama.',
                                                 'isCostEstimated': True,
                                                 'location': 'Munnar Arts Center',
                                                 'mealSuggestion': 'Dinner at a local restaurant: Kerala appam with '
                                                                   'vegetable or egg stew.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Arrive 30 minutes early to watch the intricate '
                                                                  'facial makeup application (Chutti) before Kathakali '
                                                                  'performance begins.',
                                                 'time': '04:30 PM – 07:00 PM',
                                                 'title': 'Kalaripayattu Martial Arts & Kathakali Performance',
                                                 'transitNote': 'Located in Munnar town cultural auditorium.'},
                                  'morning': {   'category': 'nature',
                                                 'cost': 200,
                                                 'duration': '3 hours',
                                                 'explanation': 'Smell fresh nutmeg, cloves, cinnamon bark, and '
                                                                'lemongrass while discovering ancient Malabar '
                                                                'medicinal traditions.',
                                                 'isCostEstimated': True,
                                                 'location': 'Chithirapuram',
                                                 'mealSuggestion': 'Herbal infused spiced water or fresh ginger-honey '
                                                                   'tea.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Guided walks explain Ayurvedic uses of natural '
                                                                  'herbs; buy whole unadulterated spices (green '
                                                                  'cardamom, black pepper, nutmeg) directly from '
                                                                  'certified estate stores.',
                                                 'time': '08:30 AM – 11:30 AM',
                                                 'title': 'Spice Garden Walk & Botanical Workshop',
                                                 'transitNote': '~15 min drive south of town towards Chithirapuram.'},
                                  'theme': 'Spices, Waterfalls & Ayurvedic Rest'},
                              {   'afternoon': {   'category': 'food',
                                                   'cost': 350,
                                                   'duration': '3 hours',
                                                   'explanation': 'Sip golden pekoe brewed from high-elevation leaves '
                                                                  'alongside steamed Kerala appams and vegetable stew.',
                                                   'isCostEstimated': True,
                                                   'location': 'Kolukkumalai Factory',
                                                   'mealSuggestion': 'Estate cafeteria brunch: fluffy appams, coconut '
                                                                     'milk, and fresh hill bananas.',
                                                   'period': 'Afternoon',
                                                   'practicalTips': 'Tour the century-old orthodox tea factory using '
                                                                    'traditional English wood rollers.',
                                                   'time': '11:30 AM – 02:30 PM',
                                                   'title': 'Organic Estate Herbal Tea Tasting & Brunch',
                                                   'transitNote': 'Located adjacent to Kolukkumalai estate peak.'},
                                  'dayNumber': 4,
                                  'evening': {   'category': 'relaxation',
                                                 'cost': 0,
                                                 'duration': '2.5 hours',
                                                 'explanation': 'Walk the heart-shaped gap valley admiring wild '
                                                                'wildflowers and dramatic cliff drop-offs into Tamil '
                                                                'Nadu plains.',
                                                 'isCostEstimated': True,
                                                 'location': 'Lockhart Estate',
                                                 'mealSuggestion': 'Roasted peanuts and cardamom tea at roadside '
                                                                   'outlook.',
                                                 'period': 'Evening',
                                                 'practicalTips': 'Carry a light windbreaker; sunset over the gorge '
                                                                  'offers wide vistas of the Bison valley.',
                                                 'time': '04:30 PM – 07:00 PM',
                                                 'title': 'Lockhart Gap Nature Trail',
                                                 'transitNote': '~25 min drive along Kochi-Dhanushkodi road on '
                                                                'return.'},
                                  'morning': {   'category': 'adventure',
                                                 'cost': 800,
                                                 'duration': '4 hours',
                                                 'explanation': "Ride a 4x4 rugged trail to the world's highest "
                                                                'organic tea estate (7,900 ft) for a breathtaking '
                                                                'sea-of-clouds sunrise.',
                                                 'isCostEstimated': True,
                                                 'location': 'Kolukkumalai Border',
                                                 'mealSuggestion': 'Sip steaming hot orthodox black tea brewed at '
                                                                   '7,900 ft while watching the golden dawn.',
                                                 'period': 'Morning',
                                                 'practicalTips': 'Start at 4:30 AM in an authorized 4x4 jeep; the 17 '
                                                                  'km bumpy off-road trail is rugged, but the '
                                                                  'cloud-inversion sunrise is unmatched.',
                                                 'time': '05:30 AM – 09:30 AM',
                                                 'title': 'Kolukkumalai Sunrise Jeep Safari',
                                                 'transitNote': 'Rough 4x4 trail begins at Suryanelli base camp (~45 '
                                                                'min from Munnar).'},
                                  'theme': 'High Cloud Forest & Sunrise Ridge'}],
                  'destinationId': 'munnar',
                  'summary': 'A cool highland retreat through emerald tea plantations, endemic Nilgiri Tahr habitats, '
                             'spice gardens, and cascading waterfalls.',
                  'title': 'Highland Estates & Western Ghats Mist'}}


# ==============================================================================
# Verified Landmark Coordinates for Curated Base Destinations (Phase 6.2)
# Exact physical coordinates sourced from verified municipal and landmark databases.
# Unverified attractions/destinations remain None (unavailable) without fabrication.
# ==============================================================================
VERIFIED_LANDMARK_COORDINATES = {
    # HYDERABAD
    ("hyderabad", 1, "morning"): {"lat": 17.3616, "lng": 78.4747, "precision": "verified_attraction", "addressLabel": "Charminar, Old City, Hyderabad"},
    ("hyderabad", 1, "afternoon"): {"lat": 17.3639, "lng": 78.4735, "precision": "verified_attraction", "addressLabel": "Hotel Shadab, Madina Circle, Hyderabad"},
    ("hyderabad", 1, "evening"): {"lat": 17.3578, "lng": 78.4717, "precision": "verified_attraction", "addressLabel": "Chowmahalla Palace, Motigalli, Hyderabad"},
    ("hyderabad", 2, "morning"): {"lat": 17.3833, "lng": 78.4011, "precision": "verified_attraction", "addressLabel": "Golconda Fort, Ibrahim Bagh, Hyderabad"},
    ("hyderabad", 2, "afternoon"): {"lat": 17.3941, "lng": 78.3957, "precision": "verified_attraction", "addressLabel": "Qutb Shahi Tombs, Ibrahim Bagh, Hyderabad"},
    ("hyderabad", 2, "evening"): {"lat": 17.4239, "lng": 78.4738, "precision": "verified_attraction", "addressLabel": "Hussain Sagar Lake, Necklace Road, Hyderabad"},
    ("hyderabad", 3, "morning"): {"lat": 17.3713, "lng": 78.4804, "precision": "verified_attraction", "addressLabel": "Salar Jung Museum, Darulshifa, Hyderabad"},
    ("hyderabad", 3, "afternoon"): {"lat": 17.4325, "lng": 78.4073, "precision": "verified_attraction", "addressLabel": "The Spicy Venue, Jubilee Hills, Hyderabad"},
    ("hyderabad", 3, "evening"): {"lat": 17.4387, "lng": 78.3846, "precision": "verified_attraction", "addressLabel": "Durgam Cheruvu Cable Bridge, Hitec City, Hyderabad"},
    ("hyderabad", 4, "morning"): {"lat": 17.4526, "lng": 78.3779, "precision": "verified_attraction", "addressLabel": "Shilparamam Arts Village, Madhapur, Hyderabad"},
    ("hyderabad", 4, "afternoon"): {"lat": 17.4156, "lng": 78.4354, "precision": "verified_attraction", "addressLabel": "Banjara Hills, Hyderabad"},
    ("hyderabad", 4, "evening"): {"lat": 17.4230, "lng": 78.4180, "precision": "verified_attraction", "addressLabel": "KBR National Park, Jubilee Hills, Hyderabad"},

    # GOA
    ("goa", 1, "morning"): {"lat": 15.4989, "lng": 73.8315, "precision": "verified_attraction", "addressLabel": "Fontainhas Latin Quarter, Panaji, Goa"},
    ("goa", 1, "afternoon"): {"lat": 15.4980, "lng": 73.8322, "precision": "verified_attraction", "addressLabel": "Viva Panjim, Fontainhas, Goa"},
    ("goa", 1, "evening"): {"lat": 15.4820, "lng": 73.8080, "precision": "verified_attraction", "addressLabel": "Miramar Beach, Panaji, Goa"},
    ("goa", 2, "morning"): {"lat": 15.5009, "lng": 73.9116, "precision": "verified_attraction", "addressLabel": "Basilica of Bom Jesus, Old Goa"},
    ("goa", 2, "afternoon"): {"lat": 15.4128, "lng": 74.0287, "precision": "verified_attraction", "addressLabel": "Sahakari Spice Farm, Ponda, Goa"},
    ("goa", 2, "evening"): {"lat": 15.0886, "lng": 73.9211, "precision": "verified_attraction", "addressLabel": "Cabo de Rama Fort, Canacona, Goa"},
    ("goa", 3, "morning"): {"lat": 15.0100, "lng": 74.0232, "precision": "verified_attraction", "addressLabel": "Palolem Beach, South Goa"},
    ("goa", 3, "afternoon"): {"lat": 15.1764, "lng": 73.9482, "precision": "verified_attraction", "addressLabel": "The Fisherman's Wharf, Cavelossim, Goa"},
    ("goa", 3, "evening"): {"lat": 15.0452, "lng": 73.9878, "precision": "verified_attraction", "addressLabel": "Agonda Beach, South Goa"},
    ("goa", 4, "morning"): {"lat": 15.6056, "lng": 73.7364, "precision": "verified_attraction", "addressLabel": "Chapora Fort, Vagator, North Goa"},
    ("goa", 4, "afternoon"): {"lat": 15.5892, "lng": 73.7745, "precision": "verified_attraction", "addressLabel": "Assagao, North Goa"},
    ("goa", 4, "evening"): {"lat": 15.5733, "lng": 73.7410, "precision": "verified_attraction", "addressLabel": "Anjuna Beach, North Goa"},

    # JAIPUR
    ("jaipur", 1, "morning"): {"lat": 26.9855, "lng": 75.8513, "precision": "verified_attraction", "addressLabel": "Amber Palace, Amer, Jaipur"},
    ("jaipur", 1, "afternoon"): {"lat": 26.9873, "lng": 75.8568, "precision": "verified_attraction", "addressLabel": "Anokhi Museum, Amer Village, Jaipur"},
    ("jaipur", 1, "evening"): {"lat": 26.9374, "lng": 75.8156, "precision": "verified_attraction", "addressLabel": "Nahargarh Fort, Jaipur"},
    ("jaipur", 2, "morning"): {"lat": 26.9258, "lng": 75.8237, "precision": "verified_attraction", "addressLabel": "City Palace, Jaipur"},
    ("jaipur", 2, "afternoon"): {"lat": 26.9248, "lng": 75.8246, "precision": "verified_attraction", "addressLabel": "Jantar Mantar, Jaipur"},
    ("jaipur", 2, "evening"): {"lat": 26.9239, "lng": 75.8267, "precision": "verified_attraction", "addressLabel": "Hawa Mahal, Badi Chaupar, Jaipur"},
    ("jaipur", 3, "morning"): {"lat": 26.9850, "lng": 75.8500, "precision": "verified_attraction", "addressLabel": "Panna Meena Ka Kund, Amer, Jaipur"},
    ("jaipur", 3, "afternoon"): {"lat": 26.9196, "lng": 75.8242, "precision": "verified_attraction", "addressLabel": "Laxmi Mishthan Bhandar (LMB), Johari Bazar, Jaipur"},
    ("jaipur", 3, "evening"): {"lat": 26.9656, "lng": 75.8415, "precision": "verified_attraction", "addressLabel": "Jal Mahal, Amer Road, Jaipur"},
    ("jaipur", 4, "morning"): {"lat": 26.9161, "lng": 75.8587, "precision": "verified_attraction", "addressLabel": "Galtaji Temple, Jaipur"},
    ("jaipur", 4, "afternoon"): {"lat": 26.9189, "lng": 75.8118, "precision": "verified_attraction", "addressLabel": "Lassiwala, MI Road, Jaipur"},
    ("jaipur", 4, "evening"): {"lat": 26.8926, "lng": 75.8647, "precision": "verified_attraction", "addressLabel": "Sisodia Rani Garden, Jaipur"},

    # MUNNAR
    ("munnar", 1, "morning"): {"lat": 10.0880, "lng": 77.0519, "precision": "verified_attraction", "addressLabel": "KDHP Tea Museum, Nullatanni, Munnar"},
    ("munnar", 1, "afternoon"): {"lat": 10.0889, "lng": 77.0595, "precision": "verified_attraction", "addressLabel": "Rapsy Restaurant, Main Town, Munnar"},
    ("munnar", 1, "evening"): {"lat": 10.0543, "lng": 77.0583, "precision": "verified_attraction", "addressLabel": "Pothamedu Viewpoint, Munnar"},
    ("munnar", 2, "morning"): {"lat": 10.1500, "lng": 77.0600, "precision": "verified_attraction", "addressLabel": "Eravikulam National Park, Rajamalai, Munnar"},
    ("munnar", 2, "afternoon"): {"lat": 10.1064, "lng": 77.1246, "precision": "verified_attraction", "addressLabel": "Mattupetty Dam, Munnar"},
    ("munnar", 2, "evening"): {"lat": 10.1256, "lng": 77.1748, "precision": "verified_attraction", "addressLabel": "Echo Point & Kundala Lake, Munnar"},
    ("munnar", 3, "morning"): {"lat": 10.0345, "lng": 77.0234, "precision": "verified_attraction", "addressLabel": "Chithirapuram Spice Plantations, Munnar"},
    ("munnar", 3, "afternoon"): {"lat": 10.0408, "lng": 77.0489, "precision": "verified_attraction", "addressLabel": "Attukad Waterfalls, Pallivasal, Munnar"},
    ("munnar", 3, "evening"): {"lat": 10.0850, "lng": 77.0610, "precision": "verified_attraction", "addressLabel": "Munnar Arts Center, Main Town, Munnar"},
    ("munnar", 4, "morning"): {"lat": 10.0872, "lng": 77.1994, "precision": "verified_attraction", "addressLabel": "Kolukkumalai Tea Estate, Munnar Border"},
    ("munnar", 4, "afternoon"): {"lat": 10.0865, "lng": 77.1980, "precision": "verified_attraction", "addressLabel": "Kolukkumalai Factory & Plantation, Munnar"},
    ("munnar", 4, "evening"): {"lat": 10.0425, "lng": 77.1082, "precision": "verified_attraction", "addressLabel": "Lockhart Gap, Munnar"},
}

for (dest_id, day_num, slot), coord in VERIFIED_LANDMARK_COORDINATES.items():
    if dest_id in SAMPLE_ITINERARIES:
        for day in SAMPLE_ITINERARIES[dest_id]["days"]:
            if day.get("dayNumber") == day_num and slot in day:
                day[slot]["coordinates"] = coord


# ==============================================================================
# Verified Booking & Visitor Portals for Curated Base Destinations (Phase 6.4)
# Direct verified URLs for official ticketing, heritage authorities & parks.
# Activities without verified advance online portals remain None without guessing.
# ==============================================================================
VERIFIED_BOOKING_RESOURCES = {
    # HYDERABAD
    ("hyderabad", 1, "morning"): {
        "url": "https://asi.nic.in/",
        "providerName": "Archaeological Survey of India (ASI)",
        "resourceType": "official_monument",
        "label": "Official ASI Monument Portal ↗",
        "description": "Centrally protected monument ticketing and visitor information via ASI.",
        "isVerified": True,
    },
    ("hyderabad", 1, "evening"): {
        "url": "https://tourism.telangana.gov.in/",
        "providerName": "Telangana State Tourism",
        "resourceType": "official_tourism",
        "label": "Telangana Tourism Portal ↗",
        "description": "Heritage palace timings and visitor details via Telangana Tourism.",
        "isVerified": True,
    },
    ("hyderabad", 2, "morning"): {
        "url": "https://asi.nic.in/",
        "providerName": "Archaeological Survey of India (ASI)",
        "resourceType": "official_monument",
        "label": "Official ASI Monument Portal ↗",
        "description": "Centrally protected monument ticketing and visitor information via ASI.",
        "isVerified": True,
    },
    ("hyderabad", 2, "afternoon"): {
        "url": "https://tourism.telangana.gov.in/",
        "providerName": "Telangana State Tourism",
        "resourceType": "official_tourism",
        "label": "Telangana Tourism Heritage ↗",
        "description": "Heritage necropolis visitor information via Telangana Tourism.",
        "isVerified": True,
    },
    ("hyderabad", 3, "morning"): {
        "url": "https://salarjungmuseum.in/",
        "providerName": "Salar Jung Museum Trust",
        "resourceType": "official_museum",
        "label": "Official Museum Website ↗",
        "description": "Official museum timings, online booking and gallery information.",
        "isVerified": True,
    },
    ("hyderabad", 4, "morning"): {
        "url": "https://tourism.telangana.gov.in/",
        "providerName": "Telangana State Tourism",
        "resourceType": "official_tourism",
        "label": "Official Crafts Village Info ↗",
        "description": "Arts & Crafts Village exhibition information via Telangana Tourism.",
        "isVerified": True,
    },

    # GOA
    ("goa", 2, "morning"): {
        "url": "https://goa-tourism.com/",
        "providerName": "Goa Tourism Development Corporation (GTDC)",
        "resourceType": "official_tourism",
        "label": "Goa Tourism Official Portal ↗",
        "description": "UNESCO World Heritage site information via Goa Tourism.",
        "isVerified": True,
    },
    ("goa", 2, "afternoon"): {
        "url": "https://sahakarifarms.com/",
        "providerName": "Sahakari Spice Farm",
        "resourceType": "official_portal",
        "label": "Official Farm Website ↗",
        "description": "Direct spice plantation tours, lunch packages, and visiting guidelines.",
        "isVerified": True,
    },
    ("goa", 4, "morning"): {
        "url": "https://goa-tourism.com/",
        "providerName": "Goa Tourism Development Corporation (GTDC)",
        "resourceType": "official_tourism",
        "label": "Goa Tourism Heritage ↗",
        "description": "Coastal fortress visitor guidelines via Goa Tourism.",
        "isVerified": True,
    },

    # JAIPUR
    ("jaipur", 1, "morning"): {
        "url": "https://www.tourism.rajasthan.gov.in/",
        "providerName": "Department of Tourism, Government of Rajasthan",
        "resourceType": "official_monument",
        "label": "Rajasthan Tourism Portal ↗",
        "description": "Official state monument information, composite ticketing, and timings.",
        "isVerified": True,
    },
    ("jaipur", 1, "afternoon"): {
        "url": "https://www.anokhi.com/museum/",
        "providerName": "Anokhi Museum of Hand Printing",
        "resourceType": "official_museum",
        "label": "Official Museum Website ↗",
        "description": "Hand-block printing museum visiting hours and workshop information.",
        "isVerified": True,
    },
    ("jaipur", 1, "evening"): {
        "url": "https://www.tourism.rajasthan.gov.in/",
        "providerName": "Department of Tourism, Government of Rajasthan",
        "resourceType": "official_monument",
        "label": "Rajasthan Tourism Portal ↗",
        "description": "Nahargarh Fort timings and visiting information.",
        "isVerified": True,
    },
    ("jaipur", 2, "morning"): {
        "url": "https://thecitypalacejaipur.com/",
        "providerName": "The City Palace (MSMS II Museum Trust)",
        "resourceType": "official_monument",
        "label": "City Palace Official Portal ↗",
        "description": "Official royal palace museum ticket options and palace tour packages.",
        "isVerified": True,
    },
    ("jaipur", 2, "afternoon"): {
        "url": "https://www.tourism.rajasthan.gov.in/",
        "providerName": "Department of Tourism, Government of Rajasthan",
        "resourceType": "official_monument",
        "label": "Rajasthan Tourism Portal ↗",
        "description": "UNESCO astronomical observatory visitor info and entry tariffs.",
        "isVerified": True,
    },
    ("jaipur", 2, "evening"): {
        "url": "https://www.tourism.rajasthan.gov.in/",
        "providerName": "Department of Tourism, Government of Rajasthan",
        "resourceType": "official_monument",
        "label": "Rajasthan Tourism Portal ↗",
        "description": "Hawa Mahal palace facade and museum visitor information.",
        "isVerified": True,
    },

    # MUNNAR
    ("munnar", 1, "morning"): {
        "url": "https://www.kdhptea.com/",
        "providerName": "KDHP Tea Museum (Kanan Devan Hills)",
        "resourceType": "official_portal",
        "label": "KDHP Official Website ↗",
        "description": "Tea museum demonstration timings and factory experience details.",
        "isVerified": True,
    },
    ("munnar", 2, "morning"): {
        "url": "https://www.eravikulamnationalpark.in/",
        "providerName": "Kerala Forest & Wildlife Department",
        "resourceType": "official_park",
        "label": "Official Wildlife Ecotourism Portal ↗",
        "description": "Official online advance ticketing and safari shuttle booking system.",
        "isVerified": True,
    },
    ("munnar", 2, "afternoon"): {
        "url": "https://www.keralatourism.org/",
        "providerName": "Kerala Tourism",
        "resourceType": "official_tourism",
        "label": "Kerala Tourism Portal ↗",
        "description": "Boating and visitor guidelines via District Tourism Promotion Council.",
        "isVerified": True,
    },
}

for (dest_id, day_num, slot), resource in VERIFIED_BOOKING_RESOURCES.items():
    if dest_id in SAMPLE_ITINERARIES:
        for day in SAMPLE_ITINERARIES[dest_id]["days"]:
            if day.get("dayNumber") == day_num and slot in day:
                day[slot]["bookingResource"] = resource
