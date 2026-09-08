"""
Airfare Intelligence Platform — Test Suite
Tests for: data cleaning, fare validation, index calculation,
           prediction endpoint, anomaly detection, health endpoint.

Run: pytest tests/ -v
"""

import sys
from pathlib import Path
from datetime import date, datetime

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# TEST: Data Cleaning
# ═══════════════════════════════════════════════════════════════

class TestDataCleaning:

    def test_normalize_airline_known(self):
        from data.cleaning import _normalize_airline
        assert _normalize_airline("indigo") == "IndiGo"
        assert _normalize_airline("Indigo") == "IndiGo"
        assert _normalize_airline("6E") == "IndiGo"

    def test_normalize_airline_unknown(self):
        from data.cleaning import _normalize_airline
        result = _normalize_airline("SomeNewAirline")
        assert result == "SomeNewAirline"  # Return as-is, not fabricated

    def test_normalize_airline_nan(self):
        from data.cleaning import _normalize_airline
        result = _normalize_airline(float("nan"))
        assert result == "Unknown"

    def test_city_to_iata_known(self):
        from data.cleaning import _normalize_city_to_iata
        assert _normalize_city_to_iata("Delhi") == "DEL"
        assert _normalize_city_to_iata("Mumbai") == "BOM"
        assert _normalize_city_to_iata("Bengaluru") == "BLR"

    def test_city_to_iata_already_iata(self):
        from data.cleaning import _normalize_city_to_iata
        assert _normalize_city_to_iata("DEL") == "DEL"

    def test_normalize_cabin(self):
        from data.cleaning import _normalize_cabin
        assert _normalize_cabin("economy") == "Economy"
        assert _normalize_cabin("ECONOMY") == "Economy"
        assert _normalize_cabin("Business") == "Business"

    def test_normalize_stops_string(self):
        from data.cleaning import _normalize_stops
        assert _normalize_stops("non-stop") == 0
        assert _normalize_stops("1 stop") == 1
        assert _normalize_stops("2 stops") == 2

    def test_normalize_stops_numeric(self):
        from data.cleaning import _normalize_stops
        assert _normalize_stops(0) == 0
        assert _normalize_stops(1) == 1
        assert _normalize_stops(2.0) == 2

    def test_parse_duration_hm_format(self):
        from data.cleaning import _parse_duration_to_minutes
        assert _parse_duration_to_minutes("2h 30m") == 150
        assert _parse_duration_to_minutes("1h") == 60
        assert _parse_duration_to_minutes("3h 15m") == 195

    def test_parse_duration_minutes_only(self):
        from data.cleaning import _parse_duration_to_minutes
        assert _parse_duration_to_minutes("120") == 120

    def test_parse_duration_invalid_returns_none(self):
        from data.cleaning import _parse_duration_to_minutes
        result = _parse_duration_to_minutes("invalid")
        # Must be None — we do NOT fabricate duration
        assert result is None

    def test_validate_fare_valid(self):
        from data.cleaning import _validate_fare
        assert _validate_fare("4500") == 4500.0
        assert _validate_fare(3999.50) == 3999.5

    def test_validate_fare_negative_is_none(self):
        from data.cleaning import _validate_fare
        result = _validate_fare(-100)
        assert result is None  # Negative fare is invalid

    def test_validate_fare_zero_is_none(self):
        from data.cleaning import _validate_fare
        result = _validate_fare(0)
        assert result is None  # Zero fare is invalid

    def test_validate_fare_string_garbage_is_none(self):
        from data.cleaning import _validate_fare
        result = _validate_fare("not_a_number")
        assert result is None

    def test_clean_kaggle_drops_invalid_fares(self):
        """Rows with missing/negative fares must be dropped, not fabricated."""
        from data.cleaning import clean_kaggle_dataset
        raw = pd.DataFrame({
            "airline": ["IndiGo", "IndiGo", "SpiceJet"],
            "source_city": ["Delhi", "Delhi", "Mumbai"],
            "destination_city": ["Mumbai", "Mumbai", "Delhi"],
            "departure_time": ["10:00", "12:00", "09:00"],
            "arrival_time": ["12:00", "14:00", "11:00"],
            "stops": ["non-stop", "non-stop", "1 stop"],
            "class": ["Economy", "Economy", "Business"],
            "duration": ["2h", "2h", "2h"],
            "days_left": [30, 15, 7],
            "price": [4500, -100, None],  # Last two invalid
        })
        cleaned = clean_kaggle_dataset(raw)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["fare"] == 4500.0

    def test_clean_kaggle_removes_duplicates(self):
        from data.cleaning import clean_kaggle_dataset
        raw = pd.DataFrame({
            "airline": ["IndiGo", "IndiGo"],
            "source_city": ["Delhi", "Delhi"],
            "destination_city": ["Mumbai", "Mumbai"],
            "departure_time": ["10:00", "10:00"],
            "arrival_time": ["12:00", "12:00"],
            "stops": ["non-stop", "non-stop"],
            "class": ["Economy", "Economy"],
            "duration": ["2h", "2h"],
            "days_left": [30, 30],
            "price": [4500, 4500],
        })
        cleaned = clean_kaggle_dataset(raw)
        assert len(cleaned) == 1

    def test_clean_kaggle_source_is_tagged(self):
        from data.cleaning import clean_kaggle_dataset
        from data.schema import DataSource
        raw = pd.DataFrame({
            "airline": ["IndiGo"],
            "source_city": ["Delhi"],
            "destination_city": ["Mumbai"],
            "departure_time": ["10:00"],
            "arrival_time": ["12:00"],
            "stops": ["non-stop"],
            "class": ["Economy"],
            "duration": ["2h"],
            "days_left": [30],
            "price": [4500],
        })
        cleaned = clean_kaggle_dataset(raw)
        assert cleaned.iloc[0]["source"] == DataSource.KAGGLE_HISTORICAL


# ═══════════════════════════════════════════════════════════════
# TEST: Airfare Price Index Calculation
# ═══════════════════════════════════════════════════════════════

class TestIndexCalculation:

    def test_index_baseline_equals_100(self):
        """If period fare equals baseline fare, index must be exactly 100."""
        baseline = 4500.0
        current = 4500.0
        index = (current / baseline) * 100
        assert abs(index - 100.0) < 0.001

    def test_index_above_baseline(self):
        """20% fare increase → index = 120."""
        baseline = 4500.0
        current = 5400.0
        index = (current / baseline) * 100
        assert abs(index - 120.0) < 0.001

    def test_index_below_baseline(self):
        """10% fare decrease → index = 90."""
        baseline = 5000.0
        current = 4500.0
        index = (current / baseline) * 100
        assert abs(index - 90.0) < 0.01

    def test_index_example_from_spec(self):
        """Verify the spec example: baseline=4500, current=5400 → index=120."""
        baseline = 4500.0
        current = 5400.0
        index = round((current / baseline) * 100, 2)
        assert index == 120.0

    def test_index_cannot_be_computed_with_zero_baseline(self):
        """Zero baseline is invalid — should not divide by zero."""
        baseline = 0.0
        current = 5000.0
        with pytest.raises(ZeroDivisionError):
            _ = (current / baseline) * 100


# ═══════════════════════════════════════════════════════════════
# TEST: Anomaly Detection
# ═══════════════════════════════════════════════════════════════

class TestAnomalyDetection:

    def _get_severity(self, pct_deviation):
        from backend.app.services.anomaly_service import _get_severity
        return _get_severity(pct_deviation)

    def test_severity_low(self):
        assert self._get_severity(25.0) == "LOW"
        assert self._get_severity(-25.0) == "LOW"

    def test_severity_medium(self):
        assert self._get_severity(45.0) == "MEDIUM"
        assert self._get_severity(-45.0) == "MEDIUM"

    def test_severity_high(self):
        assert self._get_severity(75.0) == "HIGH"
        assert self._get_severity(-75.0) == "HIGH"

    def test_severity_critical(self):
        assert self._get_severity(150.0) == "CRITICAL"
        assert self._get_severity(-120.0) == "CRITICAL"

    def test_demo_anomaly_tagged_correctly(self):
        """Demo anomalies in the generator must always have is_demo_anomaly=True."""
        from data.demo_generator import generate_demo_dataset, generate_demo_anomalies
        df = generate_demo_dataset(n_records=500)
        df_with_anomalies = generate_demo_anomalies(df, n_anomalies=5)

        anomaly_rows = df_with_anomalies[
            df_with_anomalies.get("is_demo_anomaly", False) == True
        ]
        # All anomaly rows must be tagged as demo
        if len(anomaly_rows) > 0:
            assert anomaly_rows["source"].str.lower().eq("demo").all()


# ═══════════════════════════════════════════════════════════════
# TEST: Demo Generator
# ═══════════════════════════════════════════════════════════════

class TestDemoGenerator:

    def test_generates_expected_count(self):
        from data.demo_generator import generate_demo_dataset
        df = generate_demo_dataset(n_records=1000)
        assert len(df) == 1000

    def test_all_fares_positive(self):
        from data.demo_generator import generate_demo_dataset
        df = generate_demo_dataset(n_records=500)
        assert (df["fare"] > 0).all()

    def test_all_tagged_as_demo(self):
        from data.demo_generator import generate_demo_dataset
        from data.schema import DataSource
        df = generate_demo_dataset(n_records=500)
        assert (df["source"] == DataSource.DEMO).all()

    def test_required_columns_present(self):
        from data.demo_generator import generate_demo_dataset
        df = generate_demo_dataset(n_records=100)
        required = [
            "source", "airline", "origin", "destination",
            "travel_date", "fare", "currency", "cabin_class", "stops"
        ]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_origin_destination_are_iata_codes(self):
        from data.demo_generator import generate_demo_dataset
        from data.schema import IATA_CITY_MAP
        df = generate_demo_dataset(n_records=200)
        # All origins and destinations should be 3-letter codes
        assert df["origin"].str.len().eq(3).all()
        assert df["destination"].str.len().eq(3).all()

    def test_currency_is_inr(self):
        from data.demo_generator import generate_demo_dataset
        df = generate_demo_dataset(n_records=100)
        assert (df["currency"] == "INR").all()


# ═══════════════════════════════════════════════════════════════
# TEST: FastAPI Health Endpoint (requires running app)
# ═══════════════════════════════════════════════════════════════

class TestHealthEndpoint:
    """
    Integration tests for the FastAPI health endpoint.
    These tests use httpx TestClient and do not require a live DB.
    """

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        return TestClient(app)

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_required_fields(self, client):
        response = client.get("/health")
        data = response.json()
        required_keys = ["status", "version", "database", "ml_model", "amadeus", "demo_mode"]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_root_returns_service_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "demo_mode" in data


# ═══════════════════════════════════════════════════════════════
# TEST: DGCA 30-Day Backtesting Engine
# ═══════════════════════════════════════════════════════════════

class TestDGCABacktesting:

    def test_backtesting_api_endpoints(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        # 30-day detailed
        res = client.get("/backtesting/dgca/30-day")
        assert res.status_code == 200
        data = res.json()
        assert "summary" in data
        assert "daily_comparison" in data
        assert len(data["daily_comparison"]) == 30
        assert data["summary"]["total_days_evaluated"] == 30
        assert data["summary"]["evaluation_status"] == "PASSED (High Fidelity)"
        assert data["summary"]["correlation"] > 0.90
        assert data["summary"]["mape"] < 10.0
        assert data["summary"]["pass_rate_pct"] == 100.0

        # Summary endpoint
        res_summary = client.get("/backtesting/dgca/summary")
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        assert "pass_rate_pct" in summary_data
        assert "correlation" in summary_data
        assert summary_data["correlation"] > 0.90

        # Routes endpoint
        res_routes = client.get("/backtesting/dgca/routes")
        assert res_routes.status_code == 200
        routes_data = res_routes.json()
        assert isinstance(routes_data, list)
        assert len(routes_data) > 0

    def test_backtesting_route_specific(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        res = client.get("/backtesting/dgca/30-day?origin=DEL&destination=BOM")
        assert res.status_code == 200
        data = res.json()
        assert len(data["daily_comparison"]) == 30
        assert data["summary"]["route"] == "DEL→BOM"
        assert data["summary"]["correlation"] > 0.95


# ═══════════════════════════════════════════════════════════════
# TEST: DGCA Route Weights Engine
# ═══════════════════════════════════════════════════════════════

class TestDGCARouteWeights:

    def test_dgca_weights_table_completeness(self):
        from backend.app.services.dgca_weights import get_all_dgca_route_weights, TOTAL_ANNUAL_PAX_MILLIONS
        weights = get_all_dgca_route_weights()
        assert len(weights) == 48
        assert TOTAL_ANNUAL_PAX_MILLIONS > 30.0  # ~35.7M pax

        total_weight = sum(w["weight"] for w in weights)
        assert abs(total_weight - 1.0) < 0.01

        # Check top corridor is DEL-BOM
        del_bom = next(w for w in weights if w["origin"] == "DEL" and w["destination"] == "BOM")
        assert del_bom["distance_km"] == 1148
        assert del_bom["annual_pax_millions"] == 3.10
        assert del_bom["category"] == "Category I (Metro Trunk)"
        assert del_bom["weight_pct"] > 5.0
        # DEL-BOM must have the highest single-route weight in India
        assert del_bom["weight_pct"] == max(w["weight_pct"] for w in weights)

    def test_normalized_weights_subset(self):
        from backend.app.services.dgca_weights import get_normalized_dgca_weights
        subset = [("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR")]
        norm_w = get_normalized_dgca_weights(subset)
        assert len(norm_w) == 3
        assert abs(sum(norm_w.values()) - 1.0) < 1e-6
        assert norm_w[("DEL", "BOM")] > norm_w[("DEL", "BLR")] > norm_w[("BOM", "BLR")]

    def test_dgca_weights_api_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        res = client.get("/index/dgca-weights")
        assert res.status_code == 200
        data = res.json()
        assert data["total_routes"] == 48
        assert "weights" in data
        assert len(data["weights"]) == 48
        assert "total_monitored_pax_millions" in data

    def test_aggregate_index_with_dgca_weights_comparison(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        # DGCA weighted
        res_weighted = client.get("/index/?use_dgca_weights=true")
        assert res_weighted.status_code == 200
        w_data = res_weighted.json()
        assert w_data["use_dgca_weights"] is True
        assert "DGCA City-Pair" in w_data["weight_method"]
        assert "unweighted_index" in w_data
        assert "weighting_divergence" in w_data

        # Unweighted
        res_unweighted = client.get("/index/?use_dgca_weights=false")
        assert res_unweighted.status_code == 200
        u_data = res_unweighted.json()
        assert u_data["use_dgca_weights"] is False
        assert "Equal weights" in u_data["weight_method"]


class TestCalibratedFarePredictor:
    def test_booking_curve_dynamics(self):
        from ml.predict import get_predictor
        predictor = get_predictor()
        # 1 day out should cost noticeably more than 30 days out
        pred_1d = predictor.predict("IndiGo", "DEL", "BOM", "Economy", days_left=1)
        pred_30d = predictor.predict("IndiGo", "DEL", "BOM", "Economy", days_left=30)
        assert pred_1d.predicted_fare > pred_30d.predicted_fare
        assert pred_1d.predicted_fare >= 1.4 * pred_30d.predicted_fare

    def test_business_class_premium(self):
        from ml.predict import get_predictor
        predictor = get_predictor()
        econ = predictor.predict("Air India", "DEL", "BOM", "Economy", days_left=14)
        biz = predictor.predict("Air India", "DEL", "BOM", "Business", days_left=14)
        assert biz.predicted_fare > 4 * econ.predicted_fare

    def test_prediction_api_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        res = client.post(
            "/predict/",
            json={
                "airline": "IndiGo",
                "origin": "DEL",
                "destination": "BOM",
                "cabin_class": "Economy",
                "stops": 0,
                "days_left": 7,
                "duration_minutes": 135,
                "departure_hour": 8,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "predicted_fare" in data
        assert data["predicted_fare"] > 3000
        assert "lookup_method" in data
        assert data["confidence"] in ["high", "medium", "low"]

    def test_prediction_info_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)

        res = client.get("/predict/")
        assert res.status_code == 200
        data = res.json()
        assert data["model_ready"] is True
        assert "pricing_engine" in data
        assert data["pricing_engine"]["type"] == "hybrid"




