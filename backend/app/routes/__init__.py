"""
Airfare Intelligence Platform — API Route Handlers

Exports all route modules for the FastAPI application:
- health: System health checks and status
- fares: Airfare search, statistics, and observations
- index: Prototype Airfare Price Index calculations
- prediction: ML fare prediction and route advice
- anomalies: Price surge and drop anomaly detection
- dashboard: Aggregate statistics for frontend dashboard
- live: Amadeus live sync and data source status
"""

from backend.app.routes import (
    anomalies,
    backtesting,
    dashboard,
    fares,
    health,
    index,
    live,
    prediction,
)

__all__ = [
    "anomalies",
    "backtesting",
    "dashboard",
    "fares",
    "health",
    "index",
    "live",
    "prediction",
]
