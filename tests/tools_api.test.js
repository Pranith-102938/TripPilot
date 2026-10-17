import test from 'node:test';
import assert from 'node:assert/strict';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('FastAPI /api/tools/validate-constraints: flags budget conflict and duration limits', async () => {
  // Test 1: budget conflict
  const res1 = await fetch(`${BACKEND_URL}/tools/validate-constraints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: 'goa',
      days: 5,
      budget: 4500,
      travelStyle: 'comfort'
    })
  });
  assert.equal(res1.status, 200);
  const data1 = await res1.json();
  assert.equal(data1.isValid, false);
  assert.ok(data1.conflictsDetected.some(c => c.includes('Budget Deficit Conflict')));
  assert.ok(data1.recommendations.length > 0);

  // Test 2: valid plan
  const res2 = await fetch(`${BACKEND_URL}/tools/validate-constraints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: 'jaipur',
      days: 3,
      budget: 25000,
      travelStyle: 'balanced',
      interests: ['culture']
    })
  });
  assert.equal(res2.status, 200);
  const data2 = await res2.json();
  assert.equal(data2.isValid, true);
  assert.equal(data2.errors.length, 0);
});

test('FastAPI /api/tools/select-activities: returns curated rationale and activity matches', async () => {
  const res = await fetch(`${BACKEND_URL}/tools/select-activities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: 'hyderabad',
      interests: ['food', 'culture'],
      days: 2
    })
  });

  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.isCurated, true);
  assert.equal(data.destinationId, 'hyderabad');
  assert.equal(data.selectedActivities.length, 6);
  assert.ok(data.rationaleSummary.includes('hyderabad') || data.rationaleSummary.includes('Hyderabad'));
});

test('FastAPI /api/tools/adjust-duration: extends itinerary to 6 days with distinct schedules', async () => {
  // 1. Get base plan
  const planRes = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Bengaluru',
      destinationId: 'hyderabad',
      days: 3,
      budget: 30000,
      interests: ['culture'],
      travelStyle: 'balanced'
    })
  });
  const plan = await planRes.json();

  // 2. Adjust duration to 6 days via tool
  const adjRes = await fetch(`${BACKEND_URL}/tools/adjust-duration`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      itinerary: plan,
      target_days: 6
    })
  });

  assert.equal(adjRes.status, 200);
  const adjData = await adjRes.json();
  assert.equal(adjData.original_days, 3);
  assert.equal(adjData.target_days, 6);
  assert.equal(adjData.action_taken, 'extended');
  assert.equal(adjData.revised_itinerary.numDays, 6);

  const themes = adjData.revised_itinerary.activeDays.map(d => d.theme);
  assert.equal(new Set(themes).size, 6);
});

test('FastAPI /api/tools/adjust-travel-style: changes rates from balanced to comfort', async () => {
  const planRes = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Mumbai',
      destinationId: 'goa',
      days: 3,
      budget: 35000,
      interests: ['beaches'],
      travelStyle: 'balanced'
    })
  });
  const plan = await planRes.json();

  const styleRes = await fetch(`${BACKEND_URL}/tools/adjust-travel-style`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      itinerary: plan,
      target_style: 'comfort'
    })
  });

  assert.equal(styleRes.status, 200);
  const styleData = await styleRes.json();
  assert.equal(styleData.original_style, 'balanced');
  assert.equal(styleData.target_style, 'comfort');
  assert.ok(styleData.cost_delta > 0);
  assert.equal(styleData.revised_itinerary.travelStyle, 'comfort');
});

test('FastAPI /api/tools/optimize-budget: clears deficit or reports unfeasible budget honestly', async () => {
  const planRes = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Bengaluru',
      destinationId: 'hyderabad',
      days: 4,
      budget: 35000,
      interests: ['culture'],
      travelStyle: 'comfort'
    })
  });
  const plan = await planRes.json();

  // Test feasible target budget
  const optRes = await fetch(`${BACKEND_URL}/tools/optimize-budget`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      itinerary: plan,
      target_budget: plan.totalEstimatedCost - 3000
    })
  });

  assert.equal(optRes.status, 200);
  const optData = await optRes.json();
  assert.equal(optData.fits_budget, true);
  assert.equal(optData.final_deficit, 0);

  // Test impossible target budget (e.g. ₹2,000 for 4 days)
  const impossibleRes = await fetch(`${BACKEND_URL}/tools/optimize-budget`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      itinerary: plan,
      target_budget: 2000
    })
  });

  assert.equal(impossibleRes.status, 200);
  const impData = await impossibleRes.json();
  assert.equal(impData.fits_budget, false);
  assert.ok(impData.final_deficit > 0);
  assert.ok(impData.explanation.toLowerCase().includes('minimum feasible cost') || impData.explanation.toLowerCase().includes('deficit'));
});
