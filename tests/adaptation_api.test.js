import test from 'node:test';
import assert from 'node:assert/strict';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('FastAPI /api/trips/adapt: reduce_budget toggles optimization and returns updated plan', async () => {
  const planRequest = {
    startingCity: 'Mumbai',
    destinationId: 'hyderabad',
    days: 3,
    budget: 25000,
    interests: ['culture', 'food'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const response = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'reduce_budget',
      planRequest,
    }),
  });

  assert.equal(response.status, 200);
  const data = await response.json();
  assert.equal(data.budgetOptimized, true);
  assert.equal(data.destination.id, 'hyderabad');
  assert.equal(data.numDays, 3);
  assert.equal(data.activeDays.length, 3);
  assert.ok(data.totalEstimatedCost < 15250, 'Cost must be reduced under economy optimization');

  // Verify itemized costs sum to total
  const itemizedTotal = data.accommodationCost + data.foodCost + data.transportCost + data.activitiesCost;
  assert.equal(data.totalEstimatedCost, itemizedTotal);

  // Verify activity items sum to activitiesCost
  const activitySum = data.activeDays.reduce((acc, day) => {
    return acc + day.morning.cost + day.afternoon.cost + day.evening.cost;
  }, 0);
  assert.equal(data.activitiesCost, activitySum);
});

test('FastAPI /api/trips/adapt: shorten_trip reduces days and updates activeDays immediately', async () => {
  const planRequest = {
    startingCity: 'Mumbai',
    destinationId: 'hyderabad',
    days: 3,
    budget: 25000,
    interests: ['culture', 'food'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const response = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'shorten_trip',
      planRequest,
    }),
  });

  assert.equal(response.status, 200);
  const data = await response.json();
  assert.equal(data.numDays, 2);
  assert.equal(data.activeDays.length, 2);
});

test('FastAPI /api/trips/adapt: change_travel_style updates style and rates immediately', async () => {
  const planRequest = {
    startingCity: 'Mumbai',
    destinationId: 'hyderabad',
    days: 3,
    budget: 25000,
    interests: ['culture', 'food'],
    travelStyle: 'balanced',
    budgetOptimized: false,
  };

  const response = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'change_travel_style',
      planRequest,
      newTravelStyle: 'comfort',
    }),
  });

  assert.equal(response.status, 200);
  const data = await response.json();
  assert.equal(data.travelStyle, 'comfort');
  assert.equal(data.dailyStay, 5800);
});
