"""Pydantic v2 model for cost anomaly data."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

SeverityLevel = Literal["critical", "high", "medium", "low"]


class AnomalyRootCause(BaseModel):
    service: str | None = None
    region: str | None = None
    usage_type: str | None = None
    linked_account: str | None = None


class Anomaly(BaseModel):
    """A cost anomaly with explanation."""

    anomaly_id: str
    start_time: str
    end_time: str | None = None
    impact_amount: Annotated[float, Field(ge=0.0)]
    severity: SeverityLevel
    root_cause_summary: str
    likely_drivers: list[str] = Field(default_factory=list)
    likely_owner: str | None = None
    root_causes: list[AnomalyRootCause] = Field(default_factory=list)
    data_freshness_timestamp: str
