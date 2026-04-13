"""Pydantic v2 models for cost queries and forecasts."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class CostDriver(BaseModel):
    service: str
    cost: Annotated[float, Field(ge=0.0)]
    pct_of_total: float | None = None


class CostQueryResponse(BaseModel):
    total_cost: Annotated[float, Field(ge=0.0)]
    currency: str = "USD"
    period: str
    top_drivers: list[CostDriver] = Field(default_factory=list)
    data_freshness_timestamp: str
    data_completeness_pct: float = 100.0
    demo_mode: bool = False


class ForecastResponse(BaseModel):
    forecast_month: str
    mean_forecast: Annotated[float, Field(ge=0.0)]
    lower_bound: Annotated[float, Field(ge=0.0)]
    upper_bound: Annotated[float, Field(ge=0.0)]
    confidence_interval_pct: int = 80
    error_band_pct: Annotated[float, Field(ge=0.0)]
    forecast_reliability: Literal["high", "low"]
    model_basis: str = "AWS Cost Explorer forecast API"
    data_freshness_timestamp: str
    demo_mode: bool = False


class BudgetVarianceEntry(BaseModel):
    budget_name: str
    budgeted_amount: float
    actual_amount: float
    variance_amount: float
    variance_pct: float
    status: Literal["under_budget", "on_track", "at_risk", "over_budget"]


class BudgetVarianceResponse(BaseModel):
    budgets: list[BudgetVarianceEntry] = Field(default_factory=list)
    data_freshness_timestamp: str
    demo_mode: bool = False
