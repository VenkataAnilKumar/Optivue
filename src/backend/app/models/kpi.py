"""Pydantic v2 models for KPI snapshots."""
from __future__ import annotations

from pydantic import BaseModel, Field


class KPISnapshot(BaseModel):
    """Weekly/monthly KPI snapshot for the leadership dashboard."""

    period: str  # e.g. "2024-W42" or "2024-10"
    acceptance_rate: float = Field(ge=0.0, le=1.0, description="Recommendations accepted / total")
    completion_rate: float = Field(ge=0.0, le=1.0, description="Recommendations completed / accepted")
    action_safety_violations: int = Field(ge=0, description="Must always be 0")
    anomaly_triage_time_reduction_pct: float | None = None
    p95_query_latency_ms: float | None = None
    total_identified_savings: float | None = None
    total_realized_savings: float | None = None
    created_at: str
    demo_mode: bool = False


class UnitEconomics(BaseModel):
    """Unit economics metrics for the leadership dashboard."""

    cpau: float | None = Field(None, description="Cloud cost per monthly active user")
    cpt: float | None = Field(None, description="Cloud cost per transaction")
    cps: dict[str, float] | None = Field(None, description="Cloud cost per service/product")
    period: str
    data_freshness_timestamp: str
