"""
Tests for DGCA Monthly Benchmark and SIH 25-Point Compliance.
SIH Problem Statement 26056: Verifying monthly benchmark aggregation and audit endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_session_factory
from backend.app.models import DGCAMonthlyBenchmark
from backend.app.services.dgca_monthly_service import (
    seed_dgca_monthly_benchmarks,
    run_dgca_monthly_comparison,
)

client = TestClient(app)


def test_dgca_monthly_benchmark_seeding():
    """Verify that DGCA monthly sector benchmarks are seeded into database."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        count = seed_dgca_monthly_benchmarks(db)
        assert count >= 20, f"Expected at least 20 seeded benchmarks, got {count}"
        
        del_bom = db.query(DGCAMonthlyBenchmark).filter(
            DGCAMonthlyBenchmark.origin == "DEL",
            DGCAMonthlyBenchmark.destination == "BOM",
            DGCAMonthlyBenchmark.period_label == "2025-02"
        ).first()
        assert del_bom is not None
        assert del_bom.dgca_avg_fare > 0
        assert del_bom.provenance == "DGCA_PUBLIC_BENCHMARK"


def test_dgca_monthly_aggregation_comparison():
    """Verify daily to monthly aggregation comparison calculation."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        res = run_dgca_monthly_comparison(db=db, period_label="2025-02")
        assert "summary" in res
        assert "sectors" in res
        summary = res["summary"]
        assert summary["sectors_evaluated"] > 0
        assert summary["mape"] >= 0
        assert -1.0 <= summary["correlation"] <= 1.0
        assert len(res["sectors"]) > 0


def test_dgca_monthly_benchmark_endpoint():
    """Verify GET /backtesting/dgca/monthly-benchmark endpoint."""
    response = client.get("/backtesting/dgca/monthly-benchmark?period=2025-02")
    assert response.status_code == 200
    data = response.json()
    assert data["benchmark_type"] == "DGCA_MONTHLY_AVERAGE_FARE"
    assert data["is_empirical_dgca_observation"] is True
    assert "summary" in data
    assert "sectors" in data


def test_regulatory_bands_endpoint_alias():
    """Verify GET /backtesting/dgca/regulatory-bands endpoint."""
    response = client.get("/backtesting/dgca/regulatory-bands")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["benchmark_category"] == "REGULATORY_FARE_BAND"


def test_sih_compliance_endpoint():
    """Verify GET /compliance/sih-compliance endpoint evaluates all 25 requirements."""
    response = client.get("/compliance/sih-compliance")
    assert response.status_code == 200
    data = response.json()
    assert "overall_readiness_pct" in data
    assert data["overall_readiness_pct"] > 85.0
    assert "requirements" in data
    reqs = data["requirements"]
    assert len(reqs) == 25
    
    # Check that all requirements have evidence and valid completion %
    for r in reqs:
        assert "requirement" in r
        assert "status" in r
        assert "evidence" in r
        assert "data_source" in r
        assert 0 <= r["completion_pct"] <= 100
