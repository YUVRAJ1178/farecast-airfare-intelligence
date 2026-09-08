"""ML Fare Prediction routes."""
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.app.schemas import PredictionRequest, PredictionResponse

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def predict_fare(request: PredictionRequest):
    """
    Predict airfare using the trained ML model.

    Returns predicted fare with confidence bounds.
    Requires a trained model (run: python ml/train.py).
    """
    from ml.predict import get_predictor

    predictor = get_predictor()

    if not predictor.is_ready:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ML model not available",
                "action": "Run: python ml/train.py to train the model first",
            },
        )

    try:
        result = predictor.predict(
            airline=request.airline,
            origin=request.origin,
            destination=request.destination,
            cabin_class=request.cabin_class,
            stops=request.stops,
            days_left=request.days_left,
            duration_minutes=request.duration_minutes,
            departure_hour=request.departure_hour,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return PredictionResponse(
        predicted_fare=result.predicted_fare,
        lower_bound=result.lower_bound,
        upper_bound=result.upper_bound,
        confidence=result.confidence,
        model_name=result.model_name,
        r2_score=result.r2_score,
        mae=result.mae,
        note=result.note,
        lookup_method=result.lookup_method,
        recommendation=result.recommendation,
        request=request,
    )


@router.get("/")
async def prediction_info():
    """Check ML model availability and return model metadata."""
    from ml.predict import get_predictor
    predictor = get_predictor()
    return {
        "model_ready": predictor.is_ready,
        "model_name": predictor._model_name,
        "r2_score": predictor._r2,
        "rf_blend_available": predictor._rf_pipeline is not None,
        "pricing_engine": {
            "type": "hybrid",
            "components": [
                "Calibrated route-level base fares (historical medians)",
                "Yield-management booking curve (days_left → multiplier)",
                "Time-of-day demand premium",
                "Airline price-positioning index",
                "Cabin-class multiplier",
                "Random Forest route calibration (25-30% blend)",
            ],
            "booking_curve": {
                "1_day_out": "×1.80 last-minute premium",
                "3_days_out": "×1.60",
                "7_days_out": "×1.25",
                "21_days_out": "×1.00 reference",
                "30_days_out": "×0.92–0.95 early-bird discount",
            },
        },
        "note": (
            "Fare prediction uses a calibrated yield-management engine. "
            "Prices reflect booking lead time, time-of-day, cabin class, and airline. "
            "Not a booking guarantee — actual fares may vary."
        ),
    }
