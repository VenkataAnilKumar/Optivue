from typing import Any

from fastapi import APIRouter, Depends

from app.services.auth_service import UserContext, require_role
from app.services.kpi_service import get_latest_kpis

router = APIRouter()


@router.get("/")
async def list_kpis(
    user: UserContext = Depends(require_role(["finops-analyst", "leadership", "finance"])),
) -> dict[str, Any]:
    """Return latest weekly KPI snapshot for the dashboard."""
    kpis = await get_latest_kpis()
    return {"kpis": kpis}
