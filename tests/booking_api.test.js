import test from 'node:test';
import assert from 'node:assert/strict';
import { sampleItineraries, calculateBudgetBreakdown } from '../src/data/sampleItineraries.js';

const BACKEND_BASE_URL = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

test('FastAPI /api/trips/plan: returns verified bookingResource on curated landmarks', async () => {
  const res = await fetch(`${BACKEND_BASE_URL}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destinationId: 'hyderabad',
      days: 3,
      budget: 35000,
      travelStyle: 'balanced',
      startingCity: 'Mumbai',
      interests: ['heritage']
    })
  });

  assert.strictEqual(res.status, 200);
  const data = await res.json();
  const day1Morning = data.activeDays[0].morning;

  assert.ok(day1Morning.bookingResource, 'Day 1 morning must have bookingResource');
  assert.strictEqual(day1Morning.bookingResource.url, 'https://asi.nic.in/');
  assert.ok(day1Morning.bookingResource.providerName.includes('Archaeological Survey of India'));
  assert.strictEqual(day1Morning.bookingResource.isVerified, true);
});

test('FastAPI /api/trips/plan: stops without verified advance portals have bookingResource null', async () => {
  const res = await fetch(`${BACKEND_BASE_URL}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destinationId: 'goa',
      days: 2,
      budget: 25000,
      travelStyle: 'balanced',
      startingCity: 'Delhi',
      interests: ['beach']
    })
  });

  assert.strictEqual(res.status, 200);
  const data = await res.json();
  const day1Evening = data.activeDays[0].evening; // Miramar Beach (public)

  assert.strictEqual(day1Evening.bookingResource, null);
});

test('FastAPI /api/trips/adapt: preserves bookingResource after adaptation actions', async () => {
  const adaptPayload = {
    action: 'shorten_trip',
    planRequest: {
      startingCity: 'Jaipur',
      destinationId: 'jaipur',
      days: 3,
      budget: 40000,
      interests: ['culture'],
      travelStyle: 'balanced',
      budgetOptimized: false
    }
  };

  const adaptRes = await fetch(`${BACKEND_BASE_URL}/api/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(adaptPayload)
  });

  assert.strictEqual(adaptRes.status, 200);
  const adapted = await adaptRes.json();
  assert.strictEqual(adapted.numDays, 2);

  // Amber Palace (Day 1 morning) and City Palace (Day 2 morning) must retain booking portals
  assert.ok(adapted.activeDays[0].morning.bookingResource);
  assert.strictEqual(adapted.activeDays[0].morning.bookingResource.url, 'https://www.tourism.rajasthan.gov.in/');
  assert.ok(adapted.activeDays[1].morning.bookingResource);
  assert.strictEqual(adapted.activeDays[1].morning.bookingResource.url, 'https://thecitypalacejaipur.com/');
});

test('Frontend calculateBudgetBreakdown: client-side activeDays include verified booking resources', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 30000
  });

  assert.strictEqual(result.activeDays.length, 3);
  const day1Morning = result.activeDays[0].morning;
  assert.ok(day1Morning.bookingResource);
  assert.strictEqual(day1Morning.bookingResource.url, 'https://asi.nic.in/');

  // Free/unverified stop
  const day1Evening = result.activeDays[0].evening;
  assert.ok(day1Evening.bookingResource); // Chowmahalla Palace has official tourism link
  const day1Afternoon = result.activeDays[0].afternoon;
  assert.strictEqual(day1Afternoon.bookingResource, undefined); // Shadab restaurant
});
