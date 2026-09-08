"""
Tests for SIH 26056 Advance-Purchase Windows: T+1, T+7, T+15, T+30, T+45.
"""
import pytest
from backend.app.database import get_session_factory
from backend.app.models import AirfareObservation


@pytest.mark.parametrize("window_days", [1, 7, 15, 30, 45])
def test_advance_purchase_window_exists(window_days):
    """Verify that each required advance-purchase window is represented in the database."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        count = db.query(AirfareObservation).filter(
            AirfareObservation.days_left == window_days
        ).count()
        assert count > 0, f"Mandatory advance purchase window T+{window_days} is missing!"


def test_advance_purchase_t45_authenticity():
    """Verify that T+45 window contains authentic historical snapshot data."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        provenances = db.query(AirfareObservation.source_provenance).filter(
            AirfareObservation.days_left == 45
        ).distinct().all()
        prov_list = [p[0] for p in provenances]
        assert "HISTORICAL_SNAPSHOT" in prov_list, "T+45 must contain authentic historical snapshot records"


def test_advance_purchase_route_diversity():
    """Verify that windows have broad route representation."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        for w in [1, 7, 15, 30]:
            routes_count = db.query(
                AirfareObservation.origin, AirfareObservation.destination
            ).filter(
                AirfareObservation.days_left == w
            ).distinct().count()
            assert routes_count >= 30, f"Window T+{w} has fewer than 30 distinct routes: {routes_count}"
