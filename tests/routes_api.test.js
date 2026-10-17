import test from 'node:test';
import assert from 'node:assert/strict';

const BACKEND_URL = 'http://127.0.0.1:8000';

test('FastAPI /api/destinations: returns centerCoordinates for curated destinations', async () => {
  const res = await fetch(`${BACKEND_URL}/api/destinations`);
  assert.equal(res.status, 200, 'Expected 200 OK');
  const destinations = await res.json();
  assert.ok(Array.isArray(destinations), 'Expected destinations array');
  assert.ok(destinations.length >= 25, 'Expected at least 25 destinations');

  const hyderabad = destinations.find(d => d.id === 'hyderabad');
  assert.ok(hyderabad, 'Hyderabad must be present');
  assert.ok(hyderabad.centerCoordinates, 'Hyderabad must have centerCoordinates');
  assert.equal(typeof hyderabad.centerCoordinates.lat, 'number');
  assert.equal(typeof hyderabad.centerCoordinates.lng, 'number');
  assert.equal(hyderabad.centerCoordinates.precision, 'city_center');
});

test('FastAPI /api/trips/plan: returns mapCenter, totalRouteDistanceKm, and routeSegments for curated destinations', async () => {
  const planPayload = {
    startingCity: 'Bengaluru',
    destinationId: 'hyderabad',
    days: 3,
    budget: 25000,
    interests: ['heritage'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const res = await fetch(`${BACKEND_URL}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planPayload),
  });

  assert.equal(res.status, 200, 'Expected 200 OK');
  const plan = await res.json();

  assert.ok(plan.mapCenter, 'Expected mapCenter object in response');
  assert.equal(typeof plan.mapCenter.lat, 'number');
  assert.equal(typeof plan.mapCenter.lng, 'number');
  assert.ok(typeof plan.totalRouteDistanceKm === 'number', 'Expected totalRouteDistanceKm');
  assert.ok(plan.totalRouteDistanceKm > 0, 'Total distance should be > 0');

  assert.ok(Array.isArray(plan.activeDays), 'activeDays must be an array');
  const day1 = plan.activeDays[0];
  assert.ok(Array.isArray(day1.routeSegments), 'Expected routeSegments array on day');
  assert.equal(day1.routeSegments.length, 2, 'Expected 2 route segments per day');

  const morningToAfternoon = day1.routeSegments[0];
  assert.equal(morningToAfternoon.fromSlot, 'morning');
  assert.equal(morningToAfternoon.toSlot, 'afternoon');
  assert.equal(morningToAfternoon.isRouteCalculated, true);
  assert.ok(
    ['osrm_road', 'haversine_circuity'].includes(morningToAfternoon.geometrySource),
    `Unexpected geometrySource: ${morningToAfternoon.geometrySource}`
  );
  assert.ok(
    ['road', 'approximate_estimate'].includes(morningToAfternoon.routeType),
    `Unexpected routeType: ${morningToAfternoon.routeType}`
  );
  assert.ok(typeof morningToAfternoon.distanceKm === 'number');
  assert.ok(typeof morningToAfternoon.durationMinutes === 'number');
  assert.ok(Array.isArray(morningToAfternoon.polyline));
  assert.ok(morningToAfternoon.polyline.length >= 2);
});

test('FastAPI /api/trips/plan: custom unverified destination sets mapCenter to null and does not fabricate routes', async () => {
  const customPayload = {
    startingCity: 'Delhi',
    destinationId: 'custom',
    customDestinationName: 'Zanskar Unknown Spot',
    isCustomDestination: true,
    days: 2,
    budget: 15000,
    interests: ['adventure'],
    travelStyle: 'budget',
    budgetOptimized: false,
  };

  const res = await fetch(`${BACKEND_URL}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customPayload),
  });

  assert.equal(res.status, 200, 'Expected 200 OK');
  const plan = await res.json();

  assert.equal(plan.mapCenter, null, 'Unverified destination must have null mapCenter');
  assert.equal(plan.totalRouteDistanceKm, null, 'Unverified destination must have null totalRouteDistanceKm');

  for (const day of plan.activeDays) {
    assert.equal(day.dayRouteDistanceKm, null);
    assert.equal(day.morning.coordinates, null);
    for (const seg of day.routeSegments) {
      assert.equal(seg.isRouteCalculated, false);
      assert.equal(seg.geometrySource, 'unavailable');
      assert.equal(seg.routeType, 'unavailable');
      assert.equal(seg.distanceKm, null);
      assert.equal(seg.polyline, null);
    }
  }
});

test('FastAPI /api/trips/adapt: adapts trip plan while preserving route segment data and mapCenter', async () => {
  const adaptPayload = {
    action: 'change_travel_style',
    newTravelStyle: 'comfort',
    planRequest: {
      startingCity: 'Mumbai',
      destinationId: 'jaipur',
      days: 3,
      budget: 35000,
      interests: ['culture'],
      travelStyle: 'balanced',
      budgetOptimized: false,
    },
  };

  const res = await fetch(`${BACKEND_URL}/api/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(adaptPayload),
  });

  assert.equal(res.status, 200, 'Expected 200 OK');
  const adapted = await res.json();

  assert.equal(adapted.travelStyle, 'comfort');
  assert.ok(adapted.mapCenter, 'Expected mapCenter to be preserved');
  assert.ok(adapted.totalRouteDistanceKm > 0, 'Expected route distance to be calculated');
  assert.ok(adapted.activeDays[0].routeSegments.length > 0);
  assert.equal(adapted.activeDays[0].routeSegments[0].isRouteCalculated, true);
  assert.ok(['osrm_road', 'haversine_circuity'].includes(adapted.activeDays[0].routeSegments[0].geometrySource));
});

test('FastAPI /api/trips/plan: route segments include transparent traffic disclosures and route types', async () => {
  const planPayload = {
    startingCity: 'Delhi',
    destinationId: 'jaipur',
    days: 2,
    budget: 20000,
    interests: ['culture'],
    travelStyle: 'budget',
    budgetOptimized: false,
  };

  const res = await fetch(`${BACKEND_URL}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planPayload),
  });

  assert.equal(res.status, 200);
  const plan = await res.json();

  const segment = plan.activeDays[0].routeSegments[0];
  assert.ok(segment.isRouteCalculated);
  assert.ok(segment.trafficNotice, 'Expected trafficNotice disclosure');
  if (segment.routeType === 'road') {
    assert.equal(segment.geometrySource, 'osrm_road');
    assert.ok(segment.trafficNotice.includes('Static road network'));
  } else {
    assert.equal(segment.geometrySource, 'haversine_circuity');
    assert.ok(segment.trafficNotice.includes('circuity estimate'));
  }
});
