"""Pydantic v2 models for approval and action orchestration."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ApprovalStatus = Literal["pending", "approved", "rejected", "expired"]


class ApprovalRequest(BaseModel):
    recommendation_id: str
    action_type: str
    requester: str
    environment: str = "prod"


class ApprovalResponse(BaseModel):
    approval_request_id: str
    approval_token: str
    status: ApprovalStatus
    required_approvers: list[str]
    expires_at: str


class ActionExecuteRequest(BaseModel):
    recommendation_id: str
    approval_token: str
    action_type: str
    title: str | None = None
    description: str | None = None


class ActionExecuteResponse(BaseModel):
    recommendation_id: str
    ticket_id: str
    ticket_url: str
    notification_sent: bool
    status: str = "completed"
