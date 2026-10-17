"""Configurable road routing provider module for TripPilot Phase 6.3.

Integrates with the OSRM (Open Source Routing Machine) public demo service
with in-memory caching, strict timeouts, error handling, coordinate validation,
and seamless fallback hooks.

IMPORTANT: The OSRM public demo service provides static road network routing
without real-time dynamic traffic or live congestion telemetry. Road-routed
results are explicitly tagged with geometrySource="osrm_road" and routeType="road".
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple, List
import httpx

logger = logging.getLogger(__name__)


class BaseRoutingProvider(ABC):
    """Abstract interface for pluggable road routing providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name identifier of the provider."""
        pass

    @abstractmethod
    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculates turn-by-turn road route between two points.
        Returns dict with distance_km, duration_minutes, polyline, and metadata,
        or None if routing fails or coordinates are invalid.
        """
        pass


class OSRMRoutingProvider(BaseRoutingProvider):
    """
    Road routing implementation backed by the OSRM public demo API.
    Configurable via environment variables:
      - ROUTING_PROVIDER_ENABLED: 'true' (default) / 'false'
      - OSRM_BASE_URL: 'https://router.project-osrm.org' (default)
      - OSRM_TIMEOUT_SECONDS: '2.5' (default)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        enabled: Optional[bool] = None,
    ):
        self._enabled = (
            enabled
            if enabled is not None
            else os.getenv("ROUTING_PROVIDER_ENABLED", "true").lower() in ("true", "1", "yes")
        )
        self._base_url = (
            base_url
            or os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
        ).rstrip("/")
        self._timeout = (
            timeout_seconds
            if timeout_seconds is not None
            else float(os.getenv("OSRM_TIMEOUT_SECONDS", "2.5"))
        )
        # In-memory coordinate cache to respect public demo rate limits and optimize repeated queries
        self._cache: Dict[Tuple[float, float, float, float], Dict[str, Any]] = {}

    @property
    def name(self) -> str:
        return "osrm"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def clear_cache(self) -> None:
        """Clears the in-memory route cache."""
        self._cache.clear()

    @staticmethod
    def _is_valid_coord(lat: Optional[float], lng: Optional[float]) -> bool:
        """Validates that latitude and longitude are numbers within valid geographical ranges."""
        if lat is None or lng is None:
            return False
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            return False
        return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Queries OSRM driving route between origin and destination.
        Returns road distance, duration, and GeoJSON polyline as [lat, lng] pairs.
        Returns None if disabled, invalid coords, timed out, or provider error.
        """
        if not self._enabled:
            return None

        # Validate coordinates before any networking
        if not self._is_valid_coord(origin_lat, origin_lng) or not self._is_valid_coord(dest_lat, dest_lng):
            return None

        # Check cache (rounded to 5 decimal places ~1 meter precision)
        cache_key = (
            round(float(origin_lat), 5),
            round(float(origin_lng), 5),
            round(float(dest_lat), 5),
            round(float(dest_lng), 5),
        )
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Handle zero-distance edge case
        if cache_key[0] == cache_key[2] and cache_key[1] == cache_key[3]:
            zero_route = {
                "distance_km": 0.0,
                "duration_minutes": 0,
                "polyline": [[cache_key[0], cache_key[1]], [cache_key[2], cache_key[3]]],
                "provider": self.name,
                "route_type": "road",
                "geometry_source": "osrm_road",
                "traffic_notice": "Identical origin and destination coordinates."
            }
            self._cache[cache_key] = zero_route
            return zero_route

        # OSRM expects: {lng1},{lat1};{lng2},{lat2}
        url = (
            f"{self._base_url}/route/v1/driving/"
            f"{origin_lng:.6f},{origin_lat:.6f};{dest_lng:.6f},{dest_lat:.6f}"
            f"?overview=full&geometries=geojson"
        )
        headers = {
            "User-Agent": "TripPilot/1.0 (Hackathon Educational Demo; Python/FastAPI)",
            "Accept": "application/json"
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    logger.warning(
                        "OSRM returned status %s for points (%s,%s)->(%s,%s)",
                        response.status_code, origin_lat, origin_lng, dest_lat, dest_lng
                    )
                    return None

                data = response.json()
                if data.get("code") != "Ok" or not data.get("routes"):
                    logger.warning("OSRM returned non-Ok code: %s", data.get("code"))
                    return None

                primary_route = data["routes"][0]
                distance_meters = float(primary_route.get("distance", 0.0))
                duration_seconds = float(primary_route.get("duration", 0.0))
                raw_coords = primary_route.get("geometry", {}).get("coordinates", [])

                # OSRM GeoJSON coords are [lng, lat]; convert to Leaflet standard [lat, lng]
                polyline: List[List[float]] = []
                for pt in raw_coords:
                    if len(pt) >= 2:
                        polyline.append([round(float(pt[1]), 5), round(float(pt[0]), 5)])

                if not polyline:
                    polyline = [
                        [round(origin_lat, 5), round(origin_lng, 5)],
                        [round(dest_lat, 5), round(dest_lng, 5)]
                    ]

                result = {
                    "distance_km": round(distance_meters / 1000.0, 1),
                    "duration_minutes": max(1, round(duration_seconds / 60.0)),
                    "polyline": polyline,
                    "provider": self.name,
                    "route_type": "road",
                    "geometry_source": "osrm_road",
                    "traffic_notice": "Static road network calculation (OSRM). Real-time traffic congestion not included."
                }

                # Store in cache
                self._cache[cache_key] = result
                return result

        except httpx.TimeoutException:
            logger.warning("OSRM request timed out after %s seconds", self._timeout)
            return None
        except Exception as e:
            logger.warning("OSRM request failed: %s (%s)", type(e).__name__, str(e))
            return None


# Global singleton provider instance
_DEFAULT_ROUTING_PROVIDER: Optional[BaseRoutingProvider] = None


def get_routing_provider() -> BaseRoutingProvider:
    """Returns the globally configured routing provider instance."""
    global _DEFAULT_ROUTING_PROVIDER
    if _DEFAULT_ROUTING_PROVIDER is None:
        _DEFAULT_ROUTING_PROVIDER = OSRMRoutingProvider()
    return _DEFAULT_ROUTING_PROVIDER


def set_routing_provider(provider: BaseRoutingProvider) -> None:
    """Allows testing or dependency injection to set a custom routing provider."""
    global _DEFAULT_ROUTING_PROVIDER
    _DEFAULT_ROUTING_PROVIDER = provider
