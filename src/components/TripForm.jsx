import React, { useState } from 'react';
import { 
  MapPin, 
  Calendar, 
  IndianRupee, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2,
  Landmark,
  UtensilsCrossed,
  Mountain,
  Compass,
  Footprints,
  Loader2
} from 'lucide-react';
import { destinations as defaultDestinations, interestOptions, travelStyles, startingCities } from '../data/destinations';
import { formatINR } from '../utils/formatters';

const iconMap = {
  Landmark,
  UtensilsCrossed,
  Mountain,
  Compass,
  Footprints
};

export default function TripForm({
  formData,
  onChange,
  onSubmit,
  hasBuiltItinerary = false,
  isLoading = false,
  destinationsList = defaultDestinations
}) {
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};

    if (!formData.startingCity || formData.startingCity.trim().length < 2) {
      newErrors.startingCity = 'Please specify your departure city (at least 2 characters).';
    }

    if (formData.isCustomDestination || formData.destinationId === 'custom') {
      if (!formData.customDestinationName || formData.customDestinationName.trim().length < 2) {
        newErrors.customDestinationName = 'Please enter a destination name (at least 2 characters).';
      }
    } else if (!formData.destinationId) {
      newErrors.destinationId = 'Please select a destination.';
    }

    const daysNum = Number(formData.days);
    if (!daysNum || isNaN(daysNum) || daysNum < 1) {
      newErrors.days = 'Duration must be at least 1 day.';
    } else if (daysNum > 30) {
      newErrors.days = 'Duration cannot exceed 30 days.';
    }

    const budgetNum = Number(formData.budget);
    if (!budgetNum || isNaN(budgetNum) || budgetNum < 5000) {
      newErrors.budget = 'Please enter a realistic minimum budget of at least ₹5,000.';
    }

    if (!formData.interests || formData.interests.length === 0) {
      newErrors.interests = 'Select at least one travel interest.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit();
    }
  };

  const handleInterestToggle = (interestId) => {
    const current = formData.interests || [];
    let updated;
    if (current.includes(interestId)) {
      if (current.length === 1) {
        // Prevent deselecting the last remaining interest
        return;
      }
      updated = current.filter(id => id !== interestId);
    } else {
      updated = [...current, interestId];
    }
    onChange({ ...formData, interests: updated });
    if (errors.interests) {
      setErrors(prev => ({ ...prev, interests: null }));
    }
  };

  const handlePresetBudget = (amount) => {
    onChange({ ...formData, budget: amount });
    if (errors.budget) {
      setErrors(prev => ({ ...prev, budget: null }));
    }
  };

  // Live daily budget calculation for immediate user feedback
  const numericBudget = Number(formData.budget);
  const numericDays = Number(formData.days);
  const hasValidDailyBudget =
    !isNaN(numericBudget) &&
    numericBudget > 0 &&
    !isNaN(numericDays) &&
    numericDays > 0;
  const dailyBudgetAmount = hasValidDailyBudget ? Math.round(numericBudget / numericDays) : null;

  return (
    <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 sm:p-8 shadow-card">
      {/* Editorial Header */}
      <div className="mb-6 border-b border-sand-100 pb-5">
        <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-forest-700 bg-forest-50 px-2.5 py-1 rounded-md mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Interactive Planner</span>
        </div>
        <h2 className="font-serif text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight">
          Plan a trip that fits your budget.
        </h2>
        <p className="mt-1.5 text-sm text-charcoal-600 leading-relaxed">
          Configure your departure city, duration, and pace. TripPilot structures a balanced daily itinerary with itemized costs before intelligent optimization kicks in.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-6">
        {/* Row 1: Departure & Destination */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Starting City */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="startingCity" className="block text-xs font-semibold text-charcoal-800 uppercase tracking-wider">
                Starting City <span className="text-terracotta-500">*</span>
              </label>
              <span className="text-[11px] text-charcoal-500">Any city or airport</span>
            </div>
            <div className="relative">
              <input
                type="text"
                id="startingCity"
                list="startingCitiesList"
                placeholder="e.g. Bengaluru, Mumbai, Pune..."
                value={formData.startingCity || ''}
                onChange={(e) => {
                  onChange({ ...formData, startingCity: e.target.value });
                  if (errors.startingCity) setErrors(prev => ({ ...prev, startingCity: null }));
                }}
                className={`w-full rounded-lg border bg-canvas px-3.5 py-2.5 pl-9 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700 ${
                  errors.startingCity ? 'border-terracotta-500 bg-red-50/20' : 'border-sand-300'
                }`}
              />
              <MapPin className="pointer-events-none absolute left-3 top-3 w-4 h-4 text-charcoal-400" />
              <datalist id="startingCitiesList">
                {startingCities.map((city) => (
                  <option key={city} value={city} />
                ))}
              </datalist>
            </div>
            {/* Quick Hub Suggestions */}
            <div className="mt-1.5 flex flex-wrap items-center gap-1">
              <span className="text-[10px] text-charcoal-500 font-medium mr-0.5">Popular:</span>
              {['Bengaluru', 'Mumbai', 'Delhi NCR', 'Hyderabad', 'Chennai'].map((hub) => (
                <button
                  key={hub}
                  type="button"
                  onClick={() => {
                    onChange({ ...formData, startingCity: hub });
                    if (errors.startingCity) setErrors(prev => ({ ...prev, startingCity: null }));
                  }}
                  className={`text-[10px] px-1.5 py-0.5 rounded transition-colors ${
                    formData.startingCity === hub
                      ? 'bg-forest-100 text-forest-900 font-semibold border border-forest-300'
                      : 'bg-sand-100 text-charcoal-600 hover:bg-sand-200/70 border border-sand-200/60'
                  }`}
                >
                  {hub.replace(' NCR', '')}
                </button>
              ))}
            </div>
            {errors.startingCity && (
              <p className="mt-1.5 flex items-center gap-1 text-xs text-terracotta-600">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{errors.startingCity}</span>
              </p>
            )}
          </div>

          {/* Destination */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="destinationId" className="block text-xs font-semibold text-charcoal-800 uppercase tracking-wider">
                Destination <span className="text-terracotta-500">*</span>
              </label>
              <span className="text-[11px] text-charcoal-500">
                {formData.destinationId === 'custom' || formData.isCustomDestination ? 'Manual Entry' : `${destinationsList.length} Curated`}
              </span>
            </div>
            <div className="relative">
              <select
                id="destinationId"
                value={formData.isCustomDestination ? 'custom' : formData.destinationId}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val === 'custom') {
                    onChange({
                      ...formData,
                      destinationId: 'custom',
                      isCustomDestination: true,
                      customDestinationName: formData.customDestinationName || ''
                    });
                  } else {
                    onChange({
                      ...formData,
                      destinationId: val,
                      isCustomDestination: false,
                      customDestinationName: ''
                    });
                  }
                  if (errors.destinationId) setErrors(prev => ({ ...prev, destinationId: null }));
                  if (errors.customDestinationName) setErrors(prev => ({ ...prev, customDestinationName: null }));
                }}
                className={`w-full appearance-none rounded-lg border bg-canvas px-3.5 py-2.5 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700 ${
                  errors.destinationId ? 'border-terracotta-500 bg-red-50/20' : 'border-sand-300'
                }`}
              >
                <option value="">Choose a destination in India...</option>
                <optgroup label="Curated Destinations (Verified Benchmarks)">
                  {destinationsList.map((dest) => (
                    <option key={dest.id} value={dest.id}>
                      {dest.name}, {dest.state} ({dest.indicativeRange})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Custom Exploration">
                  <option value="custom">+ Enter another destination in India...</option>
                </optgroup>
              </select>
              <MapPin className="pointer-events-none absolute right-3.5 top-3 w-4 h-4 text-forest-700" />
            </div>

            {/* Custom Destination Text Input when 'custom' is selected */}
            {(formData.destinationId === 'custom' || formData.isCustomDestination) && (
              <div className="mt-2.5 space-y-2">
                <div className="relative">
                  <input
                    type="text"
                    id="customDestinationName"
                    placeholder="Enter destination name (e.g. Coorg, Pondicherry, Spiti Valley)"
                    value={formData.customDestinationName || ''}
                    onChange={(e) => {
                      onChange({
                        ...formData,
                        destinationId: 'custom',
                        isCustomDestination: true,
                        customDestinationName: e.target.value
                      });
                      if (errors.customDestinationName) setErrors(prev => ({ ...prev, customDestinationName: null }));
                    }}
                    className={`w-full rounded-lg border bg-canvas px-3.5 py-2 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700 ${
                      errors.customDestinationName ? 'border-terracotta-500 bg-red-50/20' : 'border-sand-300'
                    }`}
                  />
                </div>
                {errors.customDestinationName && (
                  <p className="flex items-center gap-1 text-xs text-terracotta-600">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{errors.customDestinationName}</span>
                  </p>
                )}
                <div className="rounded-lg bg-amber-50/80 border border-amber-200/80 p-2.5 text-xs text-amber-900 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    <strong>Limited information notice:</strong> This location is not in our verified regional database. We provide standardized baseline estimates; attraction admissions and specific distances are not verified.
                  </p>
                </div>
              </div>
            )}

            {errors.destinationId && (
              <p className="mt-1.5 flex items-center gap-1 text-xs text-terracotta-600">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{errors.destinationId}</span>
              </p>
            )}
          </div>
        </div>

        {/* Row 2: Duration & Total Budget */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Days */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="days" className="text-xs font-semibold text-charcoal-800 uppercase tracking-wider">
                Travel Days <span className="text-terracotta-500">*</span>
              </label>
              <span className="text-xs text-charcoal-500 font-medium">1 to 30 days supported</span>
            </div>
            <div className="relative flex items-center">
              <input
                type="number"
                id="days"
                min="1"
                max="30"
                placeholder="e.g. 7"
                value={formData.days}
                onChange={(e) => {
                  const raw = e.target.value;
                  const val = raw === '' ? '' : parseInt(raw, 10);
                  onChange({ ...formData, days: isNaN(val) ? '' : val });
                  if (errors.days) setErrors(prev => ({ ...prev, days: null }));
                }}
                className={`w-full rounded-lg border bg-canvas px-3.5 py-2.5 pl-9 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700 ${
                  errors.days ? 'border-terracotta-500 bg-red-50/20' : 'border-sand-300'
                }`}
              />
              <Calendar className="pointer-events-none absolute left-3 top-3 w-4 h-4 text-charcoal-400" />
            </div>
            {/* Quick Duration Presets */}
            <div className="mt-1.5 flex flex-wrap items-center gap-1">
              <span className="text-[10px] text-charcoal-500 font-medium mr-0.5">Presets:</span>
              {[1, 3, 5, 7, 10, 14, 21].map((presetDays) => (
                <button
                  key={presetDays}
                  type="button"
                  onClick={() => {
                    onChange({ ...formData, days: presetDays });
                    if (errors.days) setErrors(prev => ({ ...prev, days: null }));
                  }}
                  className={`text-[10px] px-1.5 py-0.5 rounded transition-colors ${
                    Number(formData.days) === presetDays
                      ? 'bg-forest-100 text-forest-900 font-semibold border border-forest-300'
                      : 'bg-sand-100 text-charcoal-600 hover:bg-sand-200/70 border border-sand-200/60'
                  }`}
                >
                  {presetDays} {presetDays === 1 ? 'Day' : 'Days'}
                </button>
              ))}
            </div>
            {errors.days && (
              <p className="mt-1.5 flex items-center gap-1 text-xs text-terracotta-600">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{errors.days}</span>
              </p>
            )}
          </div>

          {/* Budget */}
          <div>
            <div className="flex items-center justify-between mb-1.5 gap-2">
              <label htmlFor="budget" className="text-xs font-semibold text-charcoal-800 uppercase tracking-wider shrink-0">
                Total Budget (INR) <span className="text-terracotta-500">*</span>
              </label>
              <div className="flex items-center gap-1.5 flex-wrap justify-end text-right">
                <span className="text-xs font-bold text-forest-900">
                  {formData.budget ? formatINR(Number(formData.budget)) : '₹0'}
                </span>
                {hasValidDailyBudget && (
                  <span className="text-[11px] font-semibold text-forest-800 bg-forest-50 px-1.5 py-0.5 rounded border border-forest-200/70" title="Approximate daily budget; actual spending may vary.">
                    ~{formatINR(dailyBudgetAmount)}/day
                  </span>
                )}
              </div>
            </div>
            <div className="relative">
              <input
                type="number"
                id="budget"
                step="1000"
                min="5000"
                value={formData.budget}
                placeholder="e.g. 25000"
                onChange={(e) => {
                  onChange({ ...formData, budget: e.target.value });
                  if (errors.budget) setErrors(prev => ({ ...prev, budget: null }));
                }}
                className={`w-full rounded-lg border bg-canvas px-3.5 py-2.5 pl-9 text-sm text-charcoal-900 transition-colors focus:border-forest-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-forest-700 ${
                  errors.budget ? 'border-terracotta-500 bg-red-50/20' : 'border-sand-300'
                }`}
              />
              <IndianRupee className="pointer-events-none absolute left-3 top-3 w-4 h-4 text-charcoal-400" />
            </div>
            {/* Quick Budget Presets & Daily Advisory */}
            <div className="mt-1.5 flex flex-wrap items-center justify-between gap-1">
              <div className="flex items-center gap-1">
                <span className="text-[10px] text-charcoal-500 font-medium mr-0.5">Presets:</span>
                {[15000, 25000, 40000, 60000].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => handlePresetBudget(preset)}
                    className={`text-[10px] px-1.5 py-0.5 rounded transition-colors ${
                      Number(formData.budget) === preset
                        ? 'bg-forest-100 text-forest-900 font-semibold border border-forest-300'
                        : 'bg-sand-100 text-charcoal-600 hover:bg-sand-200/70 border border-sand-200/60'
                    }`}
                  >
                    ₹{(preset / 1000)}k
                  </button>
                ))}
              </div>
              {hasValidDailyBudget && (
                <span className="text-[10px] text-charcoal-400 italic">
                  Approximate daily budget; actual spending may vary.
                </span>
              )}
            </div>
            {errors.budget && (
              <p className="mt-1.5 flex items-center gap-1 text-xs text-terracotta-600">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{errors.budget}</span>
              </p>
            )}
          </div>
        </div>

        {/* Row 3: Travel Interests */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold text-charcoal-800 uppercase tracking-wider">
              Travel Interests <span className="text-terracotta-500">*</span>
            </label>
            <span className="text-xs text-charcoal-500">Select what matters most</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
            {interestOptions.map((item) => {
              const Icon = iconMap[item.icon] || Compass;
              const isSelected = (formData.interests || []).includes(item.id);
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleInterestToggle(item.id)}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
                    isSelected
                      ? 'bg-forest-50 border-forest-600 text-forest-900 shadow-subtle ring-1 ring-forest-600'
                      : 'bg-canvas border-sand-200/90 text-charcoal-600 hover:border-sand-300 hover:bg-sand-50'
                  }`}
                  aria-pressed={isSelected}
                >
                  <Icon className={`w-4 h-4 mb-1.5 ${isSelected ? 'text-forest-700' : 'text-charcoal-400'}`} />
                  <span className="text-xs font-medium leading-tight">{item.label}</span>
                </button>
              );
            })}
          </div>
          {errors.interests && (
            <p className="mt-1.5 flex items-center gap-1 text-xs text-terracotta-600">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>{errors.interests}</span>
            </p>
          )}
        </div>

        {/* Row 4: Travel Style */}
        <div>
          <label className="block text-xs font-semibold text-charcoal-800 mb-2 uppercase tracking-wider">
            Travel Style
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {travelStyles.map((style) => {
              const isSelected = formData.travelStyle === style.id;
              return (
                <label
                  key={style.id}
                  className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-forest-50/70 border-forest-600 text-charcoal-900 shadow-subtle ring-1 ring-forest-600'
                      : 'bg-canvas border-sand-200/90 text-charcoal-600 hover:border-sand-300 hover:bg-sand-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="travelStyle"
                    value={style.id}
                    checked={isSelected}
                    onChange={(e) => onChange({ ...formData, travelStyle: e.target.value })}
                    className="sr-only"
                  />
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-bold text-charcoal-900 capitalize">
                      {style.label}
                    </span>
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-forest-700" />
                    )}
                  </div>
                  <span className="text-xs text-charcoal-500 leading-snug">
                    {style.description}
                  </span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-forest-900 text-canvas font-semibold text-sm hover:bg-forest-800 active:bg-forest-950 transition-colors shadow-subtle flex items-center justify-center gap-2.5 focus-visible:ring-2 focus-visible:ring-forest-700 disabled:opacity-75 disabled:cursor-wait"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 text-forest-300 animate-spin" />
                <span>Generating Plan...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-forest-300" />
                <span>Build my itinerary</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
