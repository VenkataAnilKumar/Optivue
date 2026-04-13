"""Pydantic v2 model for a FinOps recommendation."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

PriorityTier = Literal["P1", "P2", "P3"]
ActionType = Literal["rightsizing", "idle_shutdown", "commitment_purchase", "scaling", "other"]
EffortLevel = Literal["low", "medium", "high"]
RiskLevel = Literal["low", "medium", "high"]
RecommendationStatus = Literal["new", "pending_approval", "approved", "in_progress", "completed", "dismissed"]


class Recommendation(BaseModel):
    """A ranked cloud cost optimization recommendation."""

    id: str
    resource_type: str
    resource_id: str
    account_id: str | None = None
    region: str | None = None
    action_type: ActionType
    title: str = ""
    description: str = ""
    estimated_monthly_savings: Annotated[float, Field(ge=0.0)]
    confidence_score: Annotated[float, Field(ge=0.0, le=1.0)]
    effort: EffortLevel = "medium"
    risk: RiskLevel = "medium"
    priority_score: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0
    priority_tier: PriorityTier = "P3"
    strategic_alignment_score: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    needs_review: bool = False
    status: RecommendationStatus = "new"
    owner: str | None = None
    data_freshness_timestamp: str = ""
    created_at: str = ""
    updated_at: str = ""

    @field_validator("confidence_score", "priority_score", "strategic_alignment_score")
    @classmethod
    def _score_in_range(cls, v: float) -> float:  # noqa: N805
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return round(v, 4)


class RecommendationStatusUpdate(BaseModel):
    status: RecommendationStatus
    actor: str | None = None
    reason: str | None = None
