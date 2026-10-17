# TripPilot — Backend Service (Phase 2)

FastAPI backend service powering deterministic trip planning, budget calculations, and constraint adaptations for TripPilot.

> [!NOTE]
> **Phase 2 Status:** The backend uses deterministic regional benchmarks to calculate day-by-day itineraries and itemized budgets with mathematical precision. AI-powered decision making via **Strands Decider 2B** and **Amazon Bedrock** is scheduled for Phase 3.

---

## 1. Prerequisites

- **Python:** 3.11 or 3.12 (tested on Python 3.12)
- **pip:** 24.0 or higher
- **PowerShell:** on Windows 10/11

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── __init__.py           # Application package
│   ├── main.py               # FastAPI entrypoint, endpoints, and CORS
│   ├── models.py             # Pydantic request/response schemas
│   ├── data.py               # Curated Indian destinations & sample itineraries
│   └── services/
│       ├── __init__.py       # Services package
│       └── trip_planner.py   # Planning engine, budget math, and adaptive actions
├── tests/
│   ├── __init__.py           # Test package
│   └── test_api.py           # Pytest test suite (14 test cases)
├── requirements.txt          # Python dependencies
└── README.md                 # Backend documentation
```

---

## 3. Virtual Environment & Setup (Windows PowerShell)

Open Windows PowerShell and navigate to the project directory:

```powershell
cd "d:\AWS_hackathon - TripPilot\backend"

# 1. Create a Python virtual environment (if not already created)
python -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# If script execution is disabled, enable it for current process:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# 3. Upgrade pip and install dependencies
pip install -r requirements.txt
```

---

## 4. Running the Development Server

With the virtual environment activated:

```powershell
# From the backend directory
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The server will be accessible at:
- **API Base:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## 5. API Endpoints & Sample Requests

### 1. Health Check
- **Endpoint:** `GET /api/health`
- **Description:** Verifies service health without claiming AI integration.
- **Example Response:**
  ```json
  {
    "status": "ok",
    "app": "TripPilot Backend",
    "version": "1.0.0",
    "phase": "Phase 2 - FastAPI Backend Foundation",
    "ai_connected": false,
    "message": "FastAPI backend running. AI integrations scheduled for Phase 3."
  }
  ```

### 2. Destination Discovery
- **Endpoint:** `GET /api/destinations`
- **Description:** Returns all curated destinations in India (Hyderabad, Goa, Jaipur, Munnar).

- **Endpoint:** `GET /api/destinations/{destination_id}`
- **Description:** Returns single destination metadata or `HTTP 404` if not found.

### 3. Generate Trip Plan
- **Endpoint:** `POST /api/trips/plan`
- **Sample Request:**
  ```json
  {
    "startingCity": "Bengaluru",
    "destinationId": "hyderabad",
    "days": 3,
    "budget": 30000,
    "interests": ["culture", "food"],
    "travelStyle": "balanced",
    "budgetOptimized": false
  }
  ```
- **Sample Response:**
  ```json
  {
    "destination": {
      "id": "hyderabad",
      "name": "Hyderabad",
      "state": "Telangana"
    },
    "itineraryTitle": "Nizami Grandeur & Culinary Trail",
    "numDays": 3,
    "activeDays": [...],
    "travelStyle": "balanced",
    "budgetOptimized": false,
    "accommodationCost": 8400,
    "foodCost": 3600,
    "transportCost": 2400,
    "activitiesCost": 2200,
    "totalEstimatedCost": 16600,
    "userBudget": 30000.0,
    "remainingBudget": 13400.0,
    "isOverBudget": false,
    "deficit": 0.0,
    "isSample": true
  }
  ```

### 4. Adaptive Planning
- **Endpoint:** `POST /api/trips/adapt`
- **Supported Actions:** `reduce_budget`, `shorten_trip`, `change_travel_style`
- **Sample Request (Reduce Budget):**
  ```json
  {
    "action": "reduce_budget",
    "planRequest": {
      "startingCity": "Bengaluru",
      "destinationId": "hyderabad",
      "days": 3,
      "budget": 30000,
      "interests": ["culture"],
      "travelStyle": "balanced",
      "budgetOptimized": false
    }
  }
  ```
- **Sample Request (Change Style):**
  ```json
  {
    "action": "change_travel_style",
    "planRequest": { ... },
    "newTravelStyle": "comfort"
  }
  ```

---

## 6. Running Backend Tests

Run the complete test suite with `pytest`:

```powershell
cd "d:\AWS_hackathon - TripPilot\backend"
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v
```

All 14 tests verify:
- Health response content
- Destination listing and lookup
- Validation rules and limits (budget >= 5000, days >= 1)
- Budget surplus and deficit calculations
- Mathematical consistency (`accommodation + food + transit + activities == total`)
- Adaptation rules (`reduce_budget`, `shorten_trip`, `change_travel_style`)
- 422 error handling for unsupported actions
