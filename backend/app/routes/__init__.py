"""Route module — exports all API routers for inclusion in the FastAPI app."""

from app.routes.fees import router as fees_router
from app.routes.merchants import router as merchants_router
from app.routes.metrics import router as metrics_router
from app.routes.ops import router as ops_router
from app.routes.reconciliation import router as reconciliation_router
from app.routes.transactions import router as transactions_router
from app.routes.webhook import router as webhook_router

all_routers = [
    webhook_router,
    transactions_router,
    merchants_router,
    fees_router,
    reconciliation_router,
    metrics_router,
    ops_router,
]

__all__ = [
    "all_routers",
    "fees_router",
    "merchants_router",
    "metrics_router",
    "ops_router",
    "reconciliation_router",
    "transactions_router",
    "webhook_router",
]
