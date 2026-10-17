import destinationsData from './destinations.json' with { type: 'json' };

export const destinations = destinationsData;

export const exploreCategories = [
  { id: 'all', label: 'All Destinations' },
  { id: 'nature', label: 'Nature' },
  { id: 'adventure', label: 'Adventure' },
  { id: 'beaches', label: 'Beaches' },
  { id: 'heritage', label: 'Heritage & Culture' },
  { id: 'hills', label: 'Hill Stations' },
  { id: 'food', label: 'Food & Dining' },
  { id: 'relaxation', label: 'Relaxation' }
];

export const hillStationIds = [
  'munnar', 'manali', 'leh-ladakh', 'ooty', 'darjeeling', 'coorg', 'shillong', 'kodaikanal'
];

export function filterDestinations(list = destinationsData, { search = '', category = 'all' } = {}) {
  let results = list;
  if (search && search.trim()) {
    const q = search.trim().toLowerCase();
    results = results.filter(d =>
      (d.name && d.name.toLowerCase().includes(q)) ||
      (d.state && d.state.toLowerCase().includes(q)) ||
      (d.tagline && d.tagline.toLowerCase().includes(q)) ||
      (d.description && d.description.toLowerCase().includes(q)) ||
      (Array.isArray(d.highlights) && d.highlights.some(h => h.toLowerCase().includes(q)))
    );
  }

  if (category && category.trim().toLowerCase() !== 'all') {
    const cat = category.trim().toLowerCase();
    if (['hills', 'hill_stations', 'hill stations'].includes(cat)) {
      results = results.filter(d => hillStationIds.includes(d.id.toLowerCase()));
    } else if (['heritage', 'culture'].includes(cat)) {
      results = results.filter(d => {
        const interests = (d.primaryInterests || []).map(x => x.toLowerCase());
        return interests.includes('heritage') || interests.includes('culture');
      });
    } else {
      results = results.filter(d => {
        const interests = (d.primaryInterests || []).map(x => x.toLowerCase());
        return interests.includes(cat);
      });
    }
  }

  return results;
}

export const interestOptions = [
  { id: 'culture', label: 'Culture & Heritage', icon: 'Landmark' },
  { id: 'food', label: 'Culinary & Dining', icon: 'UtensilsCrossed' },
  { id: 'nature', label: 'Nature & Landscapes', icon: 'Mountain' },
  { id: 'relaxation', label: 'Relaxation & Wellness', icon: 'Compass' },
  { id: 'adventure', label: 'Adventure & Trails', icon: 'Footprints' }
];

export const travelStyles = [
  {
    id: 'budget',
    label: 'Budget',
    description: 'Clean hostels & homestays, public transit, local street eateries',
    rateMultiplier: 0.65
  },
  {
    id: 'balanced',
    label: 'Balanced',
    description: 'Comfortable boutique hotels, app cabs, mid-range dining',
    rateMultiplier: 1.0
  },
  {
    id: 'comfort',
    label: 'Comfort',
    description: 'Premium heritage stays/resorts, dedicated chauffeur, curated dining',
    rateMultiplier: 1.85
  }
];

export const startingCities = [
  'Bengaluru',
  'Mumbai',
  'Delhi NCR',
  'Hyderabad',
  'Chennai',
  'Kolkata',
  'Pune',
  'Ahmedabad',
  'Kochi',
  'Jaipur',
  'Chandigarh',
  'Lucknow',
  'Goa',
  'Indore',
  'Bhopal',
  'Coimbatore',
  'Bhubaneswar',
  'Guwahati',
  'Nagpur',
  'Surat',
  'Visakhapatnam',
  'Trivandrum',
  'Varanasi',
  'Patna',
  'Ranchi'
];
