"""Dashboard metrics route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.metrics import MetricsOut
from app.services import metrics as metrics_service

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("", response_model=MetricsOut)
def get_metrics(
    db: Session = Depends(get_db),
) -> MetricsOut:
    """Compute and return dashboard metrics."""
    data = metrics_service.compute_metrics(db)
    return MetricsOut(**data)
