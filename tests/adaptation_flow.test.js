import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateBudgetBreakdown } from '../src/data/sampleItineraries.js';

test('calculateBudgetBreakdown: standard calculation has correct categories and sums', () => {
  const result = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 25000
  });

  assert.equal(result.numDays, 3);
  assert.equal(result.budgetOptimized, false);
  assert.equal(result.activeDays.length, 3);

  // Mathematical integrity
  const total = result.accommodationCost + result.foodCost + result.transportCost + result.activitiesCost;
  assert.equal(result.totalEstimatedCost, total);
  assert.equal(result.remainingBudget, 25000 - total);

  // Activities sum check
  const activitySum = result.activeDays.reduce((acc, day) => {
    return acc + day.morning.cost + day.afternoon.cost + day.evening.cost;
  }, 0);
  assert.equal(result.activitiesCost, activitySum);
});

test('calculateBudgetBreakdown: economy rates reduce costs and update activeDays items', () => {
  const standard = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 25000
  });

  const economy = calculateBudgetBreakdown({
    destinationId: 'hyderabad',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: true,
    userBudget: 25000
  });

  assert.equal(economy.budgetOptimized, true);
  assert.ok(economy.totalEstimatedCost < standard.totalEstimatedCost, 'Economy total must be less than standard');
  assert.ok(economy.activitiesCost < standard.activitiesCost, 'Activities cost must be discounted');

  // Verify activity items in activeDays match economy activitiesCost
  const economyActivitySum = economy.activeDays.reduce((acc, day) => {
    return acc + day.morning.cost + day.afternoon.cost + day.evening.cost;
  }, 0);
  assert.equal(economy.activitiesCost, economyActivitySum);

  // Verify Day 1 morning activity is discounted
  assert.equal(standard.activeDays[0].morning.cost, 150);
  assert.equal(economy.activeDays[0].morning.cost, 128); // round(150 * 0.85)
});

test('calculateBudgetBreakdown: shortening trip recalculates days and costs', () => {
  const threeDays = calculateBudgetBreakdown({
    destinationId: 'munnar',
    days: 3,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 30000
  });

  const twoDays = calculateBudgetBreakdown({
    destinationId: 'munnar',
    days: 2,
    travelStyle: 'balanced',
    budgetOptimized: false,
    userBudget: 30000
  });

  assert.equal(twoDays.numDays, 2);
  assert.equal(twoDays.activeDays.length, 2);
  assert.ok(twoDays.totalEstimatedCost < threeDays.totalEstimatedCost);
});

test('calculateBudgetBreakdown: changing travel style adjusts rates appropriately', () => {
  const budgetStyle = calculateBudgetBreakdown({
    destinationId: 'jaipur',
    days: 3,
    travelStyle: 'budget',
    budgetOptimized: false,
    userBudget: 25000
  });

  const comfortStyle = calculateBudgetBreakdown({
    destinationId: 'jaipur',
    days: 3,
    travelStyle: 'comfort',
    budgetOptimized: false,
    userBudget: 25000
  });

  assert.ok(budgetStyle.totalEstimatedCost < comfortStyle.totalEstimatedCost);
  assert.ok(budgetStyle.dailyStay < comfortStyle.dailyStay);
});
