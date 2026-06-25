from sqlalchemy.orm import Session

from app.models.merchant import Merchant


def get_all(db: Session) -> list[Merchant]:
    """Return all merchants ordered by name."""
    return db.query(Merchant).order_by(Merchant.name).all()


def get_by_id(db: Session, merchant_id: str) -> Merchant | None:
    """Return a single merchant by primary key, or None."""
    return db.query(Merchant).filter(Merchant.id == merchant_id).first()
