"""
Airfare Intelligence Platform — Scheduler Endpoints
SIH Problem Statement 26056 — Requirement 12: Automated Pipeline Controls
"""

from fastapi import APIRouter
from backend.app.services.scheduler_service import scheduler

router = APIRouter()


@router.get("/status", tags=["Scheduler"])
async def get_scheduler_status():
    """
    Get current background scheduler status, next run times,
    and history of automated pipeline executions.
    """
    return scheduler.get_status()


@router.post("/trigger", tags=["Scheduler"])
async def trigger_pipeline():
    """
    Trigger an immediate on-demand execution of the automated
    collection, index calculation, and anomaly detection pipeline.
    """
    result = await scheduler.execute_pipeline(job_type="ON_DEMAND")
    return {
        "message": "Pipeline execution completed successfully",
        "result": result,
    }
