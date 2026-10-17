import React, { useState } from 'react';
import { Compass, Menu, X, Bookmark, MapPin, Sparkles } from 'lucide-react';

export default function Header({ activeTab, onTabChange, savedCount = 0 }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'plan', label: 'Plan a Trip', icon: Sparkles },
    { id: 'explore', label: 'Explore', icon: MapPin },
    { id: 'saved', label: 'Saved Trips', icon: Bookmark, badge: savedCount > 0 ? savedCount : null },
  ];

  const handleNavClick = (tabId) => {
    onTabChange(tabId);
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 bg-canvas/95 backdrop-blur-sm border-b border-sand-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand Wordmark */}
          <button
            onClick={() => handleNavClick('plan')}
            className="flex items-center gap-3 group focus-visible:ring-2 focus-visible:ring-forest-700 rounded-md py-1 pr-2 text-left"
            aria-label="TripPilot Home"
          >
            <div className="w-10 h-10 rounded-lg bg-forest-900 text-canvas flex items-center justify-center shadow-subtle group-hover:bg-forest-800 transition-colors">
              <Compass className="w-5 h-5 text-forest-200" strokeWidth={2.2} />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-2xl font-semibold tracking-tight text-forest-950">
                  TripPilot
                </span>
                <span className="text-[10px] font-sans font-medium uppercase tracking-wider bg-forest-100 text-forest-800 px-1.5 py-0.5 rounded">
                  AI Travel Planner
                </span>
              </div>
              <p className="text-xs text-charcoal-500 font-sans tracking-normal hidden sm:block">
                Your personalized journey, planned intelligently
              </p>
            </div>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`relative px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 focus-visible:ring-2 focus-visible:ring-forest-700 ${
                    isActive
                      ? 'text-forest-900 bg-sand-100/80 font-semibold'
                      : 'text-charcoal-600 hover:text-forest-900 hover:bg-sand-100/50'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-forest-800' : 'text-charcoal-400'}`} />
                  <span>{item.label}</span>
                  {item.badge !== null && (
                    <span className="ml-1 text-[11px] font-semibold bg-forest-800 text-canvas px-1.5 py-0.2 rounded-full">
                      {item.badge}
                    </span>
                  )}
                  {isActive && (
                    <span className="absolute bottom-0 left-4 right-4 h-0.5 bg-forest-800 rounded-full" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right utility: Currency & compact user indicator */}
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-medium text-charcoal-600 bg-sand-100/70 border border-sand-200 px-2.5 py-1.5 rounded-md">
              <span className="w-2 h-2 rounded-full bg-forest-600" />
              <span>INR (₹)</span>
            </div>
            <div 
              className="flex items-center gap-2 text-xs font-medium text-charcoal-700 border border-sand-200 bg-canvas-card px-2.5 py-1.5 rounded-md"
              title="Guest planning session active"
            >
              <div className="w-5 h-5 rounded-full bg-forest-900 text-canvas text-[11px] font-semibold flex items-center justify-center">
                TP
              </div>
              <span>Guest Planner</span>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg text-charcoal-700 hover:text-forest-900 hover:bg-sand-100 focus-visible:ring-2 focus-visible:ring-forest-700"
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open navigation menu'}
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-sand-200 bg-canvas px-4 pt-3 pb-6 space-y-2 shadow-elevated">
          <div className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-md text-base font-medium transition-colors ${
                    isActive
                      ? 'bg-forest-900 text-canvas font-semibold'
                      : 'text-charcoal-700 hover:bg-sand-100 hover:text-forest-900'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${isActive ? 'text-forest-200' : 'text-charcoal-500'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== null && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      isActive ? 'bg-forest-800 text-white' : 'bg-sand-200 text-charcoal-700'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="pt-3 border-t border-sand-200 flex items-center justify-between text-xs text-charcoal-600 px-1">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-forest-600" />
              Currency: INR (₹)
            </span>
            <span className="text-charcoal-500">AI Travel Planner</span>
          </div>
        </div>
      )}
    </header>
  );
}
