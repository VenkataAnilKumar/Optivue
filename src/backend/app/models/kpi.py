"""Pydantic v2 models for KPI snapshots."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class KPISnapshot(BaseModel):
    """Weekly/monthly KPI snapshot for the leadership dashboard."""

    period: str  # e.g. "2024-W42" or "2024-10"
    acceptance_rate: float = Field(ge=0.0, le=1.0, description="Recommendations accepted / total")
    completion_rate: float = Field(ge=0.0, le=1.0, description="Recommendations completed / accepted")
    action_safety_violations: int = Field(ge=0, description="Must always be 0")
    anomaly_triage_time_reduction_pct: Optional[float] = None
    p95_query_latency_ms: Optional[float] = None
    total_identified_savings: Optional[float] = None
    total_realized_savings: Optional[float] = None
    created_at: str
    demo_mode: bool = False


class UnitEconomics(BaseModel):
    """Unit economics metrics for the leadership dashboard."""

    cpau: Optional[float] = Field(None, description="Cloud cost per monthly active user")
    cpt: Optional[float] = Field(None, description="Cloud cost per transaction")
    cps: Optional[dict[str, float]] = Field(None, description="Cloud cost per service/product")
    period: str
    data_freshness_timestamp: str
