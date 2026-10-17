import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import TripForm from './components/TripForm';
import DestinationCard from './components/DestinationCard';
import ItineraryPanel from './components/ItineraryPanel';
import BudgetPanel from './components/BudgetPanel';
import AgentPlannerPanel from './components/AgentPlannerPanel';
import Footer from './components/Footer';


import { destinations as staticDestinations, exploreCategories, filterDestinations } from './data/destinations';
import { sampleItineraries, calculateBudgetBreakdown } from './data/sampleItineraries';
import { checkHealth, fetchDestinations, planTrip, adaptTrip, enrichTrip } from './services/api';
import { formatINR } from './utils/formatters';
import { 
  Sparkles, 
  MapPin, 
  Calendar, 
  IndianRupee, 
  Check, 
  ArrowRight, 
  Bookmark, 
  Trash2, 
  Info,
  Compass,
  AlertTriangle,
  RefreshCw,
  Terminal,
  Server,
  Search,
  SlidersHorizontal,
  X
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('plan');

  // Search and Category Filter State for Explore Section
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [visibleCount, setVisibleCount] = useState(8);

  // Planning Form State with sensible defaults
  const [formData, setFormData] = useState({
    startingCity: 'Bengaluru',
    destinationId: 'hyderabad',
    days: 3,
    budget: '25000',
    interests: ['culture', 'food', 'nature'],
    travelStyle: 'balanced',
  });

  // Dynamic destinations loaded from backend (with static fallback)
  const [destinationsList, setDestinationsList] = useState(staticDestinations);

  // Active Plan & Calculation state returned by the backend
  const [currentPlan, setCurrentPlan] = useState(null);

  // UI & Loading States
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [isAdapting, setIsAdapting] = useState(false);
  const [hasBuiltItinerary, setHasBuiltItinerary] = useState(true);
  const [budgetOptimized, setBudgetOptimized] = useState(false);

  // Backend Connectivity & Error States
  const [backendStatus, setBackendStatus] = useState('checking'); // 'connected' | 'offline' | 'checking'
  const [apiError, setApiError] = useState(null);

  // Saved Itineraries (Local Storage backed)
  const [savedTrips, setSavedTrips] = useState(() => {
    try {
      const stored = localStorage.getItem('trippilot_saved_trips');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Reference for scrolling to itinerary
  const itineraryRef = useRef(null);

  // Save to localStorage whenever savedTrips updates
  useEffect(() => {
    try {
      localStorage.setItem('trippilot_saved_trips', JSON.stringify(savedTrips));
    } catch (e) {
      console.warn('Unable to persist to localStorage', e);
    }
  }, [savedTrips]);

  // Initial connection check & load data on mount
  useEffect(() => {
    let isMounted = true;

    async function initializeBackend() {
      setBackendStatus('checking');
      setApiError(null);
      try {
        // 1. Health check
        await checkHealth();
        
        // 2. Load destinations from backend
        const dests = await fetchDestinations();
        if (isMounted && Array.isArray(dests) && dests.length > 0) {
          setDestinationsList(dests);
        }

        // 3. Request initial plan from FastAPI backend
        const initialPlan = await planTrip({
          ...formData,
          budgetOptimized: false
        });

        if (isMounted) {
          setCurrentPlan(initialPlan);
          setBackendStatus('connected');
        }
      } catch (err) {
        if (isMounted) {
          console.warn('Backend initialization notice:', err.message);
          setBackendStatus('offline');
          setApiError(
            'FastAPI backend is offline. Start the backend by running: "python -m uvicorn app.main:app --reload" inside the backend folder.'
          );
          // Fall back to local calculation if backend is not yet started
          const fallbackCalc = calculateBudgetBreakdown({
            destinationId: formData.destinationId,
            days: Number(formData.days) || 3,
            travelStyle: formData.travelStyle,
            budgetOptimized: false,
            userBudget: Number(formData.budget) || 25000
          });
          const staticItin = sampleItineraries[formData.destinationId] || sampleItineraries.hyderabad;
          setCurrentPlan({
            destination: staticDestinations.find(d => d.id === formData.destinationId) || staticDestinations[0],
            itineraryTitle: staticItin.title,
            itinerarySummary: staticItin.summary,
            ...fallbackCalc
          });
        }
      }
    }

    initializeBackend();

    return () => {
      isMounted = false;
    };
  }, []);

  // Current active destination
  const currentDestination = destinationsList.find(d => d.id === formData.destinationId) || destinationsList[0];

  // Fallback calculation object if plan not yet loaded
  const displayCalculation = currentPlan || calculateBudgetBreakdown({
    destinationId: formData.destinationId,
    days: Number(formData.days) || 3,
    travelStyle: formData.travelStyle,
    budgetOptimized,
    userBudget: Number(formData.budget) || 25000
  });

  const displayItinerary = {
    title: currentPlan?.itineraryTitle || (sampleItineraries[formData.destinationId] || sampleItineraries.hyderabad).title,
    summary: currentPlan?.itinerarySummary || (sampleItineraries[formData.destinationId] || sampleItineraries.hyderabad).summary
  };

  const displayActiveDays = currentPlan?.activeDays || displayCalculation.activeDays || [];

  // Handler: Build Itinerary via POST /api/trips/plan
  const handleBuildItinerary = async () => {
    setIsLoadingPlan(true);
    setApiError(null);

    try {
      const planResponse = await planTrip({
        ...formData,
        budgetOptimized
      });
      setCurrentPlan(planResponse);
      setBackendStatus('connected');
      setHasBuiltItinerary(true);

      if (itineraryRef.current) {
        itineraryRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (err) {
      setApiError(err.message || 'Failed to build itinerary from backend.');
      setBackendStatus('offline');
    } finally {
      setIsLoadingPlan(false);
    }
  };

  // Handler: Select destination from discovery cards or directory ("Plan this trip")
  const handleSelectDestination = async (destId) => {
    const updatedForm = {
      ...formData,
      destinationId: destId,
      isCustomDestination: false,
      customDestinationName: ''
    };
    setFormData(updatedForm);
    if (activeTab !== 'plan') {
      setActiveTab('plan');
    }

    setIsLoadingPlan(true);
    setApiError(null);
    try {
      const planResponse = await planTrip({
        ...updatedForm,
        budgetOptimized
      });
      setCurrentPlan(planResponse);
      setBackendStatus('connected');
      setHasBuiltItinerary(true);
    } catch (err) {
      console.warn('Backend plan error when selecting destination:', err.message);
      const destObj = destinationsList.find(d => d.id === destId);
      if (destObj) {
        const fallbackCalc = calculateBudgetBreakdown({
          destinationId: destId,
          days: Number(updatedForm.days) || 3,
          travelStyle: updatedForm.travelStyle,
          budgetOptimized,
          userBudget: Number(updatedForm.budget) || 25000
        });
        const staticItin = sampleItineraries[destId] || {
          title: `${destObj.name} Explorer`,
          summary: `Curated itinerary for ${destObj.name}, ${destObj.state}.`
        };
        setCurrentPlan({
          destination: destObj,
          itineraryTitle: staticItin.title,
          itinerarySummary: staticItin.summary,
          ...fallbackCalc
        });
      }
    } finally {
      setIsLoadingPlan(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Handler: Adaptive Control - Reduce Budget via POST /api/trips/adapt
  const handleToggleBudgetOptimization = async () => {
    setIsAdapting(true);
    setApiError(null);

    const activeBudgetOpt = currentPlan ? currentPlan.budgetOptimized : budgetOptimized;

    try {
      const adapted = await adaptTrip({
        action: 'reduce_budget',
        planRequest: {
          startingCity: formData.startingCity,
          destinationId: currentPlan?.destination?.id || formData.destinationId,
          days: currentPlan?.numDays || Number(formData.days),
          budget: currentPlan?.userBudget || Number(formData.budget),
          interests: formData.interests,
          travelStyle: currentPlan?.travelStyle || formData.travelStyle,
          budgetOptimized: activeBudgetOpt,
        }
      });
      setCurrentPlan(adapted);
      setBudgetOptimized(adapted.budgetOptimized);
      setFormData(prev => ({
        ...prev,
        days: adapted.numDays,
        travelStyle: adapted.travelStyle,
        destinationId: adapted.destination.id,
      }));
      setBackendStatus('connected');
    } catch (err) {
      console.warn('Backend adapt error, falling back to local calculation:', err.message);
      const nextBudgetOpt = !activeBudgetOpt;
      const targetDest = currentPlan?.destination?.id || formData.destinationId;
      const targetDays = currentPlan?.numDays || Number(formData.days);
      const targetStyle = currentPlan?.travelStyle || formData.travelStyle;
      const targetBudget = currentPlan?.userBudget || Number(formData.budget);

      const fallbackCalc = calculateBudgetBreakdown({
        destinationId: targetDest,
        days: targetDays,
        travelStyle: targetStyle,
        budgetOptimized: nextBudgetOpt,
        userBudget: targetBudget
      });
      const staticItin = sampleItineraries[targetDest] || sampleItineraries.hyderabad;
      const fallbackDest = destinationsList.find(d => d.id === targetDest) || destinationsList[0];

      setCurrentPlan({
        destination: fallbackDest,
        itineraryTitle: staticItin.title,
        itinerarySummary: staticItin.summary,
        ...fallbackCalc
      });
      setBudgetOptimized(nextBudgetOpt);
      setFormData(prev => ({
        ...prev,
        days: targetDays,
        travelStyle: targetStyle,
        destinationId: targetDest,
      }));
    } finally {
      setIsAdapting(false);
    }
  };

  // Handler: Adaptive Control - Shorten Trip via POST /api/trips/adapt
  const handleShortenTrip = async () => {
    const currentDays = currentPlan?.numDays || Number(formData.days);
    if (currentDays <= 1) return;

    setIsAdapting(true);
    setApiError(null);

    const activeBudgetOpt = currentPlan ? currentPlan.budgetOptimized : budgetOptimized;

    try {
      const adapted = await adaptTrip({
        action: 'shorten_trip',
        planRequest: {
          startingCity: formData.startingCity,
          destinationId: currentPlan?.destination?.id || formData.destinationId,
          days: currentDays,
          budget: currentPlan?.userBudget || Number(formData.budget),
          interests: formData.interests,
          travelStyle: currentPlan?.travelStyle || formData.travelStyle,
          budgetOptimized: activeBudgetOpt,
        }
      });
      setCurrentPlan(adapted);
      setBudgetOptimized(adapted.budgetOptimized);
      setFormData(prev => ({
        ...prev,
        days: adapted.numDays,
        travelStyle: adapted.travelStyle,
        destinationId: adapted.destination.id,
      }));
      setBackendStatus('connected');
    } catch (err) {
      console.warn('Backend shorten trip error, falling back to local calculation:', err.message);
      const nextDays = Math.max(1, currentDays - 1);
      const targetDest = currentPlan?.destination?.id || formData.destinationId;
      const targetStyle = currentPlan?.travelStyle || formData.travelStyle;
      const targetBudget = currentPlan?.userBudget || Number(formData.budget);

      const fallbackCalc = calculateBudgetBreakdown({
        destinationId: targetDest,
        days: nextDays,
        travelStyle: targetStyle,
        budgetOptimized: activeBudgetOpt,
        userBudget: targetBudget
      });
      const staticItin = sampleItineraries[targetDest] || sampleItineraries.hyderabad;
      const fallbackDest = destinationsList.find(d => d.id === targetDest) || destinationsList[0];

      setCurrentPlan({
        destination: fallbackDest,
        itineraryTitle: staticItin.title,
        itinerarySummary: staticItin.summary,
        ...fallbackCalc
      });
      setFormData(prev => ({
        ...prev,
        days: nextDays,
        travelStyle: targetStyle,
        destinationId: targetDest,
      }));
    } finally {
      setIsAdapting(false);
    }
  };

  // Handler: Adaptive Control - Change Travel Style via POST /api/trips/adapt
  const handleTravelStyleChange = async (styleKey) => {
    setIsAdapting(true);
    setApiError(null);

    const activeBudgetOpt = currentPlan ? currentPlan.budgetOptimized : budgetOptimized;

    try {
      const adapted = await adaptTrip({
        action: 'change_travel_style',
        planRequest: {
          startingCity: formData.startingCity,
          destinationId: currentPlan?.destination?.id || formData.destinationId,
          days: currentPlan?.numDays || Number(formData.days),
          budget: currentPlan?.userBudget || Number(formData.budget),
          interests: formData.interests,
          travelStyle: currentPlan?.travelStyle || formData.travelStyle,
          budgetOptimized: activeBudgetOpt,
        },
        newTravelStyle: styleKey
      });
      setCurrentPlan(adapted);
      setBudgetOptimized(adapted.budgetOptimized);
      setFormData(prev => ({
        ...prev,
        days: adapted.numDays,
        travelStyle: adapted.travelStyle,
        destinationId: adapted.destination.id,
      }));
      setBackendStatus('connected');
    } catch (err) {
      console.warn('Backend style change error, falling back to local calculation:', err.message);
      const targetDest = currentPlan?.destination?.id || formData.destinationId;
      const targetDays = currentPlan?.numDays || Number(formData.days);
      const targetBudget = currentPlan?.userBudget || Number(formData.budget);

      const fallbackCalc = calculateBudgetBreakdown({
        destinationId: targetDest,
        days: targetDays,
        travelStyle: styleKey,
        budgetOptimized: activeBudgetOpt,
        userBudget: targetBudget
      });
      const staticItin = sampleItineraries[targetDest] || sampleItineraries.hyderabad;
      const fallbackDest = destinationsList.find(d => d.id === targetDest) || destinationsList[0];

      setCurrentPlan({
        destination: fallbackDest,
        itineraryTitle: staticItin.title,
        itinerarySummary: staticItin.summary,
        ...fallbackCalc
      });
      setFormData(prev => ({
        ...prev,
        days: targetDays,
        travelStyle: styleKey,
        destinationId: targetDest,
      }));
    } finally {
      setIsAdapting(false);
    }
  };

  // Retry backend connection
  const handleRetryConnection = async () => {
    setBackendStatus('checking');
    setApiError(null);
    try {
      await checkHealth();
      const dests = await fetchDestinations();
      if (Array.isArray(dests) && dests.length > 0) {
        setDestinationsList(dests);
      }
      const plan = await planTrip({ ...formData, budgetOptimized });
      setCurrentPlan(plan);
      setBackendStatus('connected');
    } catch (err) {
      setBackendStatus('offline');
      setApiError(err.message);
    }
  };

  // Handler: Amazon Bedrock AI Enrichment via POST /api/trips/enrich
  const [isEnriching, setIsEnriching] = useState(false);

  const handleEnrichItinerary = async () => {
    if (!currentPlan) return;
    setIsEnriching(true);
    setApiError(null);
    try {
      const enriched = await enrichTrip(currentPlan);
      setCurrentPlan(enriched);
      setBackendStatus('connected');
    } catch (err) {
      console.warn('Bedrock enrichment notice:', err.message);
      setCurrentPlan(prev => ({
        ...prev,
        aiEnrichment: {
          status: 'provider_unavailable',
          modelId: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
          error: err.message
        }
      }));
    } finally {
      setIsEnriching(false);
    }
  };

  // Check if current configuration is saved
  const tripKey = `${formData.startingCity}-${formData.destinationId}-${formData.days}-${formData.travelStyle}`;
  const isCurrentTripSaved = savedTrips.some(t => t.id === tripKey);

  const handleToggleSaveTrip = () => {
    if (isCurrentTripSaved) {
      setSavedTrips(prev => prev.filter(t => t.id !== tripKey));
    } else {
      const newSaved = {
        id: tripKey,
        savedAt: new Date().toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }),
        destination: currentDestination,
        days: displayCalculation.numDays,
        travelStyle: formData.travelStyle,
        budgetOptimized,
        totalEstimatedCost: displayCalculation.totalEstimatedCost,
        userBudget: displayCalculation.userBudget,
        startingCity: formData.startingCity,
        interests: [...formData.interests],
        itineraryTitle: displayItinerary.title
      };
      setSavedTrips(prev => [newSaved, ...prev]);
    }
  };

  const handleLoadSavedTrip = async (saved) => {
    const updatedForm = {
      startingCity: saved.startingCity,
      destinationId: saved.destination.id,
      days: saved.days,
      budget: saved.userBudget.toString(),
      interests: saved.interests,
      travelStyle: saved.travelStyle,
    };
    setFormData(updatedForm);
    setBudgetOptimized(saved.budgetOptimized || false);
    setHasBuiltItinerary(true);
    setActiveTab('plan');

    // Trigger backend plan update
    setIsLoadingPlan(true);
    setApiError(null);
    try {
      const plan = await planTrip({
        ...updatedForm,
        budgetOptimized: saved.budgetOptimized || false
      });
      setCurrentPlan(plan);
      setBackendStatus('connected');
    } catch (err) {
      setApiError(err.message);
    } finally {
      setIsLoadingPlan(false);
    }
  };

  const handleDeleteSavedTrip = (id) => {
    setSavedTrips(prev => prev.filter(t => t.id !== id));
  };

  const handleAgentPlanUpdated = (newPlan) => {
    if (!newPlan) return;
    setCurrentPlan(newPlan);
    setFormData(prev => ({
      ...prev,
      destinationId: newPlan.destination?.id || prev.destinationId,
      days: newPlan.numDays || prev.days,
      budget: String(newPlan.userBudget || prev.budget),
      travelStyle: newPlan.travelStyle || prev.travelStyle,
    }));
    setBudgetOptimized(newPlan.budgetOptimized || false);
    setHasBuiltItinerary(true);
  };


  return (
    <div className="min-h-screen flex flex-col bg-canvas text-charcoal-900 font-sans selection:bg-forest-100 selection:text-forest-900">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        savedCount={savedTrips.length}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        
        {/* Backend Offline Banner Notice */}
        {backendStatus === 'offline' && (
          <div className="mb-8 rounded-xl border border-amber-300 bg-amber-50/80 p-4 sm:p-5 shadow-subtle">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs sm:text-sm font-bold text-amber-900">
                    FastAPI Backend Offline
                  </h4>
                  <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">
                    To enable live API planning and adaptations, start the Python server in Windows PowerShell:
                  </p>
                  <div className="mt-2 inline-flex items-center gap-2 bg-amber-100/90 border border-amber-300/80 px-2.5 py-1 rounded-md text-[11px] font-mono text-amber-950">
                    <Terminal className="w-3.5 h-3.5 text-amber-800" />
                    <span>cd backend; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload</span>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={handleRetryConnection}
                className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-800 text-white hover:bg-amber-900 transition-colors flex items-center gap-1.5 shrink-0 self-start sm:self-center shadow-subtle"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry Connection</span>
              </button>
            </div>
          </div>
        )}

        {/* API Error Notification */}
        {apiError && backendStatus !== 'offline' && (
          <div className="mb-8 rounded-xl border border-terracotta-200 bg-red-50/70 p-4 flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-terracotta-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="text-xs font-bold text-terracotta-700">API Error</div>
              <p className="text-xs text-terracotta-600 mt-0.5">{apiError}</p>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW 1: PLAN A TRIP (Primary Workspace)                  */}
        {/* ========================================================= */}
        {activeTab === 'plan' && (
          <div className="space-y-12">
            
            {/* Context Breadcrumb / Hero Tagline */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-sand-200/80 pb-4">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-500">
                  Curated Indian Journeys
                </span>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-forest-950 tracking-tight mt-0.5">
                  Plan Your Next Adventure
                </h1>
                <p className="text-xs sm:text-sm text-charcoal-500 mt-1 max-w-xl">
                  Explore destinations, customize your itinerary and plan your journey within your budget.
                </p>
              </div>

              {/* Status summary pill */}
              <div className="flex items-center gap-2.5 self-start sm:self-auto bg-sand-100/90 border border-sand-200 px-3.5 py-1.5 rounded-xl text-xs shadow-subtle">
                <span className="font-bold text-forest-900">{currentPlan?.destination?.name || currentDestination.name}</span>
                <span className="text-sand-300">•</span>
                <span className="font-medium text-charcoal-700">{currentPlan?.numDays || formData.days} Days</span>
              </div>
            </div>

            {/* Two-Column Layout: Form (7 cols) + Budget Breakdown (5 cols) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Left Column: Interactive Trip Form */}
              <div className="lg:col-span-7">
                <TripForm
                  formData={formData}
                  onChange={setFormData}
                  onSubmit={handleBuildItinerary}
                  hasBuiltItinerary={hasBuiltItinerary}
                  isLoading={isLoadingPlan}
                  destinationsList={destinationsList}
                />
              </div>

              {/* Right Column: Secondary Summary Panel (Budget Panel) */}
              <div className="lg:col-span-5 lg:sticky lg:top-24">
                <BudgetPanel calculation={displayCalculation} />
              </div>
            </div>

            {/* Strands Decider 2B Autonomous Agent Assistant */}
            <AgentPlannerPanel
              currentPlan={currentPlan}
              formData={formData}
              onPlanUpdated={handleAgentPlanUpdated}
              isAdapting={isAdapting}
              setIsAdapting={setIsAdapting}
            />

            {/* Itinerary Workspace (Day-by-Day + Adaptive Controls) */}
            <div ref={itineraryRef} className="pt-4 border-t border-sand-200">
              <ItineraryPanel
                itinerary={displayItinerary}
                activeDays={displayActiveDays}
                travelStyle={currentPlan?.travelStyle || formData.travelStyle}
                onTravelStyleChange={handleTravelStyleChange}
                budgetOptimized={currentPlan?.budgetOptimized ?? budgetOptimized}
                onToggleBudgetOptimization={handleToggleBudgetOptimization}
                onShortenTrip={handleShortenTrip}
                canShortenTrip={(currentPlan?.numDays || displayCalculation.numDays) > 1}
                isSaved={isCurrentTripSaved}
                onToggleSave={handleToggleSaveTrip}
                isAdapting={isAdapting}
                isVerified={currentPlan?.isVerified ?? !formData.isCustomDestination}
                aiEnrichment={currentPlan?.aiEnrichment}
                onEnrichItinerary={handleEnrichItinerary}
                isEnriching={isEnriching}
              />
            </div>

            {/* Destination Discovery Section (Top Featured) */}
            <div className="pt-8 border-t border-sand-200">
              <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-6">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-forest-700">
                    Handcrafted Indian Regions
                  </span>
                  <h3 className="font-serif text-2xl font-bold text-charcoal-900 mt-1">
                    Select a Featured Destination
                  </h3>
                  <p className="text-xs sm:text-sm text-charcoal-600 mt-0.5">
                    Click "Plan this trip" to instantly load verified benchmarks into your planning session.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab('explore')}
                  className="text-xs font-semibold text-forest-800 hover:text-forest-950 flex items-center gap-1 group self-start sm:self-auto bg-sand-100 hover:bg-sand-200/80 px-3 py-1.5 rounded-lg border border-sand-200/70 transition-colors"
                >
                  <span>Explore all {destinationsList.length} destinations</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {destinationsList.slice(0, 4).map((dest) => (
                  <DestinationCard
                    key={dest.id}
                    destination={dest}
                    isSelected={formData.destinationId === dest.id && !formData.isCustomDestination}
                    onSelect={handleSelectDestination}
                  />
                ))}
              </div>
            </div>

          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW 2: EXPLORE (Destination Directory)                   */}
        {/* ========================================================= */}
        {activeTab === 'explore' && (
          <div className="space-y-8">
            {/* Explore Hero Banner */}
            <div className="border-b border-sand-200/80 pb-6">
              <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-forest-700 bg-forest-50 px-2.5 py-1 rounded-md mb-2">
                <Compass className="w-3.5 h-3.5" />
                <span>Pan-India Travel Directory • {destinationsList.length} Curated Regions</span>
              </div>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-charcoal-900 mt-1">
                Explore Destinations in India
              </h1>
              <p className="text-sm text-charcoal-600 mt-1 max-w-2xl leading-relaxed">
                Discover verified regional benchmark costs, seasonal weather windows, and curated activity routes. Filter by vibe or search by state to find your next journey.
              </p>
            </div>

            {/* Search and Category Filter Bar */}
            <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-5 shadow-card space-y-4">
              {/* Row 1: Search Input */}
              <div className="relative">
                <Search className="pointer-events-none absolute left-3.5 top-3 w-4 h-4 text-charcoal-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setVisibleCount(8);
                  }}
                  placeholder="Search destinations by name, state (e.g. Kerala, Goa, Rajasthan, Himachal, Munnar)..."
                  className="w-full rounded-xl border border-sand-300 bg-canvas px-4 py-2.5 pl-10 pr-10 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery('');
                      setVisibleCount(8);
                    }}
                    className="absolute right-3 top-2.5 p-1 rounded-full text-charcoal-400 hover:text-charcoal-700 hover:bg-sand-100"
                    aria-label="Clear search"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Row 2: Category Filter Pills */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-500 flex items-center gap-1.5">
                    <SlidersHorizontal className="w-3 h-3" />
                    <span>Filter by Experience</span>
                  </span>
                  {(searchQuery || selectedCategory !== 'all') && (
                    <button
                      type="button"
                      onClick={() => {
                        setSearchQuery('');
                        setSelectedCategory('all');
                        setVisibleCount(8);
                      }}
                      className="text-xs font-semibold text-terracotta-600 hover:text-terracotta-800 transition-colors"
                    >
                      Reset filters
                    </button>
                  )}
                </div>

                <div className="flex flex-wrap gap-2">
                  {exploreCategories.map((cat) => {
                    const count = filterDestinations(destinationsList, {
                      search: searchQuery,
                      category: cat.id
                    }).length;
                    const isSelected = selectedCategory === cat.id;

                    return (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => {
                          setSelectedCategory(cat.id);
                          setVisibleCount(8);
                        }}
                        className={`text-xs px-3 py-1.5 rounded-lg border font-medium flex items-center gap-1.5 transition-all ${
                          isSelected
                            ? 'bg-forest-900 text-canvas border-forest-900 shadow-subtle'
                            : 'bg-sand-100/70 text-charcoal-700 border-sand-200/80 hover:bg-sand-200/70'
                        }`}
                      >
                        <span>{cat.label}</span>
                        <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                          isSelected ? 'bg-forest-800 text-forest-100' : 'bg-sand-200 text-charcoal-600'
                        }`}>
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Results Count & Status Bar */}
            <div className="flex items-center justify-between text-xs text-charcoal-600 px-1">
              <div>
                Showing <strong className="text-charcoal-900">{Math.min(visibleCount, filterDestinations(destinationsList, { search: searchQuery, category: selectedCategory }).length)}</strong> of <strong className="text-charcoal-900">{filterDestinations(destinationsList, { search: searchQuery, category: selectedCategory }).length}</strong> destinations
                {selectedCategory !== 'all' && (
                  <span className="ml-1.5 text-forest-800 font-medium">
                    in {exploreCategories.find(c => c.id === selectedCategory)?.label || selectedCategory}
                  </span>
                )}
                {searchQuery && (
                  <span className="ml-1.5 text-charcoal-500">
                    matching "{searchQuery}"
                  </span>
                )}
              </div>
            </div>

            {/* Destination Grid */}
            {filterDestinations(destinationsList, { search: searchQuery, category: selectedCategory }).length === 0 ? (
              <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-12 text-center shadow-card">
                <Compass className="w-10 h-10 text-charcoal-300 mx-auto mb-3" />
                <h3 className="font-serif text-xl font-bold text-charcoal-800">No destinations found</h3>
                <p className="text-sm text-charcoal-600 mt-1 max-w-md mx-auto">
                  We couldn't find any curated destinations matching your search. Try adjusting keywords or explore another category.
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('all');
                    setVisibleCount(8);
                  }}
                  className="mt-4 px-4 py-2 rounded-xl text-xs font-semibold bg-forest-900 text-canvas hover:bg-forest-800 transition-colors shadow-subtle"
                >
                  Show all {destinationsList.length} destinations
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {filterDestinations(destinationsList, { search: searchQuery, category: selectedCategory })
                  .slice(0, visibleCount)
                  .map((dest) => {
                    const isSelected = formData.destinationId === dest.id && !formData.isCustomDestination;
                    const dailyCosts = dest.indicativeDailyCost || { budget: 2200, balanced: 4500, comfort: 8500 };

                    return (
                      <div 
                        key={dest.id} 
                        className={`flex flex-col rounded-2xl border bg-canvas-card overflow-hidden shadow-card transition-all ${
                          isSelected ? 'border-forest-700 ring-2 ring-forest-700/20' : 'border-sand-200/90 hover:border-sand-300'
                        }`}
                      >
                        {/* Image Banner */}
                        <div className="relative aspect-[16/9] overflow-hidden bg-sand-200">
                          <img
                            src={dest.image}
                            alt={`${dest.name}, ${dest.state}`}
                            loading="lazy"
                            onError={(e) => {
                              if (dest.fallbackImage && e.target.src !== dest.fallbackImage) {
                                e.target.src = dest.fallbackImage;
                              }
                            }}
                            className="w-full h-full object-cover transition-transform duration-500 ease-out hover:scale-[1.02]"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900/80 via-charcoal-900/20 to-transparent" />
                          <div className="absolute top-4 left-4 flex items-center gap-1.5">
                            <span className="text-xs font-medium bg-charcoal-900/70 backdrop-blur-sm text-white px-2.5 py-1 rounded-md flex items-center gap-1">
                              <MapPin className="w-3 h-3 text-sand-300" />
                              <span>{dest.state}</span>
                            </span>
                          </div>
                          {isSelected && (
                            <div className="absolute top-4 right-4 bg-forest-900 text-canvas text-xs font-semibold px-2.5 py-1 rounded-md flex items-center gap-1.5 shadow-subtle border border-forest-600/30">
                              <Check className="w-3.5 h-3.5 text-forest-300" strokeWidth={2.5} />
                              <span>Current Plan</span>
                            </div>
                          )}
                          <div className="absolute bottom-4 left-4 right-4 text-white">
                            <h2 className="font-serif text-2xl sm:text-3xl font-bold">{dest.name}</h2>
                          </div>
                        </div>

                        {/* Content Area */}
                        <div className="p-6 flex-1 flex flex-col justify-between space-y-5">
                          <div>
                            <p className="text-xs italic text-forest-800 font-medium mb-2.5">
                              "{dest.tagline}"
                            </p>
                            <p className="text-xs text-charcoal-600 leading-relaxed mb-4">
                              {dest.description}
                            </p>

                            {/* Weather Season & Range */}
                            <div className="grid grid-cols-2 gap-3 p-3 bg-sand-50 rounded-xl border border-sand-200/70 mb-4 text-xs">
                              <div>
                                <span className="text-[10px] uppercase font-bold text-charcoal-400 block mb-0.5">
                                  Best Season
                                </span>
                                <span className="font-semibold text-charcoal-800">
                                  {dest.bestTimeToVisit}
                                </span>
                              </div>
                              <div>
                                <span className="text-[10px] uppercase font-bold text-charcoal-400 block mb-0.5">
                                  Indicative Range
                                </span>
                                <span className="font-semibold text-charcoal-800">
                                  {dest.indicativeRange}
                                </span>
                              </div>
                            </div>

                            {/* Daily Travel Style Benchmarks */}
                            <div className="mb-4">
                              <div className="text-[10px] font-bold uppercase tracking-wider text-charcoal-500 mb-1.5">
                                Indicative Daily Cost by Travel Style
                              </div>
                              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                                <div className="bg-sand-100/60 rounded-lg p-2 border border-sand-200/50">
                                  <div className="text-[10px] text-charcoal-500 font-medium">Budget</div>
                                  <div className="font-bold text-charcoal-800">{formatINR(dailyCosts.budget)}/d</div>
                                </div>
                                <div className="bg-forest-50/60 rounded-lg p-2 border border-forest-100">
                                  <div className="text-[10px] text-forest-800 font-medium">Balanced</div>
                                  <div className="font-bold text-forest-900">{formatINR(dailyCosts.balanced)}/d</div>
                                </div>
                                <div className="bg-sand-100/60 rounded-lg p-2 border border-sand-200/50">
                                  <div className="text-[10px] text-charcoal-500 font-medium">Comfort</div>
                                  <div className="font-bold text-charcoal-800">{formatINR(dailyCosts.comfort)}/d</div>
                                </div>
                              </div>
                            </div>

                            {/* Highlights */}
                            <div>
                              <div className="text-[10px] font-bold uppercase tracking-wider text-charcoal-500 mb-1.5">
                                Verified Highlights
                              </div>
                              <div className="flex flex-wrap gap-1.5">
                                {dest.highlights.map((h, i) => (
                                  <span key={i} className="text-[11px] bg-sand-100 text-charcoal-700 px-2.5 py-0.5 rounded-md border border-sand-200/70">
                                    {h}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>

                          {/* Footer Action */}
                          <div className="pt-4 border-t border-sand-100 flex items-center justify-between">
                            <span className="text-xs text-charcoal-500">
                              {isSelected ? 'Loaded in workspace' : 'Verified regional benchmark'}
                            </span>
                            <button
                              type="button"
                              onClick={() => handleSelectDestination(dest.id)}
                              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                                isSelected
                                  ? 'bg-forest-100 text-forest-900 border border-forest-300'
                                  : 'bg-forest-900 text-canvas hover:bg-forest-800 shadow-subtle'
                              }`}
                            >
                              {isSelected ? (
                                <>
                                  <Check className="w-3.5 h-3.5" />
                                  <span>Current Plan</span>
                                </>
                              ) : (
                                <>
                                  <span>Plan this trip</span>
                                  <ArrowRight className="w-3.5 h-3.5" />
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}

            {/* Pagination Controls to Browse Without Overcrowding */}
            {(() => {
              const totalMatches = filterDestinations(destinationsList, { search: searchQuery, category: selectedCategory }).length;
              if (totalMatches <= 8) return null;

              return (
                <div className="pt-4 border-t border-sand-200/80 flex flex-col sm:flex-row items-center justify-center gap-3">
                  {visibleCount < totalMatches && (
                    <button
                      type="button"
                      onClick={() => setVisibleCount(prev => Math.min(totalMatches, prev + 8))}
                      className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-forest-900 text-canvas hover:bg-forest-800 transition-colors shadow-subtle flex items-center gap-2"
                    >
                      <span>Load More Destinations (+{Math.min(8, totalMatches - visibleCount)} remaining)</span>
                    </button>
                  )}
                  {visibleCount < totalMatches && (
                    <button
                      type="button"
                      onClick={() => setVisibleCount(totalMatches)}
                      className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-sand-100 text-charcoal-800 hover:bg-sand-200 border border-sand-300 transition-colors"
                    >
                      <span>Show All ({totalMatches})</span>
                    </button>
                  )}
                  {visibleCount > 8 && (
                    <button
                      type="button"
                      onClick={() => {
                        setVisibleCount(8);
                        window.scrollTo({ top: 300, behavior: 'smooth' });
                      }}
                      className="px-4 py-2.5 rounded-xl text-xs font-semibold text-charcoal-600 hover:text-charcoal-900 underline transition-colors"
                    >
                      Show less
                    </button>
                  )}
                </div>
              );
            })()}

          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW 3: SAVED TRIPS                                       */}
        {/* ========================================================= */}
        {activeTab === 'saved' && (
          <div className="space-y-8">
            <div className="border-b border-sand-200/80 pb-5">
              <span className="text-xs font-semibold uppercase tracking-wider text-forest-700">
                Personal Library
              </span>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-charcoal-900 mt-1">
                Saved Itineraries
              </h1>
              <p className="text-sm text-charcoal-600 mt-1 leading-relaxed">
                Review your saved planning drafts and load them back into the workspace at any time.
              </p>
            </div>

            {savedTrips.length === 0 ? (
              <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-12 text-center max-w-xl mx-auto shadow-subtle">
                <div className="w-12 h-12 rounded-xl bg-sand-100 text-charcoal-400 flex items-center justify-center mx-auto mb-3">
                  <Bookmark className="w-6 h-6" />
                </div>
                <h3 className="font-serif text-lg font-bold text-charcoal-900 mb-1">
                  No saved itineraries yet
                </h3>
                <p className="text-xs text-charcoal-500 leading-relaxed mb-5">
                  When you configure a trip that matches your criteria in the planner, click "Save Plan" to bookmark it here.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveTab('plan')}
                  className="px-5 py-2.5 rounded-xl bg-forest-900 text-canvas text-xs font-semibold hover:bg-forest-800 transition-colors shadow-subtle"
                >
                  Start Planning
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {savedTrips.map((saved) => (
                  <div
                    key={saved.id}
                    className="border border-sand-200/90 rounded-2xl bg-canvas-card p-5 shadow-card flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3 text-xs text-charcoal-500">
                        <span className="flex items-center gap-1 font-medium">
                          <MapPin className="w-3.5 h-3.5 text-forest-700" />
                          <span>{saved.startingCity} → {saved.destination.name}</span>
                        </span>
                        <span>Saved {saved.savedAt}</span>
                      </div>

                      <h3 className="font-serif text-lg font-bold text-charcoal-900 mb-1">
                        {saved.destination.name} ({saved.days} Days)
                      </h3>
                      <p className="text-xs text-forest-800 font-medium mb-3">
                        {saved.itineraryTitle}
                      </p>

                      <div className="p-3 bg-sand-50 rounded-xl border border-sand-200/70 mb-4 text-xs space-y-1.5">
                        <div className="flex justify-between">
                          <span className="text-charcoal-500">Estimated Cost:</span>
                          <span className="font-bold text-charcoal-900">{formatINR(saved.totalEstimatedCost)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-charcoal-500">Allocated Budget:</span>
                          <span className="font-semibold text-charcoal-700">{formatINR(saved.userBudget)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-charcoal-500">Style:</span>
                          <span className="font-semibold capitalize text-charcoal-800">{saved.travelStyle}</span>
                        </div>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-sand-100 flex items-center justify-between gap-2">
                      <button
                        type="button"
                        onClick={() => handleDeleteSavedTrip(saved.id)}
                        className="p-2 rounded-lg text-charcoal-400 hover:text-terracotta-600 hover:bg-red-50 transition-colors"
                        title="Remove saved itinerary"
                        aria-label="Remove saved itinerary"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>

                      <button
                        type="button"
                        onClick={() => handleLoadSavedTrip(saved)}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-forest-900 text-canvas hover:bg-forest-800 transition-colors flex items-center gap-1.5 shadow-subtle"
                      >
                        <span>Load in Planner</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </main>

      {/* Footer */}
      <Footer onTabChange={setActiveTab} />
    </div>
  );
}
