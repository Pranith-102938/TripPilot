import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateBudgetBreakdown } from '../src/data/sampleItineraries.js';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('calculateBudgetBreakdown: populates daily cost breakdown matching total trip cost', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 4,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 35000
  });

  assert.equal(result.activeDays.length, 4);

  let sumDayStay = 0;
  let sumDayFood = 0;
  let sumDayTransit = 0;
  let sumDayActivities = 0;
  let sumDayTotal = 0;

  for (const day of result.activeDays) {
    assert.equal(typeof day.dayStay, 'number');
    assert.equal(typeof day.dayFood, 'number');
    assert.equal(typeof day.dayTransit, 'number');
    assert.equal(typeof day.dayActivities, 'number');
    assert.equal(typeof day.dayTotal, 'number');

    assert.equal(day.dayTotal, day.dayStay + day.dayFood + day.dayTransit + day.dayActivities);

    sumDayStay += day.dayStay;
    sumDayFood += day.dayFood;
    sumDayTransit += day.dayTransit;
    sumDayActivities += day.dayActivities;
    sumDayTotal += day.dayTotal;
  }

  assert.equal(sumDayStay, result.accommodationCost);
  assert.equal(sumDayFood, result.foodCost);
  assert.equal(sumDayTransit, result.transportCost);
  assert.equal(sumDayActivities, result.activitiesCost);
  assert.equal(sumDayTotal, result.totalEstimatedCost);
});

test('calculateBudgetBreakdown: activeDays have duration, practicalTips, mealSuggestion, and transitNote', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'jaipur',
    days: 7,
    travelStyle: 'comfort',
    budgetOptimized: false,
    userBudget: 60000
  });

  assert.equal(result.activeDays.length, 7);

  for (const day of result.activeDays) {
    assert.ok(day.theme, 'Day must have a theme');
    for (const slotKey of ['morning', 'afternoon', 'evening']) {
      const slot = day[slotKey];
      assert.ok(slot.title, `${slotKey} must have a title`);
      assert.ok(slot.location, `${slotKey} must have a location`);
      assert.ok(slot.duration, `${slotKey} must have a duration`);
      assert.ok(slot.practicalTips, `${slotKey} must have practicalTips`);
      assert.ok(slot.mealSuggestion, `${slotKey} must have mealSuggestion`);
      assert.ok(slot.transitNote, `${slotKey} must have transitNote`);
      assert.equal(typeof slot.cost, 'number');
    }
  }
});

test('FastAPI /api/trips/plan: returns detailed schedules, daily breakdowns, and transit notes', async () => {
  const res = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Bengaluru',
      destinationId: 'munnar',
      days: 3,
      budget: 30000,
      interests: ['nature', 'relaxation'],
      travelStyle: 'balanced',
      budgetOptimized: false
    })
  });

  assert.equal(res.status, 200);
  const data = await res.json();

  assert.equal(data.activeDays.length, 3);
  let totalDailyCostSum = 0;

  for (const day of data.activeDays) {
    assert.ok(day.theme);
    assert.equal(day.dayTotal, day.dayStay + day.dayFood + day.dayTransit + day.dayActivities);
    totalDailyCostSum += day.dayTotal;

    for (const slotKey of ['morning', 'afternoon', 'evening']) {
      const slot = day[slotKey];
      assert.ok(slot.title);
      assert.ok(slot.duration);
      assert.ok(slot.practicalTips);
      assert.ok(slot.mealSuggestion);
      assert.ok(slot.transitNote);
    }
  }

  assert.equal(totalDailyCostSum, data.totalEstimatedCost);
});

test('FastAPI /api/trips/adapt: preserves detailed schedule properties when adapting', async () => {
  const adaptRes = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'reduce_budget',
      planRequest: {
        startingCity: 'Chennai',
        destinationId: 'goa',
        days: 2,
        budget: 20000,
        interests: ['beaches'],
        travelStyle: 'balanced',
        budgetOptimized: false
      }
    })
  });

  assert.equal(adaptRes.status, 200);
  const adapted = await adaptRes.json();

  assert.equal(adapted.activeDays.length, 2);
  assert.equal(adapted.budgetOptimized, true);

  for (const day of adapted.activeDays) {
    assert.equal(day.dayTotal, day.dayStay + day.dayFood + day.dayTransit + day.dayActivities);
    for (const slotKey of ['morning', 'afternoon', 'evening']) {
      const slot = day[slotKey];
      assert.ok(slot.duration);
      assert.ok(slot.practicalTips);
      assert.ok(slot.mealSuggestion);
      assert.ok(slot.transitNote);
    }
  }
});
