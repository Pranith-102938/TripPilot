import test from 'node:test';
import assert from 'node:assert/strict';
import { destinations, filterDestinations, startingCities, hillStationIds, exploreCategories } from '../src/data/destinations.js';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('Frontend Destinations: contains >= 20 curated destinations across Indian regions', () => {
  assert.ok(destinations.length >= 20, `Expected at least 20 destinations, got ${destinations.length}`);
  
  // Verify mandatory schema fields on all destinations
  for (const dest of destinations) {
    assert.ok(dest.id, 'Destination must have an id');
    assert.ok(dest.name, `Destination ${dest.id} must have a name`);
    assert.ok(dest.state, `Destination ${dest.id} must have a state`);
    assert.ok(dest.tagline, `Destination ${dest.id} must have a tagline`);
    assert.ok(dest.description, `Destination ${dest.id} must have a description`);
    assert.ok(dest.indicativeRange, `Destination ${dest.id} must have an indicativeRange`);
    assert.ok(dest.bestTimeToVisit, `Destination ${dest.id} must have a bestTimeToVisit`);
    assert.ok(Array.isArray(dest.highlights) && dest.highlights.length >= 3, `Destination ${dest.id} must have >= 3 highlights`);
    assert.ok(dest.indicativeDailyCost?.budget, `Destination ${dest.id} must have budget cost`);
    assert.ok(dest.indicativeDailyCost?.balanced, `Destination ${dest.id} must have balanced cost`);
    assert.ok(dest.indicativeDailyCost?.comfort, `Destination ${dest.id} must have comfort cost`);
  }
});

test('filterDestinations: search by destination name, state, and highlights', () => {
  // Search by name
  const goaResults = filterDestinations(destinations, { search: 'goa' });
  assert.ok(goaResults.some(d => d.id === 'goa'));

  // Search by state
  const keralaResults = filterDestinations(destinations, { search: 'Kerala' });
  assert.ok(keralaResults.length >= 2, 'Kerala should have multiple destinations');
  assert.ok(keralaResults.every(d => d.state.toLowerCase().includes('kerala')));

  // Search case insensitivity
  const jaipurUpper = filterDestinations(destinations, { search: 'JAIPUR' });
  assert.equal(jaipurUpper[0]?.id, 'jaipur');
});

test('filterDestinations: category filtering returns correct subsets', () => {
  // Beaches
  const beaches = filterDestinations(destinations, { category: 'beaches' });
  assert.ok(beaches.length >= 2);
  assert.ok(beaches.some(d => d.id === 'goa'));

  // Hill stations
  const hills = filterDestinations(destinations, { category: 'hills' });
  assert.ok(hills.length >= 3);
  assert.ok(hills.some(d => d.id === 'munnar'));

  // Heritage
  const heritage = filterDestinations(destinations, { category: 'heritage' });
  assert.ok(heritage.length >= 3);
  assert.ok(heritage.some(d => d.id === 'jaipur' || d.id === 'hyderabad'));

  // Nature
  const nature = filterDestinations(destinations, { category: 'nature' });
  assert.ok(nature.length >= 3);

  // All category returns full dataset
  const all = filterDestinations(destinations, { category: 'all' });
  assert.equal(all.length, destinations.length);
});

test('Starting Cities: includes comprehensive list of major Indian hubs', () => {
  assert.ok(startingCities.length >= 20);
  assert.ok(startingCities.includes('Bengaluru'));
  assert.ok(startingCities.includes('Mumbai'));
  assert.ok(startingCities.includes('Delhi NCR'));
  assert.ok(startingCities.includes('Hyderabad'));
  assert.ok(startingCities.includes('Kochi'));
});

test('FastAPI /api/destinations: supports search and category query params', async () => {
  // Query all
  const resAll = await fetch(`${BACKEND_URL}/destinations`);
  assert.equal(resAll.status, 200);
  const dataAll = await resAll.json();
  assert.ok(dataAll.length >= 20);

  // Search query
  const resSearch = await fetch(`${BACKEND_URL}/destinations?search=rajasthan`);
  assert.equal(resSearch.status, 200);
  const dataSearch = await resSearch.json();
  assert.ok(dataSearch.length >= 2);
  assert.ok(dataSearch.every(d => d.state.toLowerCase().includes('rajasthan') || d.name.toLowerCase().includes('rajasthan')));

  // Category query
  const resCategory = await fetch(`${BACKEND_URL}/destinations?category=hills`);
  assert.equal(resCategory.status, 200);
  const dataCategory = await resCategory.json();
  assert.ok(dataCategory.length >= 3);
});

test('FastAPI /api/trips/plan: plan from Explore card with custom starting city', async () => {
  const planRequest = {
    startingCity: 'Chandigarh',
    destinationId: 'manali',
    days: 3,
    budget: 30000,
    interests: ['nature', 'adventure'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const response = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planRequest),
  });

  assert.equal(response.status, 200);
  const plan = await response.json();
  assert.equal(plan.destination.id, 'manali');
  assert.equal(plan.startingCity, 'Chandigarh');
  assert.equal(plan.numDays, 3);
  assert.equal(plan.isVerified, true);
  assert.equal(plan.activeDays.length, 3);
  assert.ok(plan.totalEstimatedCost > 0);
  assert.ok(plan.remainingBudget >= 0);
});

test('FastAPI /api/trips/plan: manual unverified destination indicates limited data', async () => {
  const planRequest = {
    startingCity: 'Pune',
    destinationId: 'custom',
    customDestinationName: 'Dhanushkodi',
    isCustomDestination: true,
    days: 2,
    budget: 18000,
    interests: ['nature', 'relaxation'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const response = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planRequest),
  });

  assert.equal(response.status, 200);
  const plan = await response.json();
  assert.equal(plan.isVerified, false);
  assert.equal(plan.destination.name, 'Dhanushkodi');
  assert.equal(plan.activitiesCost, 0, 'Unverified destination should not fabricate attraction admission fees');
  assert.ok(plan.itinerarySummary.toLowerCase().includes('unverified') || plan.itinerarySummary.toLowerCase().includes('limited'));
});
