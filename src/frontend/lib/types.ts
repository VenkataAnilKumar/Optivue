// Shared TypeScript types aligned with the backend Pydantic models

export type PriorityTier = 'P1' | 'P2' | 'P3';
export type ActionType = 'rightsizing' | 'idle_shutdown' | 'commitment_purchase' | 'scaling' | 'other';
export type EffortLevel = 'low' | 'medium' | 'high';
export type RiskLevel = 'low' | 'medium' | 'high';
export type RecommendationStatus = 'new' | 'pending_approval' | 'approved' | 'in_progress' | 'completed' | 'dismissed';
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export interface Recommendation {
  id: string;
  resource_type: string;
  resource_id: string;
  account_id?: string;
  region?: string;
  action_type: ActionType;
  title: string;
  description: string;
  estimated_monthly_savings: number;
  confidence_score: number;
  effort: EffortLevel;
  risk: RiskLevel;
  priority_score: number;
  priority_tier: PriorityTier;
  needs_review: boolean;
  status: RecommendationStatus;
  owner?: string;
  data_freshness_timestamp: string;
  created_at?: string;
}

export interface CostDriver {
  service: string;
  cost: number;
  pct_of_total?: number;
}

export interface CostQueryResponse {
  total_cost: number;
  currency: string;
  period: string;
  top_drivers: CostDriver[];
  data_freshness_timestamp: string;
  data_completeness_pct: number;
  demo_mode?: boolean;
}

export interface ForecastResponse {
  forecast_month: string;
  mean_forecast: number;
  lower_bound: number;
  upper_bound: number;
  confidence_interval_pct: number;
  error_band_pct: number;
  forecast_reliability: 'high' | 'low';
  model_basis: string;
  data_freshness_timestamp: string;
  demo_mode?: boolean;
}

export interface Anomaly {
  anomaly_id: string;
  start_time: string;
  end_time?: string;
  impact_amount: number;
  severity: SeverityLevel;
  root_cause_summary: string;
  likely_drivers: string[];
  likely_owner?: string;
  data_freshness_timestamp: string;
}

export interface KPISnapshot {
  period: string;
  acceptance_rate: number;
  completion_rate: number;
  action_safety_violations: number;
  anomaly_triage_time_reduction_pct?: number;
  p95_query_latency_ms?: number;
  total_identified_savings?: number;
  total_realized_savings?: number;
  created_at: string;
  demo_mode?: boolean;
}

export interface ApprovalResponse {
  approval_request_id: string;
  approval_token: string;
  status: ApprovalStatus;
  required_approvers: string[];
  expires_at: string;
}

export interface ActionExecuteResponse {
  recommendation_id: string;
  ticket_id: string;
  ticket_url: string;
  notification_sent: boolean;
  status: string;
}

export interface UserContext {
  sub: string;
  email: string;
  role: string;
  groups: string[];
}
