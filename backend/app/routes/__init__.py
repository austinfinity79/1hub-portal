"""Route module — exports all API routers for inclusion in the FastAPI app."""

from app.routes.api_keys import router as api_keys_router
from app.routes.audit import router as audit_router
from app.routes.auth import router as auth_router
from app.routes.fees import router as fees_router
from app.routes.merchants import router as merchants_router
from app.routes.metrics import router as metrics_router
from app.routes.ops import router as ops_router
from app.routes.reconciliation import router as reconciliation_router
from app.routes.transactions import router as transactions_router
from app.routes.users import router as users_router
from app.routes.webhook import router as webhook_router

all_routers = [
    webhook_router,
    transactions_router,
    merchants_router,
    fees_router,
    reconciliation_router,
    metrics_router,
    ops_router,
    auth_router,
    users_router,
    api_keys_router,
    audit_router,
]

__all__ = [
    "all_routers",
    "api_keys_router",
    "audit_router",
    "auth_router",
    "fees_router",
    "merchants_router",
    "metrics_router",
    "ops_router",
    "reconciliation_router",
    "transactions_router",
    "users_router",
    "webhook_router",
]
