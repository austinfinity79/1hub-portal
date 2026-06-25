"""Operations routes for manual demo triggers."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.napas.mock import MockNapasClient
from app.services import notify_router
from app.services import reconciliation as reconciliation_service

router = APIRouter(prefix="/api", tags=["Operations"])


@router.post("/notify/batch/run")
def trigger_batch_notify(
    db: Session = Depends(get_db),
) -> dict:
    """Run batch notification manually (demo; production uses cron)."""
    result = notify_router.run_batch(db)
    return result


@router.post("/reconciliation/run")
def trigger_reconciliation(
    recon_date: str = Query(..., description="Reconciliation date dd/mm/yyyy"),
    db: Session = Depends(get_db),
) -> dict:
    """Run EOD reconciliation manually (demo)."""
    dt = datetime.strptime(recon_date, "%d/%m/%Y").date()
    napas_client = MockNapasClient()
    result = reconciliation_service.run_reconciliation(db, napas_client, dt)
    return result
