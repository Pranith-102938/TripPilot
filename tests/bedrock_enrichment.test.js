import test from 'node:test';
import assert from 'node:assert/strict';

const BACKEND_URL = 'http://127.0.0.1:8000/api';

test('FastAPI /api/bedrock/status: returns model ID and provider availability status', async () => {
  const response = await fetch(`${BACKEND_URL}/bedrock/status`);
  assert.equal(response.status, 200);
  const data = await response.json();
  assert.ok(['available', 'provider_unavailable'].includes(data.status));
  assert.equal(data.model_id, 'anthropic.claude-3-5-sonnet-20241022-v2:0');
  assert.equal(typeof data.has_credentials, 'boolean');
});

test('FastAPI /api/trips/enrich: preserves all deterministic costs, dates, and activities', async () => {
  // 1. Build a baseline plan
  const planResponse = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Delhi',
      destinationId: 'jaipur',
      days: 3,
      budget: 25000,
      interests: ['heritage', 'culture'],
      travelStyle: 'balanced',
    }),
  });
  assert.equal(planResponse.status, 200);
  const plan = await planResponse.json();

  // 2. Call enrich endpoint
  const enrichResponse = await fetch(`${BACKEND_URL}/trips/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(plan),
  });
  assert.equal(enrichResponse.status, 200);
  const enriched = await enrichResponse.json();

  // 3. Mathematical and structural integrity: absolutely identical
  assert.equal(enriched.destination.id, plan.destination.id);
  assert.equal(enriched.numDays, plan.numDays);
  assert.equal(enriched.activeDays.length, plan.activeDays.length);
  assert.equal(enriched.accommodationCost, plan.accommodationCost);
  assert.equal(enriched.foodCost, plan.foodCost);
  assert.equal(enriched.transportCost, plan.transportCost);
  assert.equal(enriched.activitiesCost, plan.activitiesCost);
  assert.equal(enriched.totalEstimatedCost, plan.totalEstimatedCost);
  assert.equal(enriched.remainingBudget, plan.remainingBudget);
  assert.equal(enriched.isOverBudget, plan.isOverBudget);
  assert.equal(enriched.deficit, plan.deficit);

  // 4. Verify AI enrichment container is attached
  assert.ok(enriched.aiEnrichment);
  assert.ok(['enriched', 'provider_unavailable', 'error'].includes(enriched.aiEnrichment.status));
  assert.equal(enriched.aiEnrichment.modelId, 'anthropic.claude-3-5-sonnet-20241022-v2:0');
});

test('FastAPI /api/bedrock/narrative: accepts request and returns structured invocation result', async () => {
  const response = await fetch(`${BACKEND_URL}/bedrock/narrative`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: 'Munnar',
      durationDays: 3,
      travelStyle: 'balanced',
      highlights: ['Tea Gardens', 'Anamudi Peak'],
    }),
  });
  assert.equal(response.status, 200);
  const data = await response.json();
  assert.ok(['success', 'provider_unavailable', 'error'].includes(data.status));
  assert.equal(data.model_id, 'anthropic.claude-3-5-sonnet-20241022-v2:0');
});

test('FastAPI /api/trips/enrich: handles repeated enrichment calls on adapted itineraries', async () => {
  // Step 1: Initial plan
  const planRes = await fetch(`${BACKEND_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startingCity: 'Bengaluru',
      destinationId: 'munnar',
      days: 4,
      budget: 35000,
      interests: ['nature', 'relaxation'],
      travelStyle: 'comfort',
    }),
  });
  assert.equal(planRes.status, 200);
  const initialPlan = await planRes.json();

  // Step 2: First enrichment
  const firstEnrich = await fetch(`${BACKEND_URL}/trips/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(initialPlan),
  });
  assert.equal(firstEnrich.status, 200);
  const enrichedPlan1 = await firstEnrich.json();

  // Step 3: Adapt the trip (reduce budget)
  const adaptRes = await fetch(`${BACKEND_URL}/trips/adapt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'reduce_budget',
      planRequest: {
        startingCity: 'Bengaluru',
        destinationId: 'munnar',
        days: 4,
        budget: 35000,
        interests: ['nature', 'relaxation'],
        travelStyle: 'comfort',
        budgetOptimized: false,
      },
    }),
  });
  assert.equal(adaptRes.status, 200);
  const adaptedPlan = await adaptRes.json();
  assert.equal(adaptedPlan.budgetOptimized, true);

  // Step 4: Re-enrich the adapted plan
  const secondEnrich = await fetch(`${BACKEND_URL}/trips/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(adaptedPlan),
  });
  assert.equal(secondEnrich.status, 200);
  const enrichedPlan2 = await secondEnrich.json();

  // Verify all deterministic adapted fields are preserved
  assert.equal(enrichedPlan2.budgetOptimized, true);
  assert.equal(enrichedPlan2.totalEstimatedCost, adaptedPlan.totalEstimatedCost);
  assert.equal(enrichedPlan2.accommodationCost, adaptedPlan.accommodationCost);
  assert.ok(enrichedPlan2.aiEnrichment);
});

test('FastAPI /api/trips/enrich: invalid request payload returns HTTP 422 with structured detail', async () => {
  const response = await fetch(`${BACKEND_URL}/trips/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ invalidField: 'missing required fields' }),
  });
  assert.equal(response.status, 422);
  const errJson = await response.json();
  assert.ok(errJson.details || errJson.message || errJson.detail);
});

test('Strands Decider 2B & Bedrock: both providers report honest offline status without crashing or faking inference', async () => {
  // 1. Check Strands agent status
  const agentStatusRes = await fetch(`${BACKEND_URL}/agent/status`);
  assert.equal(agentStatusRes.status, 200);
  const agentStatus = await agentStatusRes.json();
  assert.equal(agentStatus.model, 'StrandsAgents/strands-decider-2B');
  assert.equal(typeof agentStatus.provider.available, 'boolean');

  // 2. Check Bedrock status
  const bedrockStatusRes = await fetch(`${BACKEND_URL}/bedrock/status`);
  assert.equal(bedrockStatusRes.status, 200);
  const bedrockStatus = await bedrockStatusRes.json();
  assert.equal(bedrockStatus.model_id, 'anthropic.claude-3-5-sonnet-20241022-v2:0');
  assert.equal(typeof bedrockStatus.has_credentials, 'boolean');
});

