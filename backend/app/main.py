from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.database import Base, engine
from app.models import (  # noqa: F401
    AuditLog, Fee, Merchant, MerchantApiKey, NotifyQueue,
    Reconciliation, RefreshToken, Transaction, User,
)
from app.routes import (
    api_keys, audit, auth, webhook, transactions, merchants,
    fees, reconciliation, metrics, ops, users, qr,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="1Hub Control Portal",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: JWT auth middleware hook

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(api_keys.router)
app.include_router(audit.router)
app.include_router(webhook.router)
app.include_router(transactions.router)
app.include_router(merchants.router)
app.include_router(fees.router)
app.include_router(reconciliation.router)
app.include_router(metrics.router)
app.include_router(ops.router)
app.include_router(qr.router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENV}
