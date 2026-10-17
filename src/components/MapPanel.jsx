import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  MapPin, 
  Navigation, 
  Clock, 
  Info, 
  ShieldCheck, 
  AlertCircle, 
  Footprints, 
  Car, 
  Compass,
  ArrowRight,
  Route as RouteIcon
} from 'lucide-react';

export default function MapPanel({
  currentDay,
  mapCenter,
  destination,
  totalRouteDistanceKm,
  isVerified = true
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Extract stops for current day
  const morning = currentDay?.morning;
  const afternoon = currentDay?.afternoon;
  const evening = currentDay?.evening;
  const routeSegments = currentDay?.routeSegments || [];
  const dayRouteDistanceKm = currentDay?.dayRouteDistanceKm;
  const hasRoadRoutes = currentDay?.hasRoadRoutes || routeSegments.some(s => s.routeType === 'road' || s.geometrySource === 'osrm_road');

  const stops = [
    { slot: 'morning', label: '1 • Morning', data: morning, color: '#b45309', bgClass: 'bg-amber-600' },
    { slot: 'afternoon', label: '2 • Afternoon', data: afternoon, color: '#15803d', bgClass: 'bg-emerald-600' },
    { slot: 'evening', label: '3 • Evening', data: evening, color: '#4338ca', bgClass: 'bg-indigo-600' },
  ].filter(s => Boolean(s.data));

  // Find all valid coordinates among current day stops
  const stopsWithCoords = stops.filter(s => {
    const c = s.data?.coordinates;
    return c && typeof c.lat === 'number' && typeof c.lng === 'number';
  });

  const hasAnyCoords = stopsWithCoords.length > 0 || (mapCenter && typeof mapCenter.lat === 'number');

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Clean up previous instance if exists
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    if (!hasAnyCoords) return;

    // Determine initial center and zoom
    let defaultLat = 20.5937; // Center of India fallback
    let defaultLng = 78.9629;
    let defaultZoom = 12;

    if (stopsWithCoords.length > 0) {
      defaultLat = stopsWithCoords[0].data.coordinates.lat;
      defaultLng = stopsWithCoords[0].data.coordinates.lng;
    } else if (mapCenter && typeof mapCenter.lat === 'number') {
      defaultLat = mapCenter.lat;
      defaultLng = mapCenter.lng;
    }

    // Initialize Leaflet map
    const map = L.map(mapContainerRef.current, {
      center: [defaultLat, defaultLng],
      zoom: defaultZoom,
      zoomControl: true,
      scrollWheelZoom: false, // Prevent accidental scrolling when browsing page
    });

    mapInstanceRef.current = map;

    // OpenStreetMap tile layer with required attribution
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
      maxZoom: 18,
    }).addTo(map);

    const latLngBounds = [];

    // Add markers for stops with verified coordinates
    stopsWithCoords.forEach((stop, idx) => {
      const coord = stop.data.coordinates;
      const latLng = [coord.lat, coord.lng];
      latLngBounds.push(latLng);

      // Custom HTML Pin Icon
      const pinHtml = `
        <div style="
          background-color: ${stop.color};
          color: white;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 13px;
          border: 2px solid white;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          cursor: pointer;
        ">
          ${idx + 1}
        </div>
      `;

      const customIcon = L.divIcon({
        html: pinHtml,
        className: 'custom-map-pin',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -16]
      });

      const precisionLabel = coord.precision === 'verified_attraction'
        ? 'Verified Landmark'
        : coord.precision === 'city_center'
        ? 'Municipal Center'
        : 'Approximate Location';

      const bookingLinkHtml = stop.data.bookingResource
        ? `<div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #e2e8f0;">
             <a href="${stop.data.bookingResource.url}" target="_blank" rel="noopener noreferrer" style="color: #047857; text-decoration: underline; font-weight: bold; font-size: 11px; display: inline-flex; align-items: center; gap: 3px;">
               🎟️ ${stop.data.bookingResource.label || 'Official Portal ↗'}
             </a>
           </div>`
        : `<div style="margin-top: 5px; color: #64748b; font-size: 10px;">
             ${stop.data.cost === 0 ? '✓ Free admission • No booking needed' : '• On-site admission / Walk-in'}
           </div>`;

      const popupContent = `
        <div style="font-family: inherit; font-size: 12px; line-height: 1.4; max-width: 230px;">
          <div style="font-size: 10px; font-weight: bold; text-transform: uppercase; color: ${stop.color}; margin-bottom: 2px;">
            ${stop.label}
          </div>
          <div style="font-weight: bold; font-size: 13px; color: #1e293b; margin-bottom: 4px;">
            ${stop.data.title}
          </div>
          <div style="color: #64748b; font-size: 11px; margin-bottom: 6px;">
            📍 ${stop.data.location || destination?.name || ''}
          </div>
          <div style="display: inline-block; background: #f1f5f9; color: #334155; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">
            ✓ ${precisionLabel}
          </div>
          ${bookingLinkHtml}
        </div>
      `;

      L.marker(latLng, { icon: customIcon })
        .addTo(map)
        .bindPopup(popupContent);
    });

    // If no attraction coords but map center is available, place a municipal center marker
    if (stopsWithCoords.length === 0 && mapCenter && typeof mapCenter.lat === 'number') {
      const cLatLng = [mapCenter.lat, mapCenter.lng];
      latLngBounds.push(cLatLng);

      const centerIcon = L.divIcon({
        html: `
          <div style="
            background-color: #0f766e;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ">📍</div>
        `,
        className: 'custom-center-pin',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -18]
      });

      L.marker(cLatLng, { icon: centerIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
            <div style="font-weight: bold; color: #0f766e;">${destination?.name || 'Destination'}</div>
            <div style="color: #64748b; font-size: 11px;">Municipal Center Coordinates</div>
            <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Specific landmark coordinates pending verification.</div>
          </div>
        `);
    }

    // Draw route polylines: solid for actual road routes, dashed for approximate circuity estimates
    routeSegments.forEach(segment => {
      if (segment.isRouteCalculated && segment.polyline && segment.polyline.length >= 2) {
        const polylineLatLngs = segment.polyline.map(p => [p[0], p[1]]);
        polylineLatLngs.forEach(pt => latLngBounds.push(pt));

        const isRoadRoute = segment.routeType === 'road' || segment.geometrySource === 'osrm_road';
        const modeLabel = segment.transitMode === 'walking' 
          ? 'Walking' 
          : segment.transitMode === 'auto_rickshaw' 
          ? 'Auto-rickshaw' 
          : 'Taxi / Cab';

        // Road route: solid emerald line; Circuity estimate: dashed amber line
        const line = L.polyline(polylineLatLngs, {
          color: isRoadRoute ? '#059669' : '#d97706',
          weight: isRoadRoute ? 4.5 : 3.5,
          opacity: isRoadRoute ? 0.85 : 0.70,
          dashArray: isRoadRoute ? null : '6, 8',
          lineCap: 'round',
          lineJoin: 'round'
        }).addTo(map);

        const tooltipSource = isRoadRoute
          ? '🛣️ OSRM Road Route (Static Network)'
          : '📐 Circuity Estimate (1.30× Great-Circle)';
        const trafficDisclaimer = isRoadRoute
          ? 'Live dynamic traffic congestion not included'
          : 'Approximate projection; not an actual road path';

        line.bindTooltip(`
          <div style="font-size: 11px; line-height: 1.3;">
            <strong>${segment.fromSlot} → ${segment.toSlot}</strong><br/>
            ${tooltipSource}<br/>
            ~${segment.distanceKm} km • ~${segment.durationMinutes} min via ${modeLabel}<br/>
            <span style="color: #64748b; font-size: 10px;">${trafficDisclaimer}</span>
          </div>
        `, { sticky: true });
      }
    });

    // Fit map bounds to encompass all pins and route paths
    if (latLngBounds.length > 1) {
      map.fitBounds(latLngBounds, { padding: [45, 45], maxZoom: 14 });
    } else if (latLngBounds.length === 1) {
      map.setView(latLngBounds[0], 13);
    }

    // Ensure map renders cleanly within dynamic containers
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [currentDay?.dayNumber, mapCenter, destination?.id]);

  // Transit mode icon helper
  const getTransitIcon = (mode) => {
    switch (mode) {
      case 'walking':
        return <Footprints className="w-3.5 h-3.5 text-amber-700" />;
      case 'auto_rickshaw':
        return <Compass className="w-3.5 h-3.5 text-emerald-700" />;
      case 'taxi':
      default:
        return <Car className="w-3.5 h-3.5 text-indigo-700" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Map Header Card */}
      <div className="bg-canvas-card border border-sand-200/90 rounded-2xl p-5 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-sand-100 pb-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-forest-900 text-canvas flex items-center justify-center shadow-subtle shrink-0">
              <Navigation className="w-4 h-4 text-emerald-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-base sm:text-lg font-bold text-charcoal-900">
                  Day {currentDay?.dayNumber} Route Map & Transit
                </h3>
                {dayRouteDistanceKm !== null && dayRouteDistanceKm !== undefined && (
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                    ~{dayRouteDistanceKm} km today
                  </span>
                )}
              </div>
              <p className="text-xs text-charcoal-500">
                OpenStreetMap interactive layout • {hasRoadRoutes ? 'OSRM road network' : 'Municipal gazetteer & circuity estimates'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto text-xs">
            {hasRoadRoutes ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-semibold bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-subtle">
                <RouteIcon className="w-3.5 h-3.5 text-emerald-700" />
                <span>OSRM Road Routed</span>
              </span>
            ) : stopsWithCoords.length > 0 ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-semibold bg-amber-100 text-amber-900 border border-amber-300 shadow-subtle">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-700" />
                <span>Circuity Fallback</span>
              </span>
            ) : mapCenter ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold bg-sand-100 text-charcoal-700 border border-sand-200">
                <MapPin className="w-3.5 h-3.5 text-charcoal-600" />
                <span>Municipal Center Only</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
                <span>Coordinates Unavailable</span>
              </span>
            )}
          </div>
        </div>

        {/* Leaflet Map Canvas */}
        {hasAnyCoords ? (
          <div className="relative rounded-xl overflow-hidden border border-sand-300/80 shadow-inner bg-sand-100">
            <div 
              ref={mapContainerRef} 
              style={{ height: '360px', width: '100%', zIndex: 10 }}
              aria-label={`Interactive map of Day ${currentDay?.dayNumber} itinerary in ${destination?.name || 'destination'}`}
            />
            {/* Map corner legend badge */}
            <div className="absolute bottom-2 right-2 z-20 bg-canvas/90 backdrop-blur-sm border border-sand-200 px-2.5 py-1.5 rounded-lg text-[10px] text-charcoal-600 shadow-subtle flex items-center gap-3">
              <span className="flex items-center gap-1 font-medium">
                <span className="w-2 h-2 rounded-full bg-amber-600 inline-block"></span> 1 Morning
              </span>
              <span className="flex items-center gap-1 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block"></span> 2 Afternoon
              </span>
              <span className="flex items-center gap-1 font-medium">
                <span className="w-2 h-2 rounded-full bg-indigo-600 inline-block"></span> 3 Evening
              </span>
              {hasRoadRoutes ? (
                <span className="flex items-center gap-1 font-semibold text-emerald-800 border-l border-sand-200 pl-2">
                  <span className="w-3 h-0.5 bg-emerald-600 inline-block"></span> Road Path
                </span>
              ) : (
                <span className="flex items-center gap-1 font-semibold text-amber-800 border-l border-sand-200 pl-2">
                  <span className="w-3 h-0.5 border-t border-dashed border-amber-600 inline-block"></span> Est. Path
                </span>
              )}
            </div>
          </div>
        ) : (
          /* Graceful Fallback Card for Unverified Locations */
          <div className="bg-sand-50/70 border border-dashed border-sand-300 rounded-xl p-6 text-center">
            <div className="w-10 h-10 rounded-full bg-sand-200 text-charcoal-500 flex items-center justify-center mx-auto mb-3">
              <Compass className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-charcoal-800 mb-1">
              Geographic Coordinates Unavailable
            </h4>
            <p className="text-xs text-charcoal-600 max-w-md mx-auto leading-relaxed">
              This destination was manually entered or verified geographic coordinates are not yet on file in our municipal gazetteer.
              In accordance with TripPilot principles, coordinates and road routes are never fabricated.
            </p>
          </div>
        )}

        {/* Route Segments & Transit Estimates */}
        {routeSegments.length > 0 && (
          <div className="mt-4 pt-3 border-t border-sand-100">
            <div className="text-[11px] font-bold uppercase tracking-wider text-charcoal-700 mb-2 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <span>Inter-Activity Transit Segments</span>
                <span className="text-[10px] lowercase font-normal text-charcoal-500">
                  ({hasRoadRoutes ? 'OSRM road calculations' : 'circuity-adjusted estimates'})
                </span>
              </div>
              <span className="text-[10px] font-medium text-charcoal-500">
                {hasRoadRoutes ? 'Road Routing Active' : 'Fallback Mode'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {routeSegments.map((seg, idx) => {
                const modeLabel = seg.transitMode === 'walking' 
                  ? 'Walking' 
                  : seg.transitMode === 'auto_rickshaw' 
                  ? 'Auto-rickshaw' 
                  : 'Taxi / Cab';
                const isRoad = seg.routeType === 'road' || seg.geometrySource === 'osrm_road';

                return (
                  <div 
                    key={idx} 
                    className="p-3 rounded-xl border border-sand-200/80 bg-canvas/80 text-xs flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-1 mb-1.5">
                        <span className="font-bold text-charcoal-900 flex items-center gap-1 capitalize">
                          <span>{seg.fromSlot}</span>
                          <ArrowRight className="w-3 h-3 text-sand-400" />
                          <span>{seg.toSlot}</span>
                        </span>
                        {seg.isRouteCalculated ? (
                          <div className="flex items-center gap-1.5">
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-forest-50 text-forest-800 border border-forest-200">
                              {getTransitIcon(seg.transitMode)}
                              <span>{modeLabel}</span>
                            </span>
                            <span className={`text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded ${
                              isRoad
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                                : 'bg-amber-100 text-amber-800 border border-amber-200'
                            }`}>
                              {isRoad ? 'OSRM Road' : 'Circuity Est.'}
                            </span>
                          </div>
                        ) : (
                          <span className="text-[10px] text-charcoal-400 font-medium">
                            Transit pending
                          </span>
                        )}
                      </div>

                      <div className="text-charcoal-600 text-[11px] line-clamp-1 mb-1">
                        From: <span className="text-charcoal-800">{seg.fromTitle}</span>
                      </div>
                      <div className="text-charcoal-600 text-[11px] line-clamp-1 mb-2">
                        To: <span className="text-charcoal-800">{seg.toTitle}</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-sand-100 flex items-center justify-between text-[11px]">
                      {seg.isRouteCalculated ? (
                        <>
                          <span className="text-charcoal-600 font-medium">
                            {isRoad ? 'Road Dist:' : 'Est. Dist:'} <strong className="text-charcoal-900">~{seg.distanceKm} km</strong>
                          </span>
                          <span className="text-charcoal-600 font-medium">
                            {isRoad ? 'Road Time:' : 'Est. Time:'} <strong className="text-charcoal-900">~{seg.durationMinutes} min</strong>
                          </span>
                        </>
                      ) : (
                        <span className="text-charcoal-500 italic text-[10px]">
                          Specific route distance uncalculated for unverified stops.
                        </span>
                      )}
                    </div>

                    {seg.trafficNotice && (
                      <div className="mt-1.5 text-[10px] text-charcoal-500 leading-tight">
                        {seg.trafficNotice}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Practical Transit Note & Honest Disclaimer */}
            <div className="mt-3 p-2.5 bg-sand-50/80 border border-sand-200/60 rounded-xl flex items-start gap-2 text-[11px] text-charcoal-600 leading-snug">
              <Info className="w-3.5 h-3.5 text-forest-700 shrink-0 mt-0.5" />
              <span>
                <strong>Routing & Traffic Transparency:</strong> {hasRoadRoutes ? (
                  <>Road distances and polyline geometries are computed using OpenStreetMap road networks via OSRM. Calculations reflect standard free-flow speeds and <strong>do not include dynamic real-time traffic congestion</strong>. Unverified routes or connection outages fall back gracefully to empirical circuity estimates without disrupting itinerary planning.</>
                ) : (
                  <>Route lines and transit durations are empirical circuity estimates (<code>geometrySource: haversine_circuity</code>) calibrated for Indian urban transit speeds. They provide visual context and are not real-time turn-by-turn road navigation or GPS telemetry.</>
                )}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
