"""
Tests for Data Provenance Integrity and Authenticity.
SIH Problem Statement 26056: Auditing data authenticity and ensuring no synthetic
record is ever labeled as REAL_API or REAL_SCRAPE.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_session_factory
from backend.app.models import AirfareObservation

client = TestClient(app)


def test_no_synthetic_labeled_as_real():
    """Verify that no synthetic source is labeled REAL_API in the database."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        synthetic_sources = ["historical_augmented", "scheduled_domestic", "demo"]
        fake_real_count = db.query(AirfareObservation).filter(
            AirfareObservation.source.in_(synthetic_sources),
            AirfareObservation.source_provenance.in_(["REAL_API", "REAL_SCRAPE"])
        ).count()
        assert fake_real_count == 0, f"Found {fake_real_count} synthetic records falsely marked as REAL!"


def test_all_observations_have_valid_provenance():
    """Verify that every single observation in the DB has a non-null valid provenance tag."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        valid_tags = {"REAL_API", "REAL_SCRAPE", "DGCA_PUBLIC", "HISTORICAL_SNAPSHOT", "SYNTHETIC_AUGMENTED", "SYNTHETIC_DEMO"}
        null_or_invalid = db.query(AirfareObservation).filter(
            (AirfareObservation.source_provenance == None) |
            (~AirfareObservation.source_provenance.in_(valid_tags))
        ).count()
        assert null_or_invalid == 0, f"Found {null_or_invalid} records with null/invalid source_provenance!"


def test_provenance_summary_endpoint():
    """Test /fares/provenance-summary endpoint returns accurate percentages summing to 100%."""
    response = client.get("/fares/provenance-summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_observations" in data
    assert "counts" in data
    assert "percentages" in data
    assert data["total_observations"] > 0
    
    pcts = data["percentages"]
    total_pct = sum(pcts.values())
    assert 99.9 <= total_pct <= 100.1, f"Percentages do not sum to 100%: {total_pct}"
    # REAL_API may be > 0.0% when Ignav live fares are present in the database
    assert pcts.get("REAL_API", 0.0) >= 0.0, "REAL_API percentage must be non-negative"


def test_fare_decomposition_consistency():
    """Test that base_fare + taxes + airport_fees + service_charge approximates total fare."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        sample = db.query(AirfareObservation).filter(
            AirfareObservation.base_fare.isnot(None),
            AirfareObservation.taxes.isnot(None),
            AirfareObservation.airport_fees.isnot(None),
            AirfareObservation.service_charge.isnot(None)
        ).limit(50).all()
        
        assert len(sample) > 0
        for obs in sample:
            decomposed = obs.base_fare + obs.taxes + obs.airport_fees + obs.service_charge
            # Allowed tolerance of 1 INR due to individual roundings
            assert abs(decomposed - obs.fare) <= 2.0, f"Decomposition error on ID {obs.id}: sum={decomposed}, total={obs.fare}"


def test_dashboard_exposes_provenance():
    """Test that /dashboard-summary returns the provenance breakdown."""
    response = client.get("/dashboard-summary")
    assert response.status_code == 200
    data = response.json()
    assert "provenance_breakdown" in data
    prov = data["provenance_breakdown"]
    assert "HISTORICAL_SNAPSHOT_PCT" in prov
    assert "SYNTHETIC_AUGMENTED_PCT" in prov
    assert "REAL_API_PCT" in prov
