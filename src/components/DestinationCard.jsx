import React, { useState } from 'react';
import { MapPin, Check, Calendar, ArrowRight, Tag } from 'lucide-react';

export default function DestinationCard({
  destination,
  isSelected,
  onSelect,
  variant = 'standard' // 'standard' or 'compact'
}) {
  const [imgSrc, setImgSrc] = useState(destination.image);
  const [hasError, setHasError] = useState(false);

  const handleImageError = () => {
    if (!hasError && destination.fallbackImage) {
      setImgSrc(destination.fallbackImage);
      setHasError(true);
    }
  };

  return (
    <div
      className={`group relative flex flex-col rounded-xl overflow-hidden transition-all duration-200 border bg-canvas-card ${
        isSelected
          ? 'border-forest-700 shadow-card ring-2 ring-forest-700/20'
          : 'border-sand-200/90 hover:border-sand-300 hover:shadow-card'
      }`}
    >
      {/* Destination Image */}
      <div className="relative aspect-[16/10] overflow-hidden bg-sand-200">
        <img
          src={imgSrc}
          alt={`${destination.name}, ${destination.state}`}
          onError={handleImageError}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.03]"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900/70 via-charcoal-900/20 to-transparent" />
        
        {/* Selected Badge */}
        {isSelected && (
          <div className="absolute top-3 right-3 bg-forest-900/95 text-canvas text-xs font-semibold px-2.5 py-1 rounded-md flex items-center gap-1.5 shadow-subtle border border-forest-600/30">
            <Check className="w-3.5 h-3.5 text-forest-300" strokeWidth={2.5} />
            <span>Selected</span>
          </div>
        )}

        {/* State Tag */}
        <div className="absolute bottom-3 left-3 flex items-center gap-1.5 text-xs text-white/95 font-medium bg-charcoal-900/60 backdrop-blur-sm px-2.5 py-1 rounded-md">
          <MapPin className="w-3 h-3 text-sand-200" />
          <span>{destination.state}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-baseline justify-between gap-2 mb-1.5">
            <h3 className="font-serif text-xl font-bold text-charcoal-900 tracking-tight">
              {destination.name}
            </h3>
            <span className="text-[11px] font-sans text-charcoal-500 font-medium">
              Best: {destination.bestTimeToVisit}
            </span>
          </div>

          <p className="text-xs text-forest-800 font-medium mb-2.5 line-clamp-1 italic">
            "{destination.tagline}"
          </p>

          <p className="text-xs text-charcoal-600 leading-relaxed mb-4 line-clamp-2">
            {destination.description}
          </p>

          {/* Highlights */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {destination.highlights.slice(0, 3).map((highlight, idx) => (
              <span
                key={idx}
                className="text-[11px] font-medium text-charcoal-600 bg-sand-100 px-2 py-0.5 rounded border border-sand-200/60"
              >
                {highlight}
              </span>
            ))}
          </div>
        </div>

        {/* Footer: Indicative Budget & Action */}
        <div className="pt-3.5 border-t border-sand-100 flex items-center justify-between gap-3">
          <div>
            <div className="text-[10px] uppercase font-semibold tracking-wider text-charcoal-400">
              Indicative Range
            </div>
            <div className="text-xs font-bold text-charcoal-800">
              {destination.indicativeRange}
            </div>
          </div>

          <button
            type="button"
            onClick={() => onSelect(destination.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-forest-700 ${
              isSelected
                ? 'bg-forest-100 text-forest-900 border border-forest-300 hover:bg-forest-200/70'
                : 'bg-forest-900 text-canvas hover:bg-forest-800 shadow-subtle'
            }`}
            aria-pressed={isSelected}
            aria-label={isSelected ? `Currently planning trip to ${destination.name}` : `Plan this trip to ${destination.name}`}
          >
            {isSelected ? (
              <>
                <Check className="w-3.5 h-3.5 text-forest-700" />
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
}
