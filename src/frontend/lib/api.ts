import { getAccessToken } from './auth';
import type {
  CostQueryResponse,
  ForecastResponse,
  Anomaly,
  Recommendation,
  RecommendationStatus,
  KPISnapshot,
  ApprovalResponse,
  ActionExecuteResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getAccessToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// -----------------------------------------------------------------------------
// Cost
// -----------------------------------------------------------------------------

export function getCostQuery(period = 'last_month'): Promise<CostQueryResponse> {
  return apiFetch(`/cost/query?period=${encodeURIComponent(period)}`);
}

export function getForecast(monthsAhead = 1): Promise<ForecastResponse> {
  return apiFetch(`/cost/forecast?months_ahead=${monthsAhead}`);
}

export function getBudgetVariance() {
  return apiFetch('/cost/budget-variance');
}

// -----------------------------------------------------------------------------
// Anomalies
// -----------------------------------------------------------------------------

export function listAnomalies(): Promise<{ anomalies: Anomaly[] }> {
  return apiFetch('/anomalies/');
}

export function getAnomalyExplanation(anomalyId: string): Promise<Anomaly> {
  return apiFetch(`/anomalies/explain/${encodeURIComponent(anomalyId)}`);
}

// -----------------------------------------------------------------------------
// Recommendations
// -----------------------------------------------------------------------------

export function listRecommendations(params?: {
  owner?: string;
  status?: RecommendationStatus;
}): Promise<{ recommendations: Recommendation[]; total: number }> {
  const qs = new URLSearchParams();
  if (params?.owner) qs.set('owner', params.owner);
  if (params?.status) qs.set('status', params.status);
  return apiFetch(`/recommendations/?${qs.toString()}`);
}

export function updateRecommendationStatus(
  id: string,
  status: RecommendationStatus,
  actor?: string,
  reason?: string,
): Promise<Recommendation> {
  return apiFetch(`/recommendations/${encodeURIComponent(id)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, actor, reason }),
  });
}

// -----------------------------------------------------------------------------
// Actions
// -----------------------------------------------------------------------------

export function requestApproval(
  recommendationId: string,
  actionType: string,
  requester: string,
  environment = 'prod',
): Promise<ApprovalResponse> {
  return apiFetch('/actions/request-approval', {
    method: 'POST',
    body: JSON.stringify({
      recommendation_id: recommendationId,
      action_type: actionType,
      requester,
      environment,
    }),
  });
}

export function getApprovalStatus(approvalRequestId: string): Promise<ApprovalResponse> {
  return apiFetch(`/actions/approval-status/${encodeURIComponent(approvalRequestId)}`);
}

export function executeAction(
  recommendationId: string,
  approvalToken: string,
  actionType: string,
  title?: string,
  description?: string,
): Promise<ActionExecuteResponse> {
  return apiFetch('/actions/execute', {
    method: 'POST',
    body: JSON.stringify({
      recommendation_id: recommendationId,
      approval_token: approvalToken,
      action_type: actionType,
      title,
      description,
    }),
  });
}

// -----------------------------------------------------------------------------
// KPI
// -----------------------------------------------------------------------------

export function getKPIs(): Promise<{ kpis: KPISnapshot[] }> {
  return apiFetch('/kpi/');
}
