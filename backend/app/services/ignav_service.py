"""
Airfare Intelligence Platform — Ignav Live Data Service
Phase 7: Ignav Integration (replaces Amadeus as REAL_API_FARES provider)

Modular service for querying the Ignav Flight Prices API.

API Reference:
  POST https://ignav.com/api/fares/one-way
  Auth: X-Api-Key header (server-side only — NEVER exposed in frontend JS)
  Docs: https://ignav.com/docs/one-way

CRITICAL RULES:
  - API key ONLY from environment variable IGNAV_API_KEY
  - Never hardcoded, never logged
  - If key missing → graceful degradation, no crash
  - Never fabricate a live API response
  - All live data tagged source="ignav", source_provenance="REAL_API"
  - Fields not provided by Ignav stored as NULL (no invention)
"""

import logging
import os
from datetime import date, datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

IGNAV_BASE_URL = "https://ignav.com/api"
IGNAV_ONE_WAY_URL = f"{IGNAV_BASE_URL}/fares/one-way"
IGNAV_BOOKING_LINKS_URL = f"{IGNAV_BASE_URL}/fares/booking-links"

# Cabin class normalisation for Ignav (lowercase strings)
# Ignav accepts: "economy", "premium_economy", "business", "first"
CABIN_MAP = {
    "economy": "economy",
    "Economy": "economy",
    "ECONOMY": "economy",
    "premium economy": "premium_economy",
    "Premium Economy": "premium_economy",
    "PREMIUM_ECONOMY": "premium_economy",
    "premium_economy": "premium_economy",
    "business": "business",
    "Business": "business",
    "BUSINESS": "business",
    "first": "first",
    "First": "first",
    "FIRST": "first",
}

# Display-name normalisation for cabin class stored in DB (Title-cased)
CABIN_DISPLAY_MAP = {
    "economy": "Economy",
    "premium_economy": "Premium Economy",
    "business": "Business",
    "first": "First",
}


class IgnavService:
    """
    Service for querying the Ignav Flight Prices API.

    Usage:
        svc = IgnavService()
        if svc.is_available:
            fares = svc.search_flights(
                origin="DEL",
                destination="BOM",
                departure_date=date.today(),
            )

    All results are tagged:
        source="ignav"
        source_provenance="REAL_API"

    Fields not supplied by Ignav are stored as NULL.
    This service NEVER fabricates prices, taxes, or availability.
    """

    def __init__(self):
        self._api_key: str = os.getenv("IGNAV_API_KEY", "").strip()
        if not self._api_key:
            logger.warning(
                "Ignav API key not set. "
                "Set IGNAV_API_KEY in .env to enable live data. "
                "App will run in historical/demo mode without it."
            )

    @property
    def is_available(self) -> bool:
        """Returns True if IGNAV_API_KEY is configured."""
        return bool(self._api_key)

    def _headers(self) -> dict:
        """Construct authenticated request headers. Key stays server-side."""
        return {
            "X-Api-Key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        adults: int = 1,
        cabin_class: str = "Economy",
        max_stops: Optional[int] = None,
        market: str = "IN",
        max_results: Optional[int] = None,
    ) -> list[dict]:
        """
        Search for one-way flights using the Ignav API.

        Returns a list of normalised fare observations conforming to the
        platform's airfare schema. Returns an empty list (not an exception)
        when the API is unavailable or returns no itineraries.

        NEVER fabricates results.

        Args:
            origin:         IATA departure airport code (e.g. "DEL")
            destination:    IATA arrival airport code (e.g. "BOM")
            departure_date: Date of travel
            adults:         Number of adult passengers (default 1)
            cabin_class:    "Economy" / "Business" / "First" / "Premium Economy"
            max_stops:      Maximum stops (0=nonstop, 1, 2; None=any)
            market:         2-letter country code for pricing locale (default "IN")
            max_results:    Ignored (Ignav controls result count server-side)
        """
        if not self.is_available:
            logger.warning("Ignav search called but IGNAV_API_KEY not configured")
            return []

        # Build request payload — only send fields Ignav actually supports
        payload: dict = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date.isoformat(),
            "adults": adults,
            "cabin_class": CABIN_MAP.get(cabin_class, "economy"),
            "market": market,
        }
        if max_stops is not None:
            payload["max_stops"] = max_stops

        try:
            response = httpx.post(
                IGNAV_ONE_WAY_URL,
                json=payload,
                headers=self._headers(),
                timeout=20.0,
            )
            response.raise_for_status()
            raw_data = response.json()

            itineraries = raw_data.get("itineraries", [])
            logger.info(
                f"Ignav search {origin}→{destination} on {departure_date}: "
                f"{len(itineraries)} itineraries returned"
            )
            return self._normalize_response(
                raw_data, origin, destination, departure_date, cabin_class
            )

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            body_preview = e.response.text[:300]
            if status == 401 or status == 403:
                logger.error(
                    f"Ignav API authentication failed (HTTP {status}). "
                    f"Check IGNAV_API_KEY in .env. Response: {body_preview}"
                )
            elif status == 422:
                logger.error(
                    f"Ignav API rejected request (HTTP {status} — unsupported route or params). "
                    f"Response: {body_preview}"
                )
            else:
                logger.error(
                    f"Ignav API HTTP error {status}: {body_preview}"
                )
            return []

        except httpx.TimeoutException:
            logger.error(
                f"Ignav API request timed out for {origin}→{destination} on {departure_date}"
            )
            return []

        except httpx.RequestError as e:
            logger.error(f"Ignav API network error: {e}")
            return []

        except Exception as e:
            logger.error(f"Ignav search failed unexpectedly: {e}")
            return []

    def _normalize_response(
        self,
        raw_data: dict,
        origin: str,
        destination: str,
        departure_date: date,
        cabin_class: str,
    ) -> list[dict]:
        """
        Normalise Ignav API response into the platform's common airfare schema.

        Field mapping (only genuine Ignav fields — no fabrication):
          price.amount              → fare (total_fare)
          price.currency            → currency
          price.status              → (stored in raw provenance only)
          outbound.carrier          → airline
          segment.marketing_carrier_code → airline_code (part of flight_number)
          segment.flight_number     → flight_number
          segment.departure_time_local → departure_time (HH:MM)
          segment.arrival_time_local   → arrival_time (HH:MM)
          outbound.duration_minutes → duration_minutes
          cabin_class               → cabin_class
          ignav_id                  → provider_fare_id (stored in flight_number field)

        Fields Ignav does NOT provide → stored as NULL:
          base_fare, taxes, airport_fees, service_charge, availability

        All results are tagged:
          source="ignav"
          source_provenance="REAL_API"
        """
        results = []
        collected_at = datetime.utcnow()
        booking_date = collected_at.date()

        itineraries = raw_data.get("itineraries", [])
        if not itineraries:
            logger.info(
                f"Ignav returned 0 itineraries for {origin}→{destination} "
                f"on {departure_date} — route may be unsupported or no flights available"
            )
            return []

        for itinerary in itineraries:
            try:
                # ── Price ───────────────────────────────────────────────────
                price_info = itinerary.get("price", {})
                if not price_info:
                    logger.debug("Itinerary missing price block — skipping")
                    continue

                amount = price_info.get("amount")
                if amount is None or amount <= 0:
                    logger.debug(f"Itinerary has invalid fare amount {amount!r} — skipping")
                    continue

                total_fare = float(amount)
                currency = price_info.get("currency", "INR") or "INR"
                # price.status is Ignav metadata ("verified"/"unverified") — preserved in note only
                price_status = price_info.get("status")  # noqa: F841 (available if needed)

                # ── Outbound leg ────────────────────────────────────────────
                outbound = itinerary.get("outbound", {})
                if not outbound:
                    logger.debug("Itinerary missing outbound leg — skipping")
                    continue

                outbound_duration = outbound.get("duration_minutes")
                duration_minutes = int(outbound_duration) if outbound_duration is not None else None
                # outbound.carrier is the display name of the operating carrier for the leg
                leg_carrier = outbound.get("carrier") or ""

                segments = outbound.get("segments", [])
                if not segments:
                    logger.debug("Outbound leg has no segments — skipping")
                    continue

                first_seg = segments[0]
                last_seg = segments[-1]
                stops = len(segments) - 1

                # ── Segment fields ──────────────────────────────────────────
                # marketing_carrier_code: 2-letter IATA airline code
                carrier_code = first_seg.get("marketing_carrier_code") or ""
                # flight_number: the actual flight number string
                seg_flight_number = first_seg.get("flight_number")
                # operating_carrier_name: full name of operator
                operating_name = first_seg.get("operating_carrier_name") or ""

                # Use outbound.carrier as airline display name; fall back to
                # operating_carrier_name from first segment, then carrier code
                airline_display = leg_carrier or operating_name or carrier_code or "Unknown"

                # Construct composite flight number (e.g. "6E-205")
                if carrier_code and seg_flight_number:
                    flight_number = f"{carrier_code}-{seg_flight_number}"
                elif seg_flight_number:
                    flight_number = str(seg_flight_number)
                else:
                    # Fall back to ignav_id so the booking can be referenced later
                    ignav_id = itinerary.get("ignav_id", "")
                    flight_number = f"IGNAV-{ignav_id[:8]}" if ignav_id else None

                # ── Departure / arrival times ────────────────────────────────
                # departure_time_local: "YYYY-MM-DDTHH:MM:SS"
                dep_local = first_seg.get("departure_time_local", "")
                arr_local = last_seg.get("arrival_time_local", "")
                dep_time = dep_local[11:16] if dep_local and len(dep_local) >= 16 else None
                arr_time = arr_local[11:16] if arr_local and len(arr_local) >= 16 else None

                # ── cabin_class display ──────────────────────────────────────
                ignav_cabin = itinerary.get("cabin_class", "economy")
                cabin_display = CABIN_DISPLAY_MAP.get(
                    ignav_cabin, cabin_class.title() if cabin_class else "Economy"
                )

                # ── ignav_id — preserve for booking-links endpoint ───────────
                ignav_id = itinerary.get("ignav_id")

                results.append({
                    # ── Provenance (CRITICAL — never fabricate or change) ────
                    "source": "ignav",
                    "source_provenance": "REAL_API",

                    # ── Route ────────────────────────────────────────────────
                    "origin": origin.upper(),
                    "destination": destination.upper(),
                    "airline": airline_display,

                    # ── Dates ────────────────────────────────────────────────
                    "travel_date": departure_date,
                    "booking_date": booking_date,

                    # ── Schedule ─────────────────────────────────────────────
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "stops": stops,
                    "duration_minutes": duration_minutes,

                    # ── Fare (what Ignav actually provides) ──────────────────
                    "fare": round(total_fare, 2),
                    "currency": currency,
                    "cabin_class": cabin_display,

                    # ── Fields Ignav does NOT provide → NULL (never invent) ──
                    "base_fare": None,          # Ignav does not break out base fare
                    "taxes": None,              # Ignav does not itemise taxes
                    "airport_fees": None,       # Ignav does not itemise airport fees
                    "service_charge": None,     # Ignav does not itemise service charges
                    "availability": None,       # Ignav does not expose seat availability

                    # ── Flight identifier ────────────────────────────────────
                    "flight_number": flight_number,

                    # ── Derived ──────────────────────────────────────────────
                    "days_left": (departure_date - booking_date).days,
                    "is_demo_anomaly": False,
                    "collected_at": collected_at,

                    # ── Ignav-specific metadata (not in DB schema — logged) ──
                    "_ignav_id": ignav_id,
                    "_price_status": price_status,
                    "_requires_self_transfer": itinerary.get("requires_self_transfer"),
                })

            except Exception as e:
                logger.warning(f"Failed to normalise Ignav itinerary: {e}")
                continue

        logger.info(
            f"Ignav normalised {len(results)}/{len(itineraries)} itineraries "
            f"for {origin}→{destination} on {departure_date}"
        )
        return results

    def get_booking_links(self, ignav_id: str) -> dict:
        """
        Fetch booking links for a previously searched itinerary using its ignav_id.

        Uses: POST https://ignav.com/api/fares/booking-links
        Returns the raw Ignav response dict, or an error dict.

        NEVER fabricates booking URLs — returns only what Ignav provides.
        """
        if not self.is_available:
            return {"error": "IGNAV_API_KEY not configured", "booking_links": []}

        if not ignav_id:
            return {"error": "ignav_id is required", "booking_links": []}

        try:
            response = httpx.post(
                IGNAV_BOOKING_LINKS_URL,
                json={"ignav_id": ignav_id},
                headers=self._headers(),
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Ignav booking-links HTTP error {e.response.status_code}: "
                f"{e.response.text[:200]}"
            )
            return {"error": f"HTTP {e.response.status_code}", "booking_links": []}

        except Exception as e:
            logger.error(f"Ignav booking-links request failed: {e}")
            return {"error": str(e), "booking_links": []}

    def get_status(self) -> dict:
        """Return current Ignav service status (for /live-status endpoint)."""
        if not self.is_available:
            return {
                "source": "ignav",
                "status": "unavailable",
                "message": (
                    "IGNAV_API_KEY not configured. "
                    "Set IGNAV_API_KEY in .env — register at https://ignav.com"
                ),
                "last_fetch": None,
            }

        # Lightweight connectivity test: hit the public health endpoint
        try:
            response = httpx.get(
                f"{IGNAV_BASE_URL}/health",
                timeout=5.0,
            )
            if response.status_code == 200 and response.json().get("ok"):
                return {
                    "source": "ignav",
                    "status": "active",
                    "message": "Ignav API reachable — IGNAV_API_KEY configured",
                    "last_fetch": datetime.utcnow(),
                }
        except Exception:
            pass

        # API reachable but health check inconclusive — key is set so mark as configured
        return {
            "source": "ignav",
            "status": "configured",
            "message": "IGNAV_API_KEY configured — connectivity unverified",
            "last_fetch": None,
        }


# Module-level singleton
_ignav_service: Optional[IgnavService] = None


def get_ignav_service() -> IgnavService:
    """Return the module-level IgnavService singleton."""
    global _ignav_service
    if _ignav_service is None:
        _ignav_service = IgnavService()
    return _ignav_service
