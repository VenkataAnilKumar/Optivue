export const DEFAULT_CONFIDENCE_THRESHOLD = 0.70;

export const PRIORITY_WEIGHTS = {
  savings: 0.35,
  confidence: 0.20,
  effort: 0.20,
  risk: 0.15,
  strategicAlignment: 0.10,
} as const;

export const EFFORT_NORMALIZED: Record<string, number> = {
  low: 0.2,
  medium: 0.5,
  high: 0.9,
};

export const RISK_NORMALIZED: Record<string, number> = {
  low: 0.1,
  medium: 0.5,
  high: 0.9,
};

export const DEFAULT_STRATEGIC_ALIGNMENT = 0.5;

export const PRIORITY_TIER_THRESHOLDS = {
  P1: 0.70,
  P2: 0.40,
  P3: 0.0,
} as const;

export const APPROVAL_TOKEN_TTL_HOURS = 4;
export const DEMO_FIXTURE_BASE = "fixtures";
