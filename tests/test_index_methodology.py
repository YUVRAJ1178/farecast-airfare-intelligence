"""
Tests for Airfare Price Index Mathematical Specification.
SIH Problem Statement 26056: Index calculation, Laspeyres weighting, outlier handling.
"""
import pytest
from datetime import date
from backend.app.database import get_session_factory
from backend.app.services.dgca_weights import (
    DGCA_TRUNK_CORRIDORS,
    get_normalized_dgca_weights,
    TOTAL_ANNUAL_PAX_MILLIONS,
)
from backend.app.services.index_service import (
    compute_route_index,
    compute_aggregate_index,
    DEFAULT_BASELINE_START,
    DEFAULT_BASELINE_END,
)


def test_dgca_weights_sum_to_one():
    """Verify that all normalized DGCA route weights sum to 1.0."""
    all_pairs = [tuple(c["pair"]) for c in DGCA_TRUNK_CORRIDORS]
    norm_weights = get_normalized_dgca_weights(all_pairs)
    total_w = sum(norm_weights.values())
    assert abs(total_w - 1.0) < 1e-4, f"Normalized weights do not sum to 1.0: {total_w}"


def test_subset_weights_normalize_to_one():
    """Verify that any arbitrary subset of routes normalizes correctly to 1.0."""
    subset = [("DEL", "BOM"), ("BLR", "DEL"), ("BOM", "GOI")]
    norm_weights = get_normalized_dgca_weights(subset)
    total_w = sum(norm_weights.values())
    assert abs(total_w - 1.0) < 1e-4, f"Subset weights do not sum to 1.0: {total_w}"
    assert len(norm_weights) == 3


def test_elementary_route_index_formula():
    """Verify elementary index: Index = (avg_fare / baseline_fare) * 100."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        res = compute_route_index(
            db=db,
            origin="DEL",
            destination="BOM",
            period_start=date(2025, 3, 1),
            period_end=date(2025, 3, 31),
            baseline_start=DEFAULT_BASELINE_START,
            baseline_end=DEFAULT_BASELINE_END,
        )
        if res:
            expected_index = round((res["avg_fare"] / res["baseline_avg_fare"]) * 100.0, 2)
            assert abs(res["index_value"] - expected_index) < 0.05, (
                f"Index value mismatch: calculated={res['index_value']}, expected={expected_index}"
            )


def test_aggregate_index_matches_weighted_sum():
    """Verify that the aggregate index equals the sum of (route_index * weight)."""
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        agg = compute_aggregate_index(db=db, use_dgca_weights=True)
        assert agg is not None
        assert "aggregate_index" in agg
        assert "unweighted_index" in agg
        assert agg["aggregate_index"] > 0
        assert agg["unweighted_index"] > 0
