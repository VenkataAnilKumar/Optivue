"""Pydantic v2 model for cost anomaly data."""
from __future__ import annotations

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

SeverityLevel = Literal["critical", "high", "medium", "low"]


class AnomalyRootCause(BaseModel):
    service: Optional[str] = None
    region: Optional[str] = None
    usage_type: Optional[str] = None
    linked_account: Optional[str] = None


class Anomaly(BaseModel):
    """A cost anomaly with explanation."""

    anomaly_id: str
    start_time: str
    end_time: Optional[str] = None
    impact_amount: Annotated[float, Field(ge=0.0)]
    severity: SeverityLevel
    root_cause_summary: str
    likely_drivers: list[str] = Field(default_factory=list)
    likely_owner: Optional[str] = None
    root_causes: list[AnomalyRootCause] = Field(default_factory=list)
    data_freshness_timestamp: str
