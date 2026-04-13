from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from adapters.actions.create_ticket import create_jira_ticket
from adapters.actions.notify_owner import send_owner_notification
from adapters.governance.approval import get_approval_status, request_approval, validate_approval_token
from app.services.auth_service import UserContext, get_current_user

router = APIRouter()


class ApprovalRequestBody(BaseModel):
    recommendation_id: str
    action_type: str
    environment: str = "prod"


class ApproveBody(BaseModel):
    approval_request_id: str
    recommendation_id: str
    action_type: str
    approval_token: str


@router.post("/request-approval")
async def request_action_approval(
    body: ApprovalRequestBody,
    user: UserContext = Depends(get_current_user),
) -> dict[str, Any]:
    """Create an approval request for a recommendation action (FR-6)."""
    result = await request_approval(
        recommendation_id=body.recommendation_id,
        action_type=body.action_type,
        requester=user.sub,
        environment=body.environment,
    )
    return result


@router.get("/approval-status/{approval_request_id}")
async def check_approval_status(
    approval_request_id: str,
    user: UserContext = Depends(get_current_user),
) -> dict[str, Any]:
    """Check the status of a pending approval."""
    result = await get_approval_status(approval_request_id=approval_request_id)
    return result


@router.post("/execute")
async def execute_action(
    body: ApproveBody,
    user: UserContext = Depends(get_current_user),
) -> dict[str, Any]:
    """Execute an approved action — human-in-the-loop enforcement (FR-4, FR-6)."""
    # Validate approval token FIRST — non-negotiable safety gate
    is_valid = await validate_approval_token(
        approval_token=body.approval_token,
        recommendation_id=body.recommendation_id,
        actor_role=user.role,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="valid approval_token required before executing any action",
        )

    if body.action_type == "create_ticket":
        result = await create_jira_ticket(
            recommendation_id=body.recommendation_id,
            approval_token=body.approval_token,
            actor=user.sub,
        )
    elif body.action_type == "notify_owner":
        result = await send_owner_notification(
            recommendation_id=body.recommendation_id,
            ticket_url=None,
            actor=user.sub,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action_type: {body.action_type}",
        )

    return result
