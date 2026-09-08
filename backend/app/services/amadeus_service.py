"""
Airfare Intelligence Platform — Amadeus Live Data Service
Phase 7: Amadeus Integration

Modular service for querying the Amadeus Flight Offers Search API.

CRITICAL RULES:
  - Credentials ONLY from environment variables (AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET)
  - Never hardcoded, never logged
  - If credentials missing → graceful degradation, no crash
  - Never fabricate a live API response
  - All live data tagged source="amadeus" with collected_at timestamp
"""

import logging
import os
from datetime import date, datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

# Cabin class mapping (Amadeus uses uppercase)
CABIN_MAP = {
    "Economy": "ECONOMY",
    "Premium Economy": "PREMIUM_ECONOMY",
    "Business": "BUSINESS",
    "First": "FIRST",
}


class AmadeusService:
    """
    Service for querying the Amadeus Flight Offers API.

    Usage:
        svc = AmadeusService()
        if svc.is_available:
            fares = svc.search_flights(origin="DEL", destination="BOM", departure_date=date.today())
    """

    def __init__(self):
        self._client_id = os.getenv("AMADEUS_CLIENT_ID", "").strip()
        self._client_secret = os.getenv("AMADEUS_CLIENT_SECRET", "").strip()
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        if not self._client_id or not self._client_secret:
            logger.warning(
                "Amadeus credentials not set. "
                "Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env "
                "to enable live data. App will run in historical/demo mode."
            )

    @property
    def is_available(self) -> bool:
        """Returns True if Amadeus credentials are configured."""
        return bool(self._client_id and self._client_secret)

    def _token_is_valid(self) -> bool:
        if not self._access_token or not self._token_expires_at:
            return False
        return datetime.utcnow() < self._token_expires_at

    def _get_access_token(self) -> Optional[str]:
        """Obtain OAuth2 access token from Amadeus."""
        if self._token_is_valid():
            return self._access_token

        try:
            response = httpx.post(
                AMADEUS_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 1799)
            from datetime import timedelta
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 30)
            logger.info("Amadeus access token obtained successfully")
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to obtain Amadeus access token: {e}")
            self._access_token = None
            self._token_expires_at = None
            return None

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        adults: int = 1,
        cabin_class: str = "ECONOMY",
        max_results: int = 20,
    ) -> list[dict]:
        """
        Search for flights using Amadeus Flight Offers API.

        Returns normalized fare observations (list of dicts conforming to airfare schema).
        Returns empty list (not error) if API is unavailable.

        NEVER fabricates results.
        """
        if not self.is_available:
            logger.warning("Amadeus search called but credentials not configured")
            return []

        token = self._get_access_token()
        if not token:
            logger.error("Cannot search: Amadeus token unavailable")
            return []

        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date.isoformat(),
            "adults": adults,
            "travelClass": CABIN_MAP.get(cabin_class, cabin_class.upper()),
            "max": max_results,
            "currencyCode": "INR",
        }

        try:
            response = httpx.get(
                AMADEUS_SEARCH_URL,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15.0,
            )
            response.raise_for_status()
            raw_data = response.json()
            logger.info(
                f"Amadeus search {origin}→{destination} on {departure_date}: "
                f"{len(raw_data.get('data', []))} results"
            )
            return self._normalize_response(
                raw_data, origin, destination, departure_date, cabin_class
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Amadeus API HTTP error: {e.response.status_code} — {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"Amadeus search failed: {e}")
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
        Normalize Amadeus API response to our common airfare schema.
        All results tagged source="amadeus".
        """
        results = []
        collected_at = datetime.utcnow()

        for offer in raw_data.get("data", []):
            try:
                # Price — Amadeus returns total price in requested currency
                price_info = offer.get("price", {})
                total_price = float(price_info.get("grandTotal") or price_info.get("total", 0))
                if total_price <= 0:
                    continue

                # Itinerary
                itineraries = offer.get("itineraries", [])
                if not itineraries:
                    continue

                first_itinerary = itineraries[0]
                segments = first_itinerary.get("segments", [])
                if not segments:
                    continue

                first_seg = segments[0]
                last_seg = segments[-1]

                # Duration
                duration_str = first_itinerary.get("duration", "")  # e.g. "PT2H30M"
                duration_minutes = _parse_amadeus_duration(duration_str)

                # Carrier
                carrier_code = first_seg.get("carrierCode", "")
                airline_name = raw_data.get("dictionaries", {}).get(
                    "carriers", {}
                ).get(carrier_code, carrier_code)

                # Departure / arrival
                dep_str = first_seg.get("departure", {}).get("at", "")
                arr_str = last_seg.get("arrival", {}).get("at", "")
                dep_time = dep_str[11:16] if len(dep_str) >= 16 else None
                arr_time = arr_str[11:16] if len(arr_str) >= 16 else None

                stops = len(segments) - 1

                # Booking date = today (when we queried)
                booking_date = collected_at.date()

                # Real API Fare Breakdown (extract only what API truly provides)
                raw_base = price_info.get("base")
                base_fare = float(raw_base) if raw_base is not None else None

                # Amadeus sometimes provides raw taxes list or total taxes
                raw_fees = price_info.get("fees", [])
                fee_sum = sum(float(f.get("amount", 0)) for f in raw_fees) if raw_fees else None

                # Real flight number from carrier + flight segment number
                flight_num = None
                if carrier_code and first_seg.get("number"):
                    flight_num = f"{carrier_code}-{first_seg.get('number')}"

                # Availability
                bookable_seats = offer.get("numberOfBookableSeats")
                avail = bool(bookable_seats > 0) if bookable_seats is not None else True

                results.append({
                    "source": "amadeus",
                    "source_provenance": "REAL_API",
                    "airline": airline_name or carrier_code,
                    "origin": origin.upper(),
                    "destination": destination.upper(),
                    "travel_date": departure_date,
                    "booking_date": booking_date,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "stops": stops,
                    "duration_minutes": duration_minutes,
                    "cabin_class": cabin_class.title() if cabin_class else "Economy",
                    "fare": round(total_price, 2),
                    "base_fare": round(base_fare, 2) if base_fare is not None else None,
                    "taxes": None,               # Left None when not unbundled in raw flight offer
                    "airport_fees": None,        # Left None when not unbundled in raw flight offer
                    "service_charge": fee_sum,   # Real fees sum if provided by API, else None
                    "flight_number": flight_num, # Real carrier flight number
                    "availability": avail,
                    "currency": "INR",
                    "days_left": (departure_date - booking_date).days,
                    "collected_at": collected_at,
                    "is_demo_anomaly": False,
                })

            except Exception as e:
                logger.warning(f"Failed to normalize Amadeus offer: {e}")
                continue

        return results

    def get_status(self) -> dict:
        """Return current Amadeus service status (for /live-status endpoint)."""
        if not self.is_available:
            return {
                "source": "amadeus",
                "status": "unavailable",
                "message": "Credentials not configured (set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET)",
                "last_fetch": None,
            }

        # Try token retrieval as connectivity test
        token = self._get_access_token()
        if token:
            return {
                "source": "amadeus",
                "status": "active",
                "message": "Connected — Amadeus API credentials valid",
                "last_fetch": datetime.utcnow(),
            }
        else:
            return {
                "source": "amadeus",
                "status": "error",
                "message": "Credentials configured but token retrieval failed",
                "last_fetch": None,
            }


def _parse_amadeus_duration(iso_duration: str) -> Optional[int]:
    """Parse ISO 8601 duration string (e.g. 'PT2H30M') to total minutes."""
    if not iso_duration:
        return None
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration)
    if not match:
        return None
    hours = int(match.group(1) or 0)
    mins = int(match.group(2) or 0)
    return hours * 60 + mins


# Module-level singleton
_amadeus_service: Optional[AmadeusService] = None


def get_amadeus_service() -> AmadeusService:
    global _amadeus_service
    if _amadeus_service is None:
        _amadeus_service = AmadeusService()
    return _amadeus_service
