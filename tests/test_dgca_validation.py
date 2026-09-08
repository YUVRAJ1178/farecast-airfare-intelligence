"""
Tests for DGCA Backtesting and Regulatory Benchmark Validation.
SIH Problem Statement 26056: Disclose regulatory nature and avoid false empirical claims.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.backtesting_service import DGCA_STATUTORY_CAPS, run_30day_dgca_backtest
from backend.app.database import get_session_factory

client = TestClient(app)


def test_statutory_caps_defined():
    """Verify that DGCA statutory fare caps are defined for trunk corridors."""
    assert len(DGCA_STATUTORY_CAPS) >= 30
    assert ("DEL", "BOM") in DGCA_STATUTORY_CAPS
    assert DGCA_STATUTORY_CAPS[("DEL", "BOM")]["floor"] > 0
    assert DGCA_STATUTORY_CAPS[("DEL", "BOM")]["cap"] > DGCA_STATUTORY_CAPS[("DEL", "BOM")]["floor"]


def test_backtesting_response_structure():
    """Verify that backtesting endpoint reports regulatory benchmark metadata."""
    response = client.get("/backtesting/dgca/30-day")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "daily_comparison" in data
    
    summary = data["summary"]
    assert summary["total_days_evaluated"] == 30
    assert "benchmark_category" in summary
    assert summary["benchmark_category"] == "REGULATORY_FARE_BAND"
    assert summary["is_empirical_dgca_observation"] is False, "Must not claim empirical DGCA observations"
    assert len(data["daily_comparison"]) == 30


def test_backtest_route_filtering():
    """Verify route-specific backtesting against route statutory caps."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        res = run_30day_dgca_backtest(db=db, origin="DEL", destination="BOM")
        summary = res["summary"]
        assert summary["origin"] == "DEL"
        assert summary["destination"] == "BOM"
        assert summary["has_statutory_caps"] is True
        assert summary["dgca_statutory_floor"] == 3500
        assert summary["dgca_statutory_cap"] == 25000
