"""
Airfare Intelligence Platform — SQLAlchemy Database Models
Phase 5: PostgreSQL

Table definitions for all entities.
Uses SQLAlchemy 2.x declarative style.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AirfareObservation(Base):
    """
    Core table: one row per observed airfare.
    Covers historical, live (Amadeus), and demo data.
    Source field always present to distinguish provenance.
    """
    __tablename__ = "airfare_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)          # DataSource constant
    airline = Column(String(100), nullable=False, index=True)
    origin = Column(String(10), nullable=False, index=True)          # IATA code
    destination = Column(String(10), nullable=False, index=True)     # IATA code
    travel_date = Column(Date, nullable=False, index=True)
    booking_date = Column(Date, nullable=True)
    departure_time = Column(String(10), nullable=True)               # HH:MM
    arrival_time = Column(String(10), nullable=True)                 # HH:MM
    stops = Column(Integer, nullable=False, default=0)
    duration_minutes = Column(Integer, nullable=True)
    cabin_class = Column(String(50), nullable=False, default="Economy")
    fare = Column(Float, nullable=False)                            # Total fare in INR
    base_fare = Column(Float, nullable=True)                         # Base airfare excl. taxes
    taxes = Column(Float, nullable=True)                             # Total statutory taxes (GST, etc.)
    airport_fees = Column(Float, nullable=True)                      # UDF / PSF / Airport development charges
    service_charge = Column(Float, nullable=True)                    # Airline/OTA booking or fuel surcharge
    flight_number = Column(String(50), nullable=True)                # e.g. "6E-205", "AI-101"
    availability = Column(Boolean, nullable=True, default=True)      # Available seat inventory indicator
    currency = Column(String(10), nullable=False, default="INR")
    days_left = Column(Integer, nullable=True)
    is_demo_anomaly = Column(Boolean, default=False, nullable=False)
    source_provenance = Column(String(50), nullable=True)            # REAL_API / HISTORICAL_SNAPSHOT / SYNTHETIC_DEMO
    collected_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_obs_route", "origin", "destination"),
        Index("ix_obs_route_date", "origin", "destination", "travel_date"),
        Index("ix_obs_source_collected", "source", "collected_at"),
    )

    def __repr__(self):
        return (
            f"<AirfareObservation id={self.id} "
            f"{self.origin}→{self.destination} "
            f"₹{self.fare:.0f} [{self.source}]>"
        )


class Route(Base):
    """
    Lookup table for route metadata.
    Populated automatically from observed data.
    """
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    origin_name = Column(String(200), nullable=True)
    destination_name = Column(String(200), nullable=True)
    observation_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("origin", "destination", name="uq_route"),
    )


class IndexValue(Base):
    """
    Airfare Price Index values.
    Stored at route level (and aggregate when origin=ALL, destination=ALL).

    Index = (avg_fare_period / baseline_avg_fare) × 100
    Baseline period must always be stored for transparency.

    IMPORTANT: Clearly labelled as PROTOTYPE index — not official GoI index.
    """
    __tablename__ = "index_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String(10), nullable=False, index=True)      # "ALL" for aggregate
    destination = Column(String(10), nullable=False, index=True) # "ALL" for aggregate
    period_label = Column(String(50), nullable=False)            # e.g. "2023-Q1", "2024-03"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    avg_fare = Column(Float, nullable=False)
    baseline_avg_fare = Column(Float, nullable=False)
    index_value = Column(Float, nullable=False)                  # avg_fare / baseline × 100
    baseline_period = Column(String(100), nullable=False)        # e.g. "2023-01 to 2023-03"
    cabin_class = Column(String(50), nullable=True)              # Economy / Business / All
    observation_count = Column(Integer, nullable=False, default=0)
    is_prototype = Column(Boolean, default=True, nullable=False) # Always true
    calculated_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("ix_index_route_period", "origin", "destination", "period_label"),
    )


class Prediction(Base):
    """
    Stored fare predictions from the ML model.
    Predictions are recorded with the model version used.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    airline = Column(String(100), nullable=True)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    cabin_class = Column(String(50), default="Economy")
    stops = Column(Integer, default=0)
    days_left = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    departure_hour = Column(Integer, nullable=True)
    predicted_fare = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    confidence = Column(String(20), nullable=True)   # high / medium / low
    model_name = Column(String(200), nullable=True)
    r2_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    predicted_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return (
            f"<Prediction {self.origin}→{self.destination} "
            f"₹{self.predicted_fare:.0f} [{self.model_name}]>"
        )


class Anomaly(Base):
    """
    Detected airfare anomalies.
    Contains context for UI display.

    IMPORTANT: Demo anomalies are always tagged is_demo=True.
    Live anomalies must be based on real data only.
    """
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    airline = Column(String(100), nullable=True)
    observed_fare = Column(Float, nullable=False)
    expected_low = Column(Float, nullable=False)      # Lower bound of expected range
    expected_high = Column(Float, nullable=False)     # Upper bound of expected range
    expected_baseline = Column(Float, nullable=False) # Midpoint baseline
    pct_deviation = Column(Float, nullable=False)     # Signed percentage deviation
    severity = Column(String(20), nullable=False)     # LOW / MEDIUM / HIGH / CRITICAL
    detection_method = Column(String(100), nullable=True)  # e.g., "IQR", "IsolationForest"
    explanation = Column(Text, nullable=True)              # Plain text explanation of why anomaly was triggered
    is_demo = Column(Boolean, default=False, nullable=False)
    observation_date = Column(Date, nullable=True)
    detected_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)  # False when anomaly is resolved

    __table_args__ = (
        Index("ix_anomaly_route_detected", "origin", "destination", "detected_at"),
    )

    def __repr__(self):
        return (
            f"<Anomaly {self.origin}→{self.destination} "
            f"₹{self.observed_fare:.0f} ({self.pct_deviation:+.1f}%) "
            f"[{self.severity}]>"
        )


class DGCAMonthlyBenchmark(Base):
    """
    Official DGCA / Ministry of Civil Aviation Monthly Sector Average Fare Benchmark.
    Sourced from Tariff Monitoring Unit (TMU) reports submitted to Parliament / MoCA gazettes.
    Strictly differentiated from daily platform fares and statutory fare caps.
    """
    __tablename__ = "dgca_monthly_benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    period_label = Column(String(20), nullable=False, index=True)  # e.g. "2025-02", "2025-03", "2025-04"
    dgca_avg_fare = Column(Float, nullable=False)
    distance_km = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True)                  # e.g. "Category I (Metro Trunk)"
    source_document = Column(String(250), nullable=False)          # Parliamentary / DGCA TMU gazette citation
    retrieval_date = Column(Date, nullable=False)
    provenance = Column(String(50), nullable=False, default="DGCA_PUBLIC_BENCHMARK")
    created_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_dgca_bench_route_period", "origin", "destination", "period_label"),
    )

    def __repr__(self):
        return (
            f"<DGCAMonthlyBenchmark {self.origin}→{self.destination} "
            f"[{self.period_label}]: ₹{self.dgca_avg_fare:.2f}>"
        )

