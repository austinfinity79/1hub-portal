"""Reconciliation listing routes."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import reconciliation_repo
from app.schemas.reconciliation import ReconciliationOut

router = APIRouter(prefix="/api/reconciliation", tags=["Reconciliation"])


@router.get("", response_model=list[ReconciliationOut])
def list_reconciliation(
    recon_date: str,
    db: Session = Depends(get_db),
) -> list[ReconciliationOut]:
    """List reconciliation records for a given date (dd/mm/yyyy)."""
    dt = datetime.strptime(recon_date, "%d/%m/%Y").date()
    items = reconciliation_repo.list_by_date(db, dt)
    return [ReconciliationOut.model_validate(r) for r in items]
