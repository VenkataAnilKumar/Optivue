from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user, UserContext
from app.services.bedrock_service import invoke_agent

router = APIRouter()


@router.get("/query")
async def get_cost_by_period(
    period: str = "last_month",
    user: UserContext = Depends(get_current_user),
) -> dict:
    """Natural-language cost query for a given period (FR-1)."""
    prompt = f"What is the total cloud spend for the period: {period}? Break down by top services."
    response = await invoke_agent(
        session_id=f"cost-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role, "period": period},
    )
    return response


@router.get("/forecast")
async def get_forecast(
    months_ahead: int = 1,
    user: UserContext = Depends(get_current_user),
) -> dict:
    """Monthly spend forecast with confidence interval (FR-7)."""
    prompt = f"Provide a {months_ahead}-month spend forecast with confidence interval and variance narrative."
    response = await invoke_agent(
        session_id=f"forecast-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role, "months_ahead": months_ahead},
    )
    return response


@router.get("/budget-variance")
async def get_budget_variance(
    user: UserContext = Depends(get_current_user),
) -> dict:
    """Budget vs actual variance analysis."""
    prompt = "Provide budget vs actual variance analysis for all active budgets."
    response = await invoke_agent(
        session_id=f"budget-{user.sub}",
        prompt=prompt,
        context={"user_role": user.role},
    )
    return response
