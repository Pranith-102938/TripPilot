import React from 'react';
import { 
  IndianRupee, 
  Home, 
  Utensils, 
  Car, 
  Ticket, 
  CheckCircle2, 
  AlertTriangle,
  Info
} from 'lucide-react';
import { formatINR } from '../utils/formatters';

export default function BudgetPanel({ calculation }) {
  if (!calculation) return null;

  const {
    numDays,
    dailyStay,
    dailyFood,
    dailyTransit,
    accommodationCost,
    foodCost,
    transportCost,
    activitiesCost,
    totalEstimatedCost,
    userBudget,
    remainingBudget,
    isOverBudget,
    budgetOptimized
  } = calculation;

  // Calculate percentage shares for meaningful horizontal breakdown
  const stayPct = Math.round((accommodationCost / (totalEstimatedCost || 1)) * 100);
  const foodPct = Math.round((foodCost / (totalEstimatedCost || 1)) * 100);
  const transitPct = Math.round((transportCost / (totalEstimatedCost || 1)) * 100);
  const activitiesPct = Math.max(0, 100 - (stayPct + foodPct + transitPct));

  return (
    <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-6 sm:p-7 shadow-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-sand-100 pb-4 mb-5">
        <div>
          <h3 className="font-serif text-xl font-bold text-charcoal-900">
            Trip Budget Breakdown
          </h3>
          <p className="text-xs text-charcoal-500 mt-0.5">
            Itemized estimate for {numDays} {numDays === 1 ? 'day' : 'days'} based on regional pricing
          </p>
        </div>
        <div className="text-right">
          <div className="text-[10px] uppercase font-semibold text-charcoal-400 tracking-wider">
            User Budget
          </div>
          <div className="text-sm font-bold text-charcoal-800">
            {formatINR(userBudget)}
          </div>
        </div>
      </div>

      {/* Unverified Destination Notice */}
      {calculation.isVerified === false && (
        <div className="mb-5 rounded-xl bg-amber-50/80 border border-amber-200/80 p-3 text-xs text-amber-900 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <p className="leading-snug">
            <strong>Limited Data Notice:</strong> Costs for unverified destinations reflect national baseline averages. Specific local transport fares and attraction entry tickets are not verified.
          </p>
        </div>
      )}

      {/* Main Total Highlight */}
      <div className="bg-sand-50/80 border border-sand-200/70 rounded-xl p-4 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className="text-xs font-semibold text-charcoal-600 uppercase tracking-wider block">
            Total Estimated Cost
          </span>
          <span className="text-2xl sm:text-3xl font-bold text-forest-950 font-serif tracking-tight">
            {formatINR(totalEstimatedCost)}
          </span>
          {budgetOptimized && (
            <span className="ml-2 inline-block text-[11px] font-semibold text-forest-700 bg-forest-100 px-2 py-0.5 rounded">
              Economy Rates Active
            </span>
          )}
        </div>

        {/* Budget Status Badge */}
        <div className={`p-3 rounded-lg border flex items-center gap-2.5 ${
          isOverBudget
            ? 'bg-red-50/70 border-red-200 text-terracotta-600'
            : 'bg-forest-50/70 border-forest-200 text-forest-800'
        }`}>
          {isOverBudget ? (
            <AlertTriangle className="w-5 h-5 text-terracotta-500 shrink-0" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-forest-600 shrink-0" />
          )}
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider">
              {isOverBudget ? 'Budget Exceeded' : 'Remaining Budget'}
            </div>
            <div className="text-sm font-bold">
              {isOverBudget 
                ? `+${formatINR(Math.abs(remainingBudget))} over plan`
                : `${formatINR(remainingBudget)} surplus`
              }
            </div>
          </div>
        </div>
      </div>

      {/* Proportional Cost Distribution Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs text-charcoal-500 mb-1.5 font-medium">
          <span>Cost Allocation</span>
          <span>100% accounted</span>
        </div>
        <div className="h-2.5 w-full bg-sand-200 rounded-full overflow-hidden flex" title="Visual cost share">
          <div 
            style={{ width: `${stayPct}%` }} 
            className="bg-forest-800 transition-all duration-300" 
            title={`Accommodation: ${stayPct}%`}
          />
          <div 
            style={{ width: `${foodPct}%` }} 
            className="bg-forest-600 transition-all duration-300" 
            title={`Food: ${foodPct}%`}
          />
          <div 
            style={{ width: `${transitPct}%` }} 
            className="bg-forest-400 transition-all duration-300" 
            title={`Transport: ${transitPct}%`}
          />
          <div 
            style={{ width: `${activitiesPct}%` }} 
            className="bg-sand-400 transition-all duration-300" 
            title={`Activities: ${activitiesPct}%`}
          />
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-[11px] text-charcoal-600">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-forest-800" />
            Stay ({stayPct}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-forest-600" />
            Food ({foodPct}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-forest-400" />
            Transit ({transitPct}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-sand-400" />
            Activities ({activitiesPct}%)
          </span>
        </div>
      </div>

      {/* Itemized Cost Breakdown List */}
      <div className="space-y-3 border-t border-sand-100 pt-4">
        {/* Accommodation */}
        <div className="flex items-center justify-between p-2.5 rounded-lg hover:bg-sand-50 transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-forest-50 text-forest-800 flex items-center justify-center">
              <Home className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-charcoal-900">
                Accommodation
              </div>
              <div className="text-[11px] text-charcoal-500">
                {numDays} {numDays === 1 ? 'day' : 'days'} × {formatINR(dailyStay)}/day
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-charcoal-900">
              {formatINR(accommodationCost)}
            </span>
          </div>
        </div>

        {/* Food & Dining */}
        <div className="flex items-center justify-between p-2.5 rounded-lg hover:bg-sand-50 transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-forest-50 text-forest-800 flex items-center justify-center">
              <Utensils className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-charcoal-900">
                Food & Dining
              </div>
              <div className="text-[11px] text-charcoal-500">
                {numDays} {numDays === 1 ? 'day' : 'days'} × {formatINR(dailyFood)}/day
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-charcoal-900">
              {formatINR(foodCost)}
            </span>
          </div>
        </div>

        {/* Local Transport */}
        <div className="flex items-center justify-between p-2.5 rounded-lg hover:bg-sand-50 transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-forest-50 text-forest-800 flex items-center justify-center">
              <Car className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-charcoal-900">
                Local Transit
              </div>
              <div className="text-[11px] text-charcoal-500">
                {numDays} {numDays === 1 ? 'day' : 'days'} × {formatINR(dailyTransit)}/day
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-charcoal-900">
              {formatINR(transportCost)}
            </span>
          </div>
        </div>

        {/* Activities & Entry */}
        <div className="flex items-center justify-between p-2.5 rounded-lg hover:bg-sand-50 transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sand-100 text-charcoal-700 flex items-center justify-center">
              <Ticket className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-charcoal-900">
                Experiences & Entry Tickets
              </div>
              <div className="text-[11px] text-charcoal-500">
                Sum of itemized stops across {numDays} {numDays === 1 ? 'day' : 'days'}
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-charcoal-900">
              {formatINR(activitiesCost)}
            </span>
          </div>
        </div>
      </div>

      {/* Audit Note */}
      <div className="mt-4 pt-3 border-t border-sand-100 flex items-start gap-2 text-[11px] text-charcoal-500 leading-snug">
        <Info className="w-3.5 h-3.5 text-charcoal-400 shrink-0 mt-0.5" />
        <span>
          {calculation.isVerified === false
            ? 'Figures represent standardized baseline estimates for unverified locations. Verified regional tariffs and inter-city transport are not included.'
            : 'Figures represent verified baseline estimates for the selected travel style. Inter-city flights/trains are budgeted separately in Phase 2.'}
        </span>
      </div>
    </div>
  );
}
