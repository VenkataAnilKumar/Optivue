import logging

from fastapi import FastAPI
try:
    from mangum import Mangum
except ModuleNotFoundError:  # pragma: no cover - local test fallback
    Mangum = None  # type: ignore[assignment]

from app.middleware.logging import RequestLoggingMiddleware
from app.routers import actions, anomalies, cost, kpi, recommendations

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinOps Agent API",
    description="AWS-first cloud cost optimization platform",
    version="0.1.0",
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(cost.router, prefix="/cost", tags=["cost"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["anomalies"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(actions.router, prefix="/actions", tags=["actions"])
app.include_router(kpi.router, prefix="/kpi", tags=["kpi"])


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Health check endpoint — no auth required."""
    return {"status": "healthy", "version": "0.1.0"}


handler = Mangum(app, lifespan="off") if Mangum else None
