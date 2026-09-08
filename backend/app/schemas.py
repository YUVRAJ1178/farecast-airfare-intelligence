"""
Airfare Intelligence Platform — Pydantic Schemas
Phase 6: FastAPI

Request/response schemas for all API endpoints.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Shared base models ────────────────────────────────────────

class RouteBase(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="IATA origin code")
    destination: str = Field(..., min_length=3, max_length=3, description="IATA destination code")


# ── Fare Observation ──────────────────────────────────────────

class FareObservationResponse(BaseModel):
    id: int
    source: str
    airline: str
    origin: str
    destination: str
    travel_date: date
    booking_date: Optional[date]
    departure_time: Optional[str]
    arrival_time: Optional[str]
    stops: int
    duration_minutes: Optional[int]
    cabin_class: str
    fare: float
    base_fare: Optional[float] = None
    taxes: Optional[float] = None
    airport_fees: Optional[float] = None
    service_charge: Optional[float] = None
    flight_number: Optional[str] = None
    availability: Optional[bool] = True
    source_provenance: Optional[str] = None
    currency: str
    days_left: Optional[int]
    is_demo_anomaly: bool
    collected_at: datetime

    model_config = {"from_attributes": True}


class FareQueryParams(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    airline: Optional[str] = None
    cabin_class: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    source: Optional[str] = None
    limit: int = Field(100, ge=1, le=5000)
    offset: int = Field(0, ge=0)


# ── Price Index ───────────────────────────────────────────────

class IndexValueResponse(BaseModel):
    id: int
    origin: str
    destination: str
    period_label: str
    period_start: date
    period_end: date
    avg_fare: float
    baseline_avg_fare: float
    index_value: float
    baseline_period: str
    cabin_class: Optional[str]
    observation_count: int
    is_prototype: bool
    calculated_at: datetime
    note: str = "Prototype Airfare Price Index — not the official GoI CPI index."

    model_config = {"from_attributes": True}


class IndexSummaryResponse(BaseModel):
    origin: str
    destination: str
    current_index: float
    baseline_fare: float
    current_fare: float
    change_pct: float
    periods: List[IndexValueResponse]
    note: str = "Prototype Airfare Price Index — not the official GoI CPI index."


# ── Prediction ────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    airline: str = Field(..., description="Airline name")
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    cabin_class: str = Field("Economy", description="Economy / Business / First")
    stops: int = Field(0, ge=0, le=3)
    days_left: int = Field(30, ge=1, le=365)
    duration_minutes: Optional[int] = Field(None, ge=10, le=1500)
    departure_hour: int = Field(10, ge=0, le=23)

    @field_validator("origin", "destination")
    @classmethod
    def uppercase_iata(cls, v):
        return v.upper()


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    predicted_fare: float
    lower_bound: float
    upper_bound: float
    confidence: str      # high / medium / low
    model_name: str
    r2_score: Optional[float]
    mae: Optional[float]
    note: str
    lookup_method: Optional[str] = None   # How base fare was resolved
    recommendation: Optional[str] = None  # Actionable booking advice (Buy Now / Wait)
    request: PredictionRequest


# ── Anomaly ───────────────────────────────────────────────────

class AnomalyResponse(BaseModel):
    id: int
    origin: str
    destination: str
    airline: Optional[str]
    observed_fare: float
    expected_low: float
    expected_high: float
    expected_baseline: float
    pct_deviation: float
    severity: str         # LOW / MEDIUM / HIGH / CRITICAL
    detection_method: Optional[str]
    explanation: Optional[str] = None
    is_demo: bool
    observation_date: Optional[date]
    detected_at: datetime

    model_config = {"from_attributes": True}


# ── Dashboard Summary ─────────────────────────────────────────

class KPICards(BaseModel):
    avg_fare: float
    min_fare: float
    max_fare: float
    airfare_price_index: Optional[float]
    total_observations: int
    live_observations: int
    data_source: str         # "live" / "historical" / "demo"
    last_updated: Optional[datetime]


class DashboardSummaryResponse(BaseModel):
    kpi: KPICards
    top_routes: List[dict]
    fare_trend: List[dict]
    airline_comparison: List[dict]
    anomaly_count: int
    data_mode: str           # "live" / "historical" / "demo"
    note: Optional[str]


# ── Live Status ───────────────────────────────────────────────

class DataSourceStatus(BaseModel):
    source: str
    status: str           # "active" / "unavailable" / "demo"
    message: str
    last_fetch: Optional[datetime]


class LiveStatusResponse(BaseModel):
    overall_mode: str     # "live" / "historical" / "demo"
    ignav: DataSourceStatus
    amadeus: Optional[DataSourceStatus] = None   # Legacy — kept for backward compat
    database: DataSourceStatus
    ml_model: DataSourceStatus
    note: str


# ── Health ────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    ml_model: str
    ignav: str
    amadeus: str   # Legacy field — kept for backward compat
    demo_mode: bool
    timestamp: datetime


# ── Routes / Airlines lists ───────────────────────────────────

class RouteInfo(BaseModel):
    origin: str
    destination: str
    origin_name: Optional[str]
    destination_name: Optional[str]
    observation_count: int

    model_config = {"from_attributes": True}


class AirlineInfo(BaseModel):
    name: str
    observation_count: int
    avg_fare: Optional[float]
    routes: int


# ── Ignav Live Search (active REAL_API_FARES provider) ───────────

class IgnavSearchRequest(BaseModel):
    """
    Request schema for the Ignav one-way fare search.
    Endpoint: POST https://ignav.com/api/fares/one-way
    Auth:     X-Api-Key header (server-side only — IGNAV_API_KEY env var)
    """
    origin: str = Field(..., min_length=3, max_length=3, description="IATA departure code")
    destination: str = Field(..., min_length=3, max_length=3, description="IATA arrival code")
    departure_date: date
    adults: int = Field(1, ge=1, le=9)
    cabin_class: str = Field(
        "Economy",
        description="Economy / Premium Economy / Business / First",
    )
    max_stops: Optional[int] = Field(
        None, ge=0, le=2, description="0=nonstop, 1, 2, or omit for any"
    )
    market: str = Field("IN", min_length=2, max_length=2, description="2-letter market code (e.g. IN, US, GB)")

    @field_validator("origin", "destination")
    @classmethod
    def uppercase_iata(cls, v):
        return v.upper()


class IgnavSearchResponse(BaseModel):
    """Response schema for a successful Ignav live fare search."""
    source: str = "ignav"
    provider: str = "Ignav"
    origin: str
    destination: str
    departure_date: date
    results_count: int
    fares: List[FareObservationResponse]
    note: str = (
        "Live data from Ignav Flight Prices API. "
        "source_provenance=REAL_API. "
        "Fields not provided by Ignav (taxes, base_fare, etc.) are NULL — no fabrication."
    )
    fetched_at: datetime


# ── Amadeus Live Search (legacy — retained for backward compat) ───

class AmadeusSearchRequest(BaseModel):
    """Legacy Amadeus search request — retained for backward compatibility."""
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure_date: date
    adults: int = Field(1, ge=1, le=9)
    cabin_class: str = Field("ECONOMY", description="ECONOMY / BUSINESS / FIRST")

    @field_validator("origin", "destination")
    @classmethod
    def uppercase_iata(cls, v):
        return v.upper()


class AmadeusSearchResponse(BaseModel):
    """Legacy Amadeus response schema — retained for backward compatibility."""
    source: str = "amadeus"
    origin: str
    destination: str
    departure_date: date
    results_count: int
    fares: List[FareObservationResponse]
    note: str = "Legacy Amadeus Flight Offers Search API (no longer the active provider)."
    fetched_at: datetime
