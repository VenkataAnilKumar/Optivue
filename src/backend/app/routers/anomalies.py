from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user, UserContext
from app.services.bedrock_service import invoke_agent

router = APIRouter()


@router.get("/explain/{anomaly_id}")
async def explain_anomaly(
    anomaly_id: str,
    user: UserContext = Depends(get_current_user),
) -> dict:
    """Anomaly explanation with top cost drivers (FR-2)."""
    prompt = f"Explain the cost anomaly with ID {anomaly_id}. Identify the top drivers and likely owner."
    response = await invoke_agent(
        session_id=f"anomaly-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role, "anomaly_id": anomaly_id},
    )
    return response


@router.get("/")
async def list_anomalies(
    user: UserContext = Depends(get_current_user),
) -> dict:
    """List recent cost anomalies."""
    prompt = "List recent cost anomalies with severity, impact amount, and likely owners."
    response = await invoke_agent(
        session_id=f"anomalies-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role},
    )
    return response
