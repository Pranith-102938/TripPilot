/**
 * TripPilot Frontend API Client
 * Centralized service for communicating with the FastAPI backend.
 */
// Resolve API base URL: supports optional VITE_API_BASE_URL for production while preserving local /api proxy
const RAW_BASE_URL = (import.meta.env?.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
const API_BASE = RAW_BASE_URL
  ? (RAW_BASE_URL.endsWith('/api') ? RAW_BASE_URL : `${RAW_BASE_URL}/api`)
  : '/api';

/**
 * Helper to process API responses and format useful error messages.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' 
          ? errJson.detail 
          : JSON.stringify(errJson.detail);
      } else if (errJson.message) {
        errorDetail = errJson.message;
        if (errJson.details && Array.isArray(errJson.details)) {
          errorDetail += ` (${errJson.details.join(', ')})`;
        }
      }
    } catch {
      // If response body is not JSON, use default status text
      errorDetail = response.statusText || errorDetail;
    }
    const error = new Error(errorDetail);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

/**
 * Wraps fetch calls with friendly offline / connection error detection.
 */
async function apiFetch(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    return await handleResponse(response);
  } catch (err) {
    // Detect network / offline errors
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error(
        'Backend service unreachable. Please ensure the FastAPI server is running on http://127.0.0.1:8000 (run: uvicorn app.main:app --reload in the backend directory).'
      );
    }
    throw err;
  }
}

/**
 * Health check endpoint
 */
export async function checkHealth() {
  return apiFetch('/health');
}

/**
 * Fetch curated destinations with optional search and category filters
 */
export async function fetchDestinations({ search, category } = {}) {
  const params = new URLSearchParams();
  if (search && search.trim()) params.append('search', search.trim());
  if (category && category !== 'all') params.append('category', category);
  const queryStr = params.toString() ? `?${params.toString()}` : '';
  return apiFetch(`/destinations${queryStr}`);
}

/**
 * Fetch a single destination by ID
 */
export async function fetchDestination(destinationId) {
  return apiFetch(`/destinations/${encodeURIComponent(destinationId)}`);
}

/**
 * Request an itinerary and itemized budget from backend
 */
export async function planTrip(tripParams) {
  return apiFetch('/trips/plan', {
    method: 'POST',
    body: JSON.stringify({
      startingCity: tripParams.startingCity,
      destinationId: tripParams.destinationId,
      customDestinationName: tripParams.customDestinationName || null,
      isCustomDestination: Boolean(tripParams.isCustomDestination),
      days: Number(tripParams.days),
      budget: Number(tripParams.budget),
      interests: tripParams.interests,
      travelStyle: tripParams.travelStyle || 'balanced',
      budgetOptimized: Boolean(tripParams.budgetOptimized),
    }),
  });
}

/**
 * Request an adaptive constraint adjustment from backend
 * Supported actions: 'reduce_budget', 'shorten_trip', 'change_travel_style'
 */
export async function adaptTrip({ action, planRequest, newTravelStyle }) {
  return apiFetch('/trips/adapt', {
    method: 'POST',
    body: JSON.stringify({
      action,
      planRequest: {
        startingCity: planRequest.startingCity,
        destinationId: planRequest.destinationId,
        customDestinationName: planRequest.customDestinationName || null,
        isCustomDestination: Boolean(planRequest.isCustomDestination),
        days: Number(planRequest.days),
        budget: Number(planRequest.budget),
        interests: planRequest.interests,
        travelStyle: planRequest.travelStyle || 'balanced',
        budgetOptimized: Boolean(planRequest.budgetOptimized),
      },
      newTravelStyle: newTravelStyle || null,
    }),
  });
}

/**
 * Check Strands Decider 2B Agent status and provider connectivity
 */
export async function fetchAgentStatus() {
  return apiFetch('/agent/status');
}

/**
 * Submit a natural-language planning or adaptation request to Strands Decider 2B Agent
 */
export async function planWithAgent({
  userRequest,
  destinationId,
  destinationName,
  startingCity,
  duration,
  budget,
  travelStyle,
  interests,
  currentItinerary,
}) {
  return apiFetch('/agent/plan', {
    method: 'POST',
    body: JSON.stringify({
      user_request: userRequest,
      destination_id: destinationId || null,
      destination_name: destinationName || null,
      starting_city: startingCity || null,
      duration: duration ? Number(duration) : null,
      budget: budget ? Number(budget) : null,
      travel_style: travelStyle || null,
      interests: interests || null,
      current_itinerary: currentItinerary || null,
    }),
  });
}

/**
 * Check Amazon Bedrock Runtime availability and model configuration
 */
export async function fetchBedrockStatus() {
  return apiFetch('/bedrock/status');
}

/**
 * Request Amazon Bedrock AI enrichment for an existing itinerary
 * Preserves all deterministic costs, dates, activities, and durations.
 */
export async function enrichTrip(itinerary) {
  return apiFetch('/trips/enrich', {
    method: 'POST',
    body: JSON.stringify(itinerary),
  });
}

