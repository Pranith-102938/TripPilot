# TripPilot — Phase 4: Strands Agents SDK & Decider 2B Integration

TripPilot is an intelligent travel-planning workspace designed to craft balanced, realistic daily itineraries across Indian destinations with strict budget adherence.

> [!IMPORTANT]
> **Phase 4 Implementation Notice**  
> This release provides **Phase 4: Strands Agents SDK & Decider 2B Integration** — connecting an autonomous agent powered by the **Strands Decider 2B** decision model (`StrandsAgents/strands-decider-2B`) for genuine tool selection.
> The agent registers all five planning tools with the official Strands SDK `@tool` decorator, evaluates user requests using `SystemOneRequest` choice schemas with calibrated confidence, executes tools sequentially, and updates the itinerary.
> **Strict AI Honesty**: If the Decider 2B inference endpoint is unconfigured or offline, TripPilot transparently surfaces provider status without simulating or falsely claiming AI reasoning.

---

## 1. Overview & Visual Identity

TripPilot departs from cookie-cutter travel templates and generic AI chat interfaces. It embraces a refined editorial visual identity:
- **Warm off-white background** (`#F8F6F0`) paired with subtle parchment cards (`#FFFFFF`, `#F3EFE8`).
- **Deep forest green** (`#132C24`, `#1A3D32`, `#2E6652`) as the grounding primary accent.
- **Charcoal typography** (`#171A19`, `#383E3B`) with strong contrast and readable hierarchy using *Plus Jakarta Sans* and *Newsreader*.
- **Subtle borders & restrained drop shadows** replacing garish neon gradients and blurred glassmorphism.
- **High-resolution photography** and genuine regional context for 25 curated Indian destinations, with support for custom unverified destinations.

---

## 2. Architecture & Strands Decider 2B Integration

```
                                  ┌───────────────────────────────┐
                                  │      React + Vite Frontend    │
                                  │   (Tailwind CSS, Lucide Icons)│
                                  │   • AgentPlannerPanel.jsx     │
                                  └──────────────┬────────────────┘
                                                 │
                                         /api proxy (port 3000)
                                                 │
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │      FastAPI Backend (Py3.12) │
                                  │    (Pydantic, Uvicorn, Pytest)│
                                  └───────┬──────────────┬────────┘
                                          │              │
                       ┌──────────────────┴──┐        ┌──┴──────────────────────────────────────┐
                       ▼                     ▼        ▼                                         ▼
            /api/destinations        /api/trips/plan  /api/agent/plan & /agent/status
         (25 Curated Regions)        & /trips/adapt   ┌─────────────────────────────────────────┐
                                                      │ StrandsAgentService                     │
                                                      │   │                                     │
                                                      │   ▼ (SystemOneRequest: ChoiceQuestion)  │
                                                      │ Strands Decider 2B Inference Endpoint   │
                                                      │ (StrandsAgents/strands-decider-2B)      │
                                                      │   │                                     │
                                                      │   ▼ (Sequential Tool Execution)         │
                                                      │ 5 Strands @tool Registered Tools:       │
                                                      │  • optimize_budget                      │
                                                      │  • adjust_trip_duration                 │
                                                      │  • adjust_travel_style                  │
                                                      │  • select_interest_activities           │
                                                      │  • validate_trip_constraints            │
                                                      └─────────────────────────────────────────┘
```


### Modular Travel Planning Tools (`backend/app/tools/`)

All tools operate as standalone Python functions accepting validated Pydantic models or clean keyword arguments, returning structured Pydantic responses:

1. **Budget Optimizer (`optimize_budget`):**
   - Calculates initial deficit before applying adjustments.
   - Deterministically applies 3 tiers of cost reduction:
     - Tier 1: Economy rates for stay, food, and transit.
     - Tier 2: Downshifts travel style (Comfort → Balanced → Budget).
     - Tier 3: Substitutes premium paid attractions with free cultural, nature, or heritage exploration.
   - Recalculates all daily and trip-wide totals consistently.
   - **Strict Budget Honesty:** If a target budget is below the minimum feasible baseline cost, `fits_budget` is `False`, `final_deficit > 0`, and the limitation is reported truthfully.

2. **Trip Duration Adjuster (`adjust_trip_duration`):**
   - Shortens or extends itineraries within 1–30 days.
   - Preserves high-priority highlights when shortening.
   - Draws from 26 curated thematic day blueprints when extending to guarantee non-duplicated daily schedules.
   - Recalculates all accommodation, food, transit, and daily breakdowns.

3. **Travel-Style Adjuster (`adjust_travel_style`):**
   - Recalibrates accommodation class, dining tier, and transit modes across `Budget`, `Balanced`, and `Comfort`.
   - Preserves destination, duration, and core activities while recalculating daily and total costs.

4. **Interest-Based Activity Selector (`select_interest_activities`):**
   - Prioritizes activities matching user interests (e.g. Heritage, Nature, Food, Adventure, Relaxation).
   - Generates slot-by-slot visit recommendations with specific selection rationales.
   - Explicitly tags whether entries come from curated regional facts or generic fallback templates.

5. **Constraint Validator (`validate_trip_constraints`):**
   - Enforces duration boundaries (1–30 days).
   - Enforces minimum feasible budget (₹5,000 system floor; destination-specific minimum costs).
   - Detects style-to-budget mismatches (e.g., Comfort style with a tight budget).
   - Returns structured issues (error/warning) and suggestions without silent mutations.

6. **Strands SDK Registry (`PLANNING_TOOLS_REGISTRY`):**
   - Maps each tool name to its callable, Pydantic schemas, and tool descriptions for registration with `@tool` or Strands Agents SDK.

---

## 3. Technology Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite 6
- **Language:** JavaScript (ESNext / JSX)
- **Styling:** Tailwind CSS 3 with PostCSS & Autoprefixer
- **Icons:** Lucide React
- **Package Manager:** npm

### Backend
- **Framework:** FastAPI >= 0.115
- **Server:** Uvicorn >= 0.34
- **Data Validation:** Pydantic >= 2.10
- **Testing:** Pytest >= 8.3 with HTTPX / TestClient; Node test runner
- **Runtime:** Python 3.11 or 3.12 (tested on Python 3.12.10)

---

## 4. Directory Structure

```
TripPilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Application package
│   │   ├── main.py               # FastAPI entrypoint, endpoints, and CORS
│   │   ├── models.py             # Pydantic request/response schemas
│   │   ├── data.py               # Curated Indian destinations & sample itineraries
│   │   ├── services/
│   │   │   ├── __init__.py       # Services package
│   │   │   └── trip_planner.py   # Planning engine, budget math, and adaptive actions
│   │   └── tools/                # Phase 3 Modular Planning Tools
│   │       ├── __init__.py       # Package exports & PLANNING_TOOLS_REGISTRY
│   │       ├── schemas.py        # Pydantic schemas for all 5 tools
│   │       ├── budget_optimizer.py
│   │       ├── duration_adjuster.py
│   │       ├── travel_style_adjuster.py
│   │       ├── activity_selector.py
│   │       └── constraint_validator.py
│   ├── tests/
│   │   ├── __init__.py           # Test package
│   │   ├── test_api.py           # API integration test suite (29 tests)
│   │   └── test_tools.py         # Phase 3 tools unit test suite (17 tests)
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend documentation

├── public/
│   └── favicon.svg               # Compass SVG brand mark
├── src/
│   ├── components/
│   │   ├── Header.jsx            # Responsive header, wordmark, navigation tabs
│   │   ├── TripForm.jsx          # Accessible planning inputs, presets, and validation
│   │   ├── DestinationCard.jsx   # Curated destination cards with indicative costs
│   │   ├── ItineraryPanel.jsx    # Day-by-day morning/afternoon/evening schedule
│   │   ├── BudgetPanel.jsx       # Itemized budget breakdown & allocation bar
│   │   └── Footer.jsx            # Editorial brand footer & Phase 2 disclosures
│   ├── data/
│   │   ├── destinations.js       # Curated client-side fallback destination data
│   │   └── sampleItineraries.js  # Curated itineraries & deterministic cost engine
│   ├── services/
│   │   └── api.js                # Centralized FastAPI client & error handling
│   ├── utils/
│   │   └── formatters.js         # Indian Rupee (INR) and pluralization helpers
│   ├── App.jsx                   # Main workspace, state management, & API sync
│   ├── main.jsx                  # Application entry point
│   └── index.css                 # Tailwind directives & focus styling
├── index.html                    # HTML template with typography imports
├── package.json                  # Frontend dependencies & npm scripts
├── postcss.config.js             # PostCSS configuration
├── tailwind.config.js            # Editorial color palette & typography theme
├── vite.config.js                # Vite build configuration with /api proxy
├── README.md                     # Root project documentation
```

---

## 5. Getting Started (Windows PowerShell)

### Step 1: Start the FastAPI Backend

Open a PowerShell terminal:

```powershell
cd "d:\AWS_hackathon - TripPilot\backend"

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. You can inspect interactive documentation at `http://127.0.0.1:8000/docs`.

---

### Step 2: Start the React Frontend

Open a **second** PowerShell terminal:

```powershell
cd "d:\AWS_hackathon - TripPilot"

# Install frontend dependencies (if not already installed)
npm.cmd install

# Start development server
npm.cmd run dev
```

Navigate to `http://localhost:3000` in your web browser.

---

### Step 3: Run Backend Tests

In your backend terminal with the virtual environment activated:

```powershell
cd "d:\AWS_hackathon - TripPilot"
& ".\backend\.venv\Scripts\python.exe" -m pytest backend/tests -v
```

All 54 tests will execute, verifying API endpoints, data validation, budget mathematics, adaptive actions, modular tools, and Strands Decider 2B agent tool selection and provider handling.

---

### Step 4: Run Frontend & Integration Tests

```powershell
cd "d:\AWS_hackathon - TripPilot"
npm.cmd test
```

All 34 integration and frontend tests will execute across adaptation flows, custom durations, detailed itineraries, destination exploration, tool endpoints, and Strands Decider 2B agent endpoints.

---

### Step 5: Run Frontend Production Build

```powershell
cd "d:\AWS_hackathon - TripPilot"
npm.cmd run build
```

---

### Step 6: Launching Strands Decider 2B for Live Inference (Optional)

To enable live autonomous tool selection with the real Strands Decider 2B model:

```powershell
# In a dedicated GPU or high-memory terminal with the virtual environment activated:
& ".\backend\.venv\Scripts\python.exe" -m strands_decider serve StrandsAgents/strands-decider-2B --port 8001
```

Once running, configure `STRANDS_DECIDER_ENDPOINT=http://127.0.0.1:8001/v1/systemone` in your `.env` file. The frontend agent panel will immediately reflect "Live Server Connected" and execute real System 1 decision calls.

---

## 6. Current Limitations & Verification Status (Phase 4)

1. **Deterministic Benchmark Data:** The backend computes schedules and costs from regional baseline benchmarks and curated templates without fabricating real-time flight/hotel prices.
2. **25 Curated Indian Destinations:** Comprehensive regional coverage across India, plus transparent support for unverified custom destinations.
3. **Verified Strands Decider 2B Integration:**
   - Both `strands-agents` (v1.61.1) and `strands-decider` (v0.1.0) are installed and verified.
   - All 5 planning tools are registered using Strands SDK's official `@tool` decorator with full OpenAPI parameter schemas.
   - Decider client implements `SystemOneRequest` and `SystemOneResponse` with typed `ChoiceQuestion` criteria.
   - Fully automated mock and integration tests verify single-tool, multi-tool sequential workflows, and provider failure handling.
   - **Live Model Execution Notice**: A local GPU server running `strands-decider serve StrandsAgents/strands-decider-2B` on port 8001 was not running during automated testing; the agent proved transparent provider reporting (`provider_unavailable`) and executed fully in mock verification without fake AI claims.

---

## 7. Planned Future Phases

- **Phase 5 — Amazon Bedrock Multi-Agent Generative Synthesis:**
  - Multi-agent itinerary synthesis combining Strands Decider 2B (System 1 fast classification) with Amazon Bedrock Claude (System 2 rich generative narrative).
  - Serverless AWS backend deployment (AWS Lambda, Amazon API Gateway, Amazon DynamoDB).
- **Phase 6 — Live Supplier APIs & Booking:**
  - Live flight, train, and hotel pricing integrations.
  - Interactive map routing with real-time transit schedules.
- **Phase 7 — Collaboration & Offline Export:**
  - Multi-user trip sharing and downloadable PDF itineraries.


