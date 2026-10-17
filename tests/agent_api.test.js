/**
 * Integration tests for Strands Decider 2B Agent API endpoints.
 */
import test from 'node:test';
import assert from 'node:assert/strict';

const BASE_URL = 'http://127.0.0.1:8000';

test('FastAPI /api/agent/status: returns model and registered Strands tools', async () => {
  const res = await fetch(`${BASE_URL}/api/agent/status`);
  assert.equal(res.status, 200);

  const data = await res.json();
  assert.equal(data.status, 'ok');
  assert.equal(data.model, 'StrandsAgents/strands-decider-2B');
  assert.ok(data.provider, 'Provider status object is present');
  assert.equal(data.registered_tools.length, 5);

  const toolNames = data.registered_tools.map(t => t.name);
  assert.ok(toolNames.includes('optimize_budget'));
  assert.ok(toolNames.includes('adjust_trip_duration'));
  assert.ok(toolNames.includes('adjust_travel_style'));
  assert.ok(toolNames.includes('select_interest_activities'));
  assert.ok(toolNames.includes('validate_trip_constraints'));
});

test('FastAPI /api/agent/plan: handles unavailable provider transparently without faking execution', async () => {
  const payload = {
    user_request: 'Please optimize my 3-day Jaipur trip to fit 12,000 INR',
    destination_id: 'jaipur',
    duration: 3,
    budget: 12000,
    travel_style: 'balanced'
  };

  const res = await fetch(`${BASE_URL}/api/agent/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  assert.equal(res.status, 200);
  const data = await res.json();

  assert.equal(data.model, 'StrandsAgents/strands-decider-2B');
  assert.equal(data.status, 'provider_unavailable');
  assert.equal(data.execution_mode, 'provider_unavailable');
  assert.equal(data.selected_tools.length, 0);
  assert.equal(data.tool_traces.length, 0);
  assert.ok(data.explanation.includes('Strands Decider 2B model server is not connected'));
  assert.ok(data.itinerary, 'Baseline itinerary returned so UI remains functional');
  assert.equal(data.itinerary.destination.id, 'jaipur');
});

test('FastAPI /api/agent/plan: input validation returns HTTP 422 for invalid requests', async () => {
  // Empty user_request (violates min_length=3)
  const resEmpty = await fetch(`${BASE_URL}/api/agent/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_request: 'a'
    }),
  });
  assert.equal(resEmpty.status, 422);

  // Invalid duration (> 30 days)
  const resDuration = await fetch(`${BASE_URL}/api/agent/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_request: 'Plan a 45-day tour',
      duration: 45
    }),
  });
  assert.equal(resDuration.status, 422);
});
