import React, { useState } from 'react';
import MapPanel from './MapPanel';
import { 
  Sun, 
  CloudSun, 
  Moon, 
  IndianRupee, 
  MapPin, 
  Clock, 
  Sparkles, 
  Sliders, 
  MinusCircle, 
  TrendingDown, 
  ShieldCheck, 
  Info,
  Calendar,
  Share2,
  BookmarkCheck,
  Bookmark,
  Loader2,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Utensils,
  Navigation,
  Eye,
  EyeOff,
  Compass,
  Map as MapIcon,
  Ticket,
  ExternalLink
} from 'lucide-react';
import { formatINR } from '../utils/formatters';

export default function ItineraryPanel({
  itinerary,
  activeDays,
  travelStyle,
  onTravelStyleChange,
  budgetOptimized,
  onToggleBudgetOptimization,
  onShortenTrip,
  canShortenTrip,
  isSaved,
  onToggleSave,
  isAdapting = false,
  isVerified = true,
  aiEnrichment = null,
  onEnrichItinerary = null,
  isEnriching = false
}) {
  const [selectedDayTab, setSelectedDayTab] = useState(1);
  const [viewMode, setViewMode] = useState('schedule'); // 'schedule' | 'map'
  const [expandedTips, setExpandedTips] = useState({});
  const [expandAll, setExpandAll] = useState(false);

  const toggleTip = (slotKey) => {
    const key = `${currentDay?.dayNumber || selectedDayTab}-${slotKey}`;
    setExpandedTips(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const toggleExpandAll = () => {
    const next = !expandAll;
    setExpandAll(next);
    const dayNum = currentDay?.dayNumber || selectedDayTab;
    setExpandedTips(prev => ({
      ...prev,
      [`${dayNum}-morning`]: next,
      [`${dayNum}-afternoon`]: next,
      [`${dayNum}-evening`]: next,
    }));
  };

  if (!itinerary || !activeDays || activeDays.length === 0) {
    return (
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-8 text-center">
        <p className="text-charcoal-600">Select a destination and click "Build my itinerary" to view the schedule.</p>
      </div>
    );
  }

  // Ensure selected tab is within active days
  const currentDayIndex = Math.min(selectedDayTab - 1, activeDays.length - 1);
  const currentDay = activeDays[currentDayIndex] || activeDays[0];

  const timeSlots = [
    { key: 'morning', label: 'Morning', icon: Sun, slotColor: 'text-amber-700 bg-amber-50/60 border-amber-200/50' },
    { key: 'afternoon', label: 'Afternoon', icon: CloudSun, slotColor: 'text-forest-700 bg-forest-50/60 border-forest-200/50' },
    { key: 'evening', label: 'Evening', icon: Moon, slotColor: 'text-indigo-700 bg-indigo-50/60 border-indigo-200/50' },
  ];

  return (
    <div className="space-y-6">
      {/* Itinerary Header & Disclaimer Notice */}
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 sm:p-7 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-sand-100 pb-5 mb-5">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-[10px] font-sans font-semibold uppercase tracking-wider bg-sand-100 text-charcoal-700 px-2 py-0.5 rounded border border-sand-200/60">
                {activeDays.length}-Day {isVerified ? 'Curated Plan' : 'Exploration Plan'}
              </span>
              <span className={`text-[10px] font-sans font-semibold uppercase tracking-wider px-2 py-0.5 rounded ${
                isVerified ? 'bg-forest-100 text-forest-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {isVerified ? 'Verified Benchmarks' : 'Standardized Baseline'}
              </span>
            </div>
            <h2 className="font-serif text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight">
              {itinerary.title}
            </h2>
            <p className="text-xs sm:text-sm text-charcoal-600 mt-1 max-w-2xl leading-relaxed">
              {itinerary.summary}
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              type="button"
              onClick={onToggleSave}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-colors border ${
                isSaved
                  ? 'bg-forest-900 text-canvas border-forest-900 shadow-subtle'
                  : 'bg-canvas text-charcoal-700 border-sand-300 hover:bg-sand-100/60'
              }`}
              aria-label={isSaved ? 'Trip saved' : 'Save this itinerary'}
            >
              {isSaved ? (
                <>
                  <BookmarkCheck className="w-4 h-4 text-forest-300" />
                  <span>Saved</span>
                </>
              ) : (
                <>
                  <Bookmark className="w-4 h-4 text-charcoal-400" />
                  <span>Save Plan</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Status Notice */}
        {!isVerified ? (
          <div className="bg-amber-50/80 border border-amber-200/80 rounded-xl p-3 flex items-start gap-2.5 text-xs text-amber-900 leading-snug">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <span>
              <strong>Limited Information Notice:</strong> This destination is not yet in our curated regional database. We provide general structure and baseline estimates; exact attraction admissions, specific opening hours, and travel distances are not verified.
            </span>
          </div>
        ) : (
          <div className="bg-sand-50/70 border border-sand-200/60 rounded-xl p-3 flex items-start gap-2.5 text-xs text-charcoal-600 leading-snug">
            <Info className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
            <span>
              <strong>FastAPI Planning Engine:</strong> Displaying verified regional benchmarks calculated on the Python backend with Strands Decider 2B autonomous reasoning and Amazon Bedrock enrichment.
            </span>
          </div>
        )}
      </div>

      {/* Amazon Bedrock Generative Intelligence Card */}
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 sm:p-7 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-sand-100 pb-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-forest-900 text-canvas flex items-center justify-center shadow-subtle shrink-0">
              <Sparkles className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-lg font-bold text-charcoal-900">
                  Bedrock Generative Intelligence
                </h3>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-sand-100 text-charcoal-700 border border-sand-200">
                  Claude 3.5 Sonnet
                </span>
              </div>
              <p className="text-xs text-charcoal-500">
                AI travel synthesis powered by Amazon Bedrock • Deterministic pricing remains source of truth
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {aiEnrichment?.status === 'enriched' ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-forest-100 text-forest-800 border border-forest-200">
                <ShieldCheck className="w-3.5 h-3.5 text-forest-700" />
                <span>Enriched ({Math.round(aiEnrichment.latencyMs || 0)}ms)</span>
              </span>
            ) : aiEnrichment?.status === 'provider_unavailable' ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                <Info className="w-3.5 h-3.5 text-amber-700" />
                <span>Bedrock Offline</span>
              </span>
            ) : aiEnrichment?.status === 'error' ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
                <Info className="w-3.5 h-3.5 text-amber-800" />
                <span>Bedrock Notice</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-sand-100 text-charcoal-700 border border-sand-200">
                <span>Deterministic Mode</span>
              </span>
            )}

            {onEnrichItinerary && (
              <button
                type="button"
                onClick={onEnrichItinerary}
                disabled={isEnriching}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors border shadow-subtle ${
                  isEnriching
                    ? 'bg-sand-100 text-charcoal-500 border-sand-200 cursor-wait'
                    : 'bg-forest-900 text-canvas border-forest-900 hover:bg-forest-950 active:scale-95'
                }`}
                aria-label="Enrich itinerary using Amazon Bedrock"
              >
                {isEnriching ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Synthesizing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                    <span>{aiEnrichment?.status === 'enriched' ? 'Re-enrich Narrative' : 'Enrich with Bedrock'}</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Enrichment Body */}
        {aiEnrichment?.status === 'enriched' ? (
          <div className="space-y-4">
            {/* Travel Narrative */}
            {aiEnrichment.narrative && (
              <div className="bg-sand-50/70 border border-sand-200/80 rounded-xl p-4 sm:p-5">
                <span className="text-[10px] uppercase font-bold tracking-wider text-forest-800 block mb-1">
                  Synthesized Travel Narrative
                </span>
                <p className="font-serif text-base sm:text-lg text-charcoal-800 italic leading-relaxed">
                  "{aiEnrichment.narrative}"
                </p>
              </div>
            )}

            {/* Cultural & Food Guides Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {aiEnrichment.culturalGuidance && (
                <div className="border border-sand-200 rounded-xl p-4 bg-canvas flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <Compass className="w-4 h-4 text-forest-700 shrink-0" />
                      <h4 className="text-xs font-bold text-charcoal-900 uppercase tracking-wide">
                        Cultural Guidance & Etiquette
                      </h4>
                    </div>
                    <p className="text-xs text-charcoal-700 leading-relaxed">
                      {aiEnrichment.culturalGuidance}
                    </p>
                  </div>
                </div>
              )}

              {aiEnrichment.localFoodGuide && (
                <div className="border border-sand-200 rounded-xl p-4 bg-canvas flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <Utensils className="w-4 h-4 text-amber-700 shrink-0" />
                      <h4 className="text-xs font-bold text-charcoal-900 uppercase tracking-wide">
                        Regional Food & Dining Guide
                      </h4>
                    </div>
                    <p className="text-xs text-charcoal-700 leading-relaxed">
                      {aiEnrichment.localFoodGuide}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : aiEnrichment?.status === 'provider_unavailable' ? (
          <div className="bg-sand-50/70 border border-sand-200/80 rounded-xl p-4 flex items-start gap-3 text-xs text-charcoal-600">
            <Info className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong className="text-charcoal-800">Bedrock Runtime Offline: </strong>
              <span>
                {aiEnrichment.error || 'AWS credentials are not configured in this environment. Your verified deterministic itinerary, attraction schedules, and budget calculations remain fully active.'}
              </span>
            </div>
          </div>
        ) : aiEnrichment?.status === 'error' ? (
          <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-4 flex items-start gap-3 text-xs text-amber-900">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong className="text-amber-950">Bedrock Notice: </strong>
              <span>
                {aiEnrichment.error || 'Generative synthesis was interrupted. Your verified deterministic itinerary and budget remain fully intact.'}
              </span>
            </div>
          </div>
        ) : (
          <div className="bg-sand-50/60 border border-sand-200/60 rounded-xl p-3.5 flex items-center justify-between text-xs text-charcoal-600">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                Enrich this plan with Amazon Bedrock Claude for personalized narratives, regional food guides, and cultural tips.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Adaptive Planning Preview: Adjust Your Trip */}
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 sm:p-7 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-sand-100 pb-4 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-forest-100 text-forest-800 flex items-center justify-center">
              {isAdapting ? (
                <Loader2 className="w-4 h-4 animate-spin text-forest-700" />
              ) : (
                <Sliders className="w-4 h-4" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-lg font-bold text-charcoal-900">
                  Adjust your trip
                </h3>
                {isAdapting && (
                  <span className="text-[11px] text-forest-700 font-medium animate-pulse">
                    Adapting via FastAPI...
                  </span>
                )}
              </div>
              <p className="text-xs text-charcoal-500">
                Preview how itinerary constraints adapt calculations in real time
              </p>
            </div>
          </div>
          <span className="text-[10px] uppercase font-semibold text-charcoal-500 bg-sand-100 px-2 py-0.5 rounded self-start sm:self-center">
            FastAPI Deterministic Engine
          </span>
        </div>

        {/* Three Functional Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Control 1: Reduce the budget */}
          <div className="border border-sand-200 rounded-xl p-3.5 bg-canvas flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-charcoal-900">
                  Reduce Budget
                </span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                  budgetOptimized ? 'bg-forest-100 text-forest-800' : 'bg-sand-200 text-charcoal-600'
                }`}>
                  {budgetOptimized ? 'Active (-20%)' : 'Standard'}
                </span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-tight mb-3">
                Switches to economy homestays, self-guided passes, and local transport options.
              </p>
            </div>
            <button
              type="button"
              onClick={onToggleBudgetOptimization}
              disabled={isAdapting}
              className={`w-full py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border ${
                isAdapting ? 'opacity-60 cursor-wait' : ''
              } ${
                budgetOptimized
                  ? 'bg-forest-800 text-canvas border-forest-800'
                  : 'bg-canvas-card text-charcoal-700 border-sand-300 hover:bg-sand-100/60'
              }`}
            >
              <TrendingDown className="w-3.5 h-3.5" />
              <span>{budgetOptimized ? 'Reset to Standard' : 'Apply Economy Rates'}</span>
            </button>
          </div>

          {/* Control 2: Shorten the trip */}
          <div className="border border-sand-200 rounded-xl p-3.5 bg-canvas flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-charcoal-900">
                  Shorten Trip
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-sand-200 text-charcoal-700">
                  {activeDays.length} {activeDays.length === 1 ? 'Day' : 'Days'}
                </span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-tight mb-3">
                Compress schedule to essential highlights to reduce accommodation and transport expenses.
              </p>
            </div>
            <button
              type="button"
              onClick={onShortenTrip}
              disabled={!canShortenTrip || isAdapting}
              className={`w-full py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border ${
                canShortenTrip && !isAdapting
                  ? 'bg-canvas-card text-charcoal-800 border-sand-300 hover:bg-sand-100/80 active:bg-sand-200'
                  : 'bg-sand-100 text-charcoal-400 border-sand-200 cursor-not-allowed opacity-60'
              }`}
            >
              <MinusCircle className="w-3.5 h-3.5" />
              <span>{canShortenTrip ? 'Remove 1 Day' : 'Minimum 1 Day Reached'}</span>
            </button>
          </div>

          {/* Control 3: Change travel style */}
          <div className="border border-sand-200 rounded-xl p-3.5 bg-canvas flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-charcoal-900">
                  Travel Style
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded capitalize bg-forest-100 text-forest-800">
                  {travelStyle}
                </span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-tight mb-3">
                Recalibrates accommodation class, transit mode, and daily hospitality benchmarks.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-1">
              {['budget', 'balanced', 'comfort'].map((styleKey) => (
                <button
                  key={styleKey}
                  type="button"
                  onClick={() => onTravelStyleChange(styleKey)}
                  disabled={isAdapting}
                  className={`py-1.5 text-[11px] font-semibold rounded capitalize transition-colors ${
                    isAdapting ? 'opacity-60 cursor-wait' : ''
                  } ${
                    travelStyle === styleKey
                      ? 'bg-forest-900 text-canvas font-bold'
                      : 'bg-canvas-card text-charcoal-600 border border-sand-200 hover:bg-sand-100/60'
                  }`}
                >
                  {styleKey}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Official Verified Booking Advisory & IRCTC Transit Link */}
      <div className="bg-sand-50/90 border border-sand-200/90 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-card">
        <div className="flex items-start sm:items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-forest-700 shrink-0 mt-0.5 sm:mt-0" />
          <div className="leading-snug">
            <span className="font-bold text-charcoal-800">Verified Booking Resources: </span>
            <span className="text-charcoal-600">
              Activity links open official monument authorities and government tourism portals in a new tab. TripPilot never requests or collects payment information.
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <a
            href="https://www.irctc.co.in/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-canvas border border-sand-300 text-charcoal-800 hover:text-forest-900 hover:border-forest-400 transition-colors shadow-subtle"
            title="Official Indian Railway Catering and Tourism Corporation Portal"
          >
            <span>🚆 IRCTC Indian Railways ↗</span>
            <ExternalLink className="w-3 h-3 text-charcoal-400" />
          </a>
        </div>
      </div>

      {/* Day Navigation Tabs */}
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 shadow-card">
        <div className="flex items-center justify-between border-b border-sand-200 pb-3 mb-6 gap-3">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin flex-1">
            {activeDays.map((day) => {
              const isSelected = selectedDayTab === day.dayNumber;
              return (
                <button
                  key={day.dayNumber}
                  type="button"
                  onClick={() => setSelectedDayTab(day.dayNumber)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-forest-900 text-canvas shadow-subtle'
                      : 'bg-sand-100/80 text-charcoal-600 hover:bg-sand-200/70 hover:text-charcoal-900'
                  }`}
                  aria-pressed={isSelected}
                >
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Day {day.dayNumber}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-1 shrink-0 bg-sand-50 p-1 rounded-xl border border-sand-200/70">
            <button
              type="button"
              disabled={selectedDayTab <= 1}
              onClick={() => setSelectedDayTab(prev => Math.max(1, prev - 1))}
              className="px-2 py-1 rounded-lg text-xs font-semibold text-charcoal-700 hover:bg-sand-200/80 disabled:opacity-30 disabled:hover:bg-transparent disabled:cursor-not-allowed transition-colors"
              aria-label="Previous Day"
            >
              Prev
            </button>
            <span className="text-xs text-charcoal-600 font-bold px-1.5 whitespace-nowrap">
              {currentDay.dayNumber} of {activeDays.length}
            </span>
            <button
              type="button"
              disabled={selectedDayTab >= activeDays.length}
              onClick={() => setSelectedDayTab(prev => Math.min(activeDays.length, prev + 1))}
              className="px-2 py-1 rounded-lg text-xs font-semibold text-charcoal-700 hover:bg-sand-200/80 disabled:opacity-30 disabled:hover:bg-transparent disabled:cursor-not-allowed transition-colors"
              aria-label="Next Day"
            >
              Next
            </button>
          </div>
        </div>

        {/* View Mode Toggle: Schedule View vs Route Map View */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-4 border-b border-sand-100">
          <div className="inline-flex items-center gap-1.5 bg-sand-100/90 p-1 rounded-xl border border-sand-200">
            <button
              type="button"
              onClick={() => setViewMode('schedule')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                viewMode === 'schedule'
                  ? 'bg-canvas text-charcoal-900 shadow-subtle border border-sand-200'
                  : 'text-charcoal-600 hover:text-charcoal-900'
              }`}
              aria-pressed={viewMode === 'schedule'}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Schedule View</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('map')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                viewMode === 'map'
                  ? 'bg-canvas text-charcoal-900 shadow-subtle border border-sand-200'
                  : 'text-charcoal-600 hover:text-charcoal-900'
              }`}
              aria-pressed={viewMode === 'map'}
            >
              <Navigation className="w-3.5 h-3.5 text-forest-700" />
              <span>Route Map View</span>
              {currentDay.dayRouteDistanceKm !== null && currentDay.dayRouteDistanceKm !== undefined && (
                <span className="text-[10px] font-mono bg-forest-100 text-forest-800 px-1.5 py-0.5 rounded">
                  {currentDay.hasRoadRoutes ? '🛣️ ' : '~'}{currentDay.dayRouteDistanceKm} km
                </span>
              )}

            </button>
          </div>

          <div className="flex items-center gap-2 text-xs text-charcoal-500">
            {itinerary.totalRouteDistanceKm !== null && itinerary.totalRouteDistanceKm !== undefined && (
              <span className="inline-flex items-center gap-1 bg-sand-50 border border-sand-200 px-2.5 py-1 rounded-lg">
                <span className="text-charcoal-600">Total Route:</span>
                <strong className="text-forest-900 font-mono">~{itinerary.totalRouteDistanceKm} km</strong>
              </span>
            )}
            <span className="text-[11px] text-charcoal-400">
              {viewMode === 'map' ? 'Interactive OpenStreetMap Leaflet' : 'Detailed Day Timeline'}
            </span>
          </div>
        </div>

        {/* View Mode Content: MapPanel or Schedule Cards */}
        {viewMode === 'map' ? (
          <MapPanel
            currentDay={currentDay}
            mapCenter={itinerary.mapCenter || itinerary.destination?.centerCoordinates}
            destination={itinerary.destination}
            totalRouteDistanceKm={itinerary.totalRouteDistanceKm}
            isVerified={isVerified}
          />
        ) : (
          <div>
            {/* Current Day Theme Headline & Daily Cost Breakdown */}
            <div className="mb-6 bg-sand-50/70 p-4 sm:p-5 rounded-xl border border-sand-200/70 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-sand-200/60 pb-3">
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-forest-800 mb-0.5">
                    Day {currentDay.dayNumber} Focus
                  </div>
                  <h4 className="font-serif text-lg sm:text-xl font-bold text-charcoal-900">
                    {currentDay.theme}
                  </h4>
                </div>
                <button
                  type="button"
                  onClick={toggleExpandAll}
                  className="text-[11px] font-semibold text-forest-800 hover:text-forest-950 bg-canvas border border-sand-300 hover:border-sand-400 px-3 py-1.5 rounded-lg flex items-center gap-1.5 self-start sm:self-center transition-colors shadow-subtle shrink-0"
                  aria-label={expandAll ? 'Collapse activity tips' : 'Expand all activity tips'}
                >
                  {expandAll ? <EyeOff className="w-3.5 h-3.5 text-forest-700" /> : <Eye className="w-3.5 h-3.5 text-forest-700" />}
                  <span>{expandAll ? 'Collapse Details' : 'Expand Details & Tips'}</span>
                </button>
              </div>

              {/* Daily Budget Transparency Bar */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2.5 pt-0.5 text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[11px] font-bold text-charcoal-700 uppercase tracking-wide">
                    Day {currentDay.dayNumber} Est. Total:
                  </span>
                  <span className="font-serif text-base font-bold text-forest-900">
                    {formatINR(currentDay.dayTotal || ((currentDay.dayStay || 0) + (currentDay.dayFood || 0) + (currentDay.dayTransit || 0) + (currentDay.dayActivities || 0)))}
                  </span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    currentDay.isCostVerified !== false && isVerified !== false
                      ? 'bg-forest-100 text-forest-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {currentDay.isCostVerified !== false && isVerified !== false ? 'Verified Tariff' : 'Baseline Estimate'}
                  </span>
                </div>

                {/* Daily Component Breakdown Pills */}
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-charcoal-600">
                  <span className="bg-canvas border border-sand-200/90 px-2.5 py-1 rounded-md shadow-subtle">
                    Stay: <strong className="text-charcoal-900">{formatINR(currentDay.dayStay || 0)}</strong>
                  </span>
                  <span className="bg-canvas border border-sand-200/90 px-2.5 py-1 rounded-md shadow-subtle">
                    Food: <strong className="text-charcoal-900">{formatINR(currentDay.dayFood || 0)}</strong>
                  </span>
                  <span className="bg-canvas border border-sand-200/90 px-2.5 py-1 rounded-md shadow-subtle">
                    Transit: <strong className="text-charcoal-900">{formatINR(currentDay.dayTransit || 0)}</strong>
                  </span>
                  <span className="bg-canvas border border-sand-200/90 px-2.5 py-1 rounded-md shadow-subtle">
                    Activities: <strong className="text-charcoal-900">{formatINR(currentDay.dayActivities || 0)}</strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Day-specific Bedrock Insight if available */}
            {(() => {
              const insight = aiEnrichment?.dailyInsights?.find(
                (ins) => (ins.dayNumber || ins.day_number) === currentDay.dayNumber
              );
              if (!insight || (!insight.themeNote && !insight.practicalTip && !insight.culinaryHighlight)) {
                return null;
              }
              return (
                <div className="mb-6 bg-forest-50/40 border border-forest-200/60 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2.5">
                    <Sparkles className="w-4 h-4 text-forest-700" />
                    <span className="text-xs font-bold text-forest-900 uppercase tracking-wider">
                      Day {currentDay.dayNumber} AI Insights (Bedrock)
                    </span>
                    <span className="text-[10px] text-charcoal-400 font-medium">
                      Advisory narrative based on verified schedule
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    {insight.themeNote && (
                      <div className="bg-canvas p-3 rounded-lg border border-sand-200/80 shadow-subtle">
                        <span className="text-[10px] font-bold text-forest-800 uppercase block mb-1">
                          Daily Focus Note
                        </span>
                        <p className="text-charcoal-700 leading-snug">{insight.themeNote}</p>
                      </div>
                    )}
                    {insight.practicalTip && (
                      <div className="bg-canvas p-3 rounded-lg border border-sand-200/80 shadow-subtle">
                        <span className="text-[10px] font-bold text-amber-800 uppercase block mb-1">
                          Practical Packing & Timing
                        </span>
                        <p className="text-charcoal-700 leading-snug">{insight.practicalTip}</p>
                      </div>
                    )}
                    {insight.culinaryHighlight && (
                      <div className="bg-canvas p-3 rounded-lg border border-sand-200/80 shadow-subtle">
                        <span className="text-[10px] font-bold text-terracotta-800 uppercase block mb-1">
                          Culinary Highlight
                        </span>
                        <p className="text-charcoal-700 leading-snug">{insight.culinaryHighlight}</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}

            {/* Morning, Afternoon, Evening Cards */}
            <div className="space-y-4">
              {timeSlots.map((slot, slotIndex) => {
                const activity = currentDay[slot.key];
                if (!activity) return null;
                const SlotIcon = slot.icon;
                const displayCost = activity.cost;
                const cardKey = `${currentDay.dayNumber}-${slot.key}`;
                const isTipExpanded = expandedTips[cardKey] ?? expandAll;

                // Find connecting transit segment to next stop
                const nextSlotKey = timeSlots[slotIndex + 1]?.key;
                const transitSegment = currentDay.routeSegments?.find(
                  (s) => s.fromSlot === slot.key && s.toSlot === nextSlotKey
                );

                return (
                  <React.Fragment key={slot.key}>
                    <div className="relative border border-sand-200 rounded-xl p-5 bg-canvas hover:border-sand-300 transition-colors shadow-subtle">
                      {/* Header Row: Slot badge, Time, Duration, Cost */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold border ${slot.slotColor}`}>
                            <SlotIcon className="w-3.5 h-3.5" />
                            <span>{slot.label}</span>
                          </span>
                          <span className="text-xs font-medium text-charcoal-500 flex items-center gap-1 bg-sand-50 px-2 py-0.5 rounded border border-sand-200/60">
                            <Clock className="w-3 h-3 text-charcoal-400" />
                            <span>{activity.time}</span>
                          </span>
                          {activity.duration && (
                            <span className="text-[11px] font-semibold text-charcoal-600 bg-sand-100/90 px-2 py-0.5 rounded border border-sand-200/80">
                              ⏱ ~{activity.duration}
                            </span>
                          )}
                        </div>

                        {/* Cost Tag */}
                        <div className="flex items-center gap-1 text-xs font-bold text-forest-900 bg-forest-50 px-2.5 py-1 rounded-md border border-forest-200/60 self-start sm:self-auto">
                          <span className="text-[11px] font-medium text-forest-700">Est. Fee:</span>
                          <span>{displayCost > 0 ? formatINR(displayCost) : (isVerified ? 'Free admission' : '₹0 (Unverified)')}</span>
                        </div>
                      </div>

                      {/* Activity Title */}
                      <h5 className="font-serif text-base sm:text-lg font-bold text-charcoal-900 mb-1">
                        {activity.title}
                      </h5>

                      {/* Location & Coordinates Precision Tag */}
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-1.5 text-xs text-charcoal-500">
                          <MapPin className="w-3.5 h-3.5 text-forest-700 shrink-0" />
                          <span>{activity.location}</span>
                        </div>

                        {activity.coordinates && (
                          <button
                            type="button"
                            onClick={() => setViewMode('map')}
                            className="inline-flex items-center gap-1 text-[10px] font-bold text-forest-800 bg-forest-50 hover:bg-forest-100 px-2 py-0.5 rounded border border-forest-200 transition-colors"
                            title="Click to inspect stop on interactive map"
                          >
                            <span>📍 Verified Landmark</span>
                            <span className="text-forest-600 font-normal">• View Map →</span>
                          </button>
                        )}
                      </div>

                      {/* Explanation / Why It's Worth Doing */}
                      <p className="text-xs sm:text-sm text-charcoal-700 leading-relaxed bg-white/70 p-3 rounded-lg border border-sand-100 mb-3">
                        {activity.explanation}
                      </p>

                      {/* Route & Travel Time Strip */}
                      {activity.transitNote && (
                        <div className="flex items-start gap-2 bg-sand-50/70 border border-sand-200/70 rounded-lg p-2.5 text-xs text-charcoal-600 leading-snug mb-3">
                          <Navigation className="w-3.5 h-3.5 text-forest-700 shrink-0 mt-0.5" />
                          <div>
                            <strong className="text-charcoal-800 font-semibold">Route & Transit: </strong>
                            <span>{activity.transitNote}</span>
                          </div>
                        </div>
                      )}

                      {/* Verified Booking & Official Visitor Portal */}
                      <div className="mb-3">
                        {activity.bookingResource ? (
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3 rounded-xl bg-sand-50/80 border border-sand-200/90 text-xs shadow-subtle">
                            <div className="flex items-start gap-2.5">
                              <Ticket className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
                              <div>
                                <div className="flex items-center gap-1.5 flex-wrap">
                                  <span className="font-bold text-charcoal-800">
                                    {activity.bookingResource.providerName}
                                  </span>
                                  <span className="text-[10px] font-bold bg-forest-100 text-forest-800 px-1.5 py-0.5 rounded border border-forest-200">
                                    Verified Official Portal
                                  </span>
                                </div>
                                {activity.bookingResource.description && (
                                  <p className="text-[11px] text-charcoal-500 leading-snug mt-0.5">
                                    {activity.bookingResource.description}
                                  </p>
                                )}
                              </div>
                            </div>
                            <a
                              href={activity.bookingResource.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-forest-800 hover:bg-forest-900 text-canvas shadow-subtle transition-colors shrink-0 self-start sm:self-center"
                              aria-label={`Open verified official portal for ${activity.title} in new tab`}
                            >
                              <span>{activity.bookingResource.label || 'Official Portal ↗'}</span>
                              <ExternalLink className="w-3 h-3 text-canvas/80" />
                            </a>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-sand-50/60 border border-sand-200/60 text-[11px] text-charcoal-500">
                            <Info className="w-3.5 h-3.5 text-charcoal-400 shrink-0" />
                            <span>
                              {displayCost === 0
                                ? 'Free admission • No advance online booking required'
                                : 'On-site ticketing at entrance • No advance online booking verified'}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Practical Tips Toggle Button */}
                      <div className="pt-2 border-t border-sand-100 flex items-center justify-between">
                        <button
                          type="button"
                          onClick={() => toggleTip(slot.key)}
                          className="text-xs font-semibold text-forest-800 hover:text-forest-950 flex items-center gap-1.5 transition-colors group"
                        >
                          <Lightbulb className="w-3.5 h-3.5 text-amber-600" />
                          <span>{isTipExpanded ? 'Hide Practical Tips & Dining' : 'View Practical Tips & Dining'}</span>
                          {isTipExpanded ? (
                            <ChevronUp className="w-3.5 h-3.5 text-forest-700" />
                          ) : (
                            <ChevronDown className="w-3.5 h-3.5 text-forest-700 transition-transform group-hover:translate-y-0.5" />
                          )}
                        </button>
                        <span className="text-[10px] text-charcoal-400 font-medium">
                          {isVerified ? 'Verified Benchmark' : 'Baseline Estimate'}
                        </span>
                      </div>

                      {/* Expandable Practical Tips & Culinary Suggestions */}
                      {isTipExpanded && (
                        <div className="mt-3 pt-3 border-t border-sand-200/60 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {/* Practical Tips Box */}
                          <div className="bg-sand-50/70 border border-sand-200/70 rounded-xl p-3 flex flex-col justify-between">
                            <div>
                              <div className="flex items-center gap-1.5 font-bold text-charcoal-900 mb-1">
                                <Lightbulb className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                                <span>Practical Tips & Gear</span>
                              </div>
                              <p className="text-charcoal-600 leading-relaxed text-[11px]">
                                {activity.practicalTips || 'Confirm local opening hours and attire guidelines on arrival. Carry water and cash for local transactions.'}
                              </p>
                            </div>
                          </div>

                          {/* Culinary / Food Experience Box */}
                          <div className="bg-forest-50/40 border border-forest-200/60 rounded-xl p-3 flex flex-col justify-between">
                            <div>
                              <div className="flex items-center gap-1.5 font-bold text-forest-900 mb-1">
                                <Utensils className="w-3.5 h-3.5 text-forest-700 shrink-0" />
                                <span>Regional Food Experience</span>
                              </div>
                              <p className="text-charcoal-600 leading-relaxed text-[11px]">
                                {activity.mealSuggestion || 'Inquire with local residents or guesthouse hosts for authentic regional delicacies nearby.'}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Connecting Transit Segment Strip between stops */}
                    {transitSegment && transitSegment.isRouteCalculated && (
                      <div className="mx-2 sm:mx-6 my-1 py-1.5 px-3 rounded-lg bg-sand-100/70 border border-sand-200/80 flex items-center justify-between text-xs text-charcoal-600 shadow-subtle">
                        <div className="flex items-center gap-2">
                          <Navigation className="w-3.5 h-3.5 text-forest-700 shrink-0" />
                          <span className="font-semibold text-charcoal-800 capitalize">
                            Transfer: {transitSegment.fromSlot} → {transitSegment.toSlot}
                          </span>
                          <span className="text-[11px] text-charcoal-500">
                            ({transitSegment.routeType === 'road' ? '🛣️ Road: ' : '📐 Est: '}~{transitSegment.distanceKm} km • ~{transitSegment.durationMinutes} min via {transitSegment.transitMode?.replace('_', ' ')})
                          </span>

                        </div>
                        <button
                          type="button"
                          onClick={() => setViewMode('map')}
                          className="text-[11px] font-bold text-forest-800 hover:text-forest-950 hover:underline shrink-0"
                        >
                          View on Map →
                        </button>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

