import React from 'react';
import { Compass, ShieldCheck, Heart } from 'lucide-react';

export default function Footer({ onTabChange }) {
  return (
    <footer className="mt-16 border-t border-sand-200 bg-sand-50/60 text-charcoal-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-lg bg-forest-900 text-canvas flex items-center justify-center">
                <Compass className="w-4 h-4 text-forest-200" />
              </div>
              <span className="font-serif text-xl font-bold tracking-tight text-forest-950">
                TripPilot
              </span>
              <span className="text-[10px] font-sans font-medium uppercase tracking-wider bg-forest-100 text-forest-800 px-1.5 py-0.5 rounded">
                Phase 2 Backend
              </span>
            </div>
            <p className="text-xs text-charcoal-600 leading-relaxed max-w-md mb-4">
              An intelligent travel-planning workspace designed to balance personal preferences, local schedules, and strict budget ceilings into coherent, realistic daily itineraries across India.
            </p>
            <div className="flex items-center gap-2 text-[11px] text-charcoal-500 font-medium">
              <ShieldCheck className="w-4 h-4 text-forest-700" />
              <span>Phase 2 FastAPI Backend active. Multi-agent cloud AI integrations arrive in Phase 3.</span>
            </div>
          </div>

          {/* Quick Navigation */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal-800 mb-3">
              Workspace
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button
                  onClick={() => onTabChange('plan')}
                  className="text-charcoal-600 hover:text-forest-900 transition-colors"
                >
                  Plan a Trip
                </button>
              </li>
              <li>
                <button
                  onClick={() => onTabChange('explore')}
                  className="text-charcoal-600 hover:text-forest-900 transition-colors"
                >
                  Explore Destinations
                </button>
              </li>
              <li>
                <button
                  onClick={() => onTabChange('saved')}
                  className="text-charcoal-600 hover:text-forest-900 transition-colors"
                >
                  Saved Trips
                </button>
              </li>
            </ul>
          </div>

          {/* Planned Technology Note */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal-800 mb-3">
              Future Architecture
            </h4>
            <p className="text-xs text-charcoal-500 leading-relaxed mb-2">
              Phase 3 will introduce autonomous multi-agent reasoning via Amazon Bedrock and Strands Decider 2B for real-time schedule negotiation and live pricing adaptation.
            </p>
            <div className="text-[11px] text-charcoal-400">
              Deterministic FastAPI engine in Phase 2.
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-sand-200/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-charcoal-500">
          <p>© {new Date().getFullYear()} TripPilot. Built with React, Vite & Tailwind CSS.</p>
          <p className="flex items-center gap-1">
            Designed for thoughtful travelers
          </p>
        </div>
      </div>
    </footer>
  );
}
