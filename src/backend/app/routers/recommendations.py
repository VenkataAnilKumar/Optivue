from fastapi import APIRouter, Depends, Query
from app.services.auth_service import get_current_user, UserContext
from app.services.dynamo_service import get_recommendations_for_owner, update_recommendation_status
from app.services.bedrock_service import invoke_agent

router = APIRouter()


@router.get("/")
async def list_recommendations(
    owner: str | None = Query(default=None),
    priority_tier: str | None = Query(default=None),
    user: UserContext = Depends(get_current_user),
) -> dict:
    """List ranked savings recommendations (FR-3)."""
    if owner or priority_tier:
        items = await get_recommendations_for_owner(owner=owner or user.sub, priority_tier=priority_tier)
        return {"recommendations": items, "total": len(items), "data_freshness_timestamp": ""}

    prompt = "Generate ranked savings recommendations with confidence scores and estimated monthly savings."
    response = await invoke_agent(
        session_id=f"recs-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role},
    )
    return response


@router.patch("/{recommendation_id}/status")
async def update_status(
    recommendation_id: str,
    status: str,
    user: UserContext = Depends(get_current_user),
) -> dict:
    """Update recommendation lifecycle status."""
    await update_recommendation_status(recommendation_id=recommendation_id, status=status, actor=user.sub)
    return {"recommendation_id": recommendation_id, "status": status, "updated_by": user.sub}
