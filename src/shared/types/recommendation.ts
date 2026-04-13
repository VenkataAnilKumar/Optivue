export type PriorityTier = "P1" | "P2" | "P3";
export type RecommendationType = "rightsizing" | "idle" | "commitment" | "tagging";
export type EffortLevel = "low" | "medium" | "high";
export type RiskLevel = "low" | "medium" | "high";
export type RecommendationStatus = "open" | "acknowledged" | "in_progress" | "completed" | "dismissed";

export interface Recommendation {
  recommendation_id: string;
  type: RecommendationType;
  estimated_monthly_savings: number;
  confidence_score: number;
  priority_score: number;
  priority_tier: PriorityTier;
  effort_level: EffortLevel;
  risk_level: RiskLevel;
  rationale: string;
  evidence_refs: string[];
  suggested_owner: string;
  recommended_due_date: string;
  status: RecommendationStatus;
  needs_review: boolean;
  environment: string;
  account_id?: string;
  resource_id?: string;
  service?: string;
  region?: string;
  created_at: string;
  updated_at: string;
}

export interface RecommendationListResponse {
  recommendations: Recommendation[];
  total: number;
  data_freshness_timestamp: string;
}
