import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateBudgetBreakdown } from '../src/data/sampleItineraries.js';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('calculateBudgetBreakdown: 1-day trip generation and cost calculation', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 1,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 15000
  });

  assert.equal(result.numDays, 1);
  assert.equal(result.activeDays.length, 1);
  assert.equal(result.activeDays[0].dayNumber, 1);
  assert.equal(result.accommodationCost, result.dailyStay * 1);
  assert.equal(result.foodCost, result.dailyFood * 1);
  assert.equal(result.transportCost, result.dailyTransit * 1);
  assert.equal(result.totalEstimatedCost, result.accommodationCost + result.foodCost + result.transportCost + result.activitiesCost);
  assert.equal(result.remainingBudget, 15000 - result.totalEstimatedCost);
});

test('calculateBudgetBreakdown: 3-day trip generation and mathematical integrity', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'goa',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 25000
  });

  assert.equal(result.numDays, 3);
  assert.equal(result.activeDays.length, 3);
  assert.deepEqual(result.activeDays.map(d => d.dayNumber), [1, 2, 3]);
  assert.equal(result.accommodationCost, result.dailyStay * 3);
  assert.equal(result.foodCost, result.dailyFood * 3);
  assert.equal(result.transportCost, result.dailyTransit * 3);
  assert.equal(result.totalEstimatedCost, result.accommodationCost + result.foodCost + result.transportCost + result.activitiesCost);
});

test('calculateBudgetBreakdown: 7-day trip generation with distinct non-duplicated schedules', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'jaipur',
    days: 7,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 50000
  });

  assert.equal(result.numDays, 7);
  assert.equal(result.activeDays.length, 7);
  assert.deepEqual(result.activeDays.map(d => d.dayNumber), [1, 2, 3, 4, 5, 6, 7]);

  // Ensure all 7 daily themes are distinct
  const themes = result.activeDays.map(d => d.theme);
  assert.equal(new Set(themes).size, 7, 'All 7 daily themes must be distinct');

  // Mathematical integrity
  assert.equal(result.accommodationCost, result.dailyStay * 7);
  assert.equal(result.foodCost, result.dailyFood * 7);
  assert.equal(result.transportCost, result.dailyTransit * 7);
  assert.equal(result.totalEstimatedCost, result.accommodationCost + result.foodCost + result.transportCost + result.activitiesCost);
});

test('calculateBudgetBreakdown: 14-day trip generation with distinct non-duplicated schedules', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'munnar',
    days: 14,
    travelStyle: 'comfort',
    budgetOptimized: false,
    userBudget: 100000
  });

  assert.equal(result.numDays, 14);
  assert.equal(result.activeDays.length, 14);
  assert.deepEqual(result.activeDays.map(d => d.dayNumber), Array.from({ length: 14 }, (_, i) => i + 1));

  // Ensure all 14 daily themes are distinct
  const themes = result.activeDays.map(d => d.theme);
  assert.equal(new Set(themes).size, 14, 'All 14 daily themes must be distinct');

  // Mathematical integrity
  assert.equal(result.accommodationCost, result.dailyStay * 14);
  assert.equal(result.foodCost, result.dailyFood * 14);
  assert.equal(result.transportCost, result.dailyTransit * 14);
  assert.equal(result.totalEstimatedCost, result.accommodationCost + result.foodCost + result.transportCost + result.activitiesCost);
});

test('calculateBudgetBreakdown: shortening custom duration updates activeDays and costs', () => {
  const sevenDays = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 7,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 50000
  });

  const sixDays = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 6,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 50000
  });

  assert.equal(sixDays.numDays, 6);
  assert.equal(sixDays.activeDays.length, 6);
  assert.ok(sixDays.totalEstimatedCost < sevenDays.totalEstimatedCost);
  assert.equal(sixDays.accommodationCost, sixDays.dailyStay * 6);
});

test('FastAPI /api/trips/plan: 1-day, 3-day, 7-day, and 14-day trips via API', async () => {
  for (const days of [1, 3, 7, 14]) {
    const res = await fetch(`${BACKEND_URL}/trips/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        startingCity: 'Bengaluru',
        destinationId: 'hyderabad',
        days,
        budget: 60000,
        interests: ['culture', 'food'],
        travelStyle: 'balanced',
        budgetOptimized: false
      })
    });

    assert.equal(res.status, 200, `Expected 200 for days=${days}`);
    const data = await res.json();
    assert.equal(data.numDays, days);
    assert.equal(data.activeDays.length, days);
    assert.equal(data.accommodationCost, data.dailyStay * days);
    assert.equal(data.foodCost, data.dailyFood * days);
    assert.equal(data.transportCost, data.dailyTransit * days);
    assert.equal(data.totalEstimatedCost, data.accommodationCost + data.foodCost + data.transportCost + data.activitiesCost);
  }
});

test('FastAPI /api/trips/plan: invalid durations (0, -1, 31) return HTTP 422', async () => {
  for (const invalidDays of [0, -1, -10, 31, 50]) {
    const res = await fetch(`${BACKEND_URL}/trips/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        startingCity: 'Delhi',
        destinationId: 'jaipur',
        days: invalidDays,
        budget: 30000,
        interests: ['culture'],
        travelStyle: 'balanced',
        budgetOptimized: false
      })
    });

    assert.equal(res.status, 422, `Expected 422 for invalid days=${invalidDays}`);
  }
});

test('FastAPI /api/trips/adapt: shortening trip with custom duration and 1-day boundary', async () => {
  // Shorten 7-day trip to 6 days
  const res7 = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'shorten_trip',
      planRequest: {
        startingCity: 'Mumbai',
        destinationId: 'goa',
        days: 7,
        budget: 50000,
        interests: ['beaches'],
        travelStyle: 'balanced',
        budgetOptimized: false
      }
    })
  });

  assert.equal(res7.status, 200);
  const data7 = await res7.json();
  assert.equal(data7.numDays, 6);
  assert.equal(data7.activeDays.length, 6);

  // Attempting to shorten 1-day trip fails with 422
  const res1 = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'shorten_trip',
      planRequest: {
        startingCity: 'Mumbai',
        destinationId: 'goa',
        days: 1,
        budget: 15000,
        interests: ['beaches'],
        travelStyle: 'balanced',
        budgetOptimized: false
      }
    })
  });

  assert.equal(res1.status, 422);
});
