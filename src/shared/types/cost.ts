export interface CostDriver {
  service: string;
  cost: number;
  change_pct?: number;
}

export interface CostQueryResponse {
  total_cost: number;
  currency: string;
  period: string;
  top_drivers: CostDriver[];
  data_freshness_timestamp: string;
  data_completeness_pct: number;
}

export interface BudgetVarianceResponse {
  budget_name: string;
  budgeted_amount: number;
  actual_amount: number;
  variance_amount: number;
  variance_pct: number;
  status: "under_budget" | "on_track" | "at_risk" | "over_budget";
  narrative: string;
}

export interface ForecastResponse {
  forecast_month: string;
  mean_forecast: number;
  lower_bound: number;
  upper_bound: number;
  confidence_interval_pct: number;
  error_band_pct: number;
  forecast_reliability: "high" | "low";
  model_basis: string;
}
