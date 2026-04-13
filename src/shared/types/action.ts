export type ActionType = "rightsizing" | "idle_shutdown" | "commitment_purchase" | "create_ticket" | "notify_owner";
export type ActionStatus = "started" | "approval_pending" | "approved" | "blocked" | "completed" | "failed";
export type ApprovalStatus = "pending" | "approved" | "denied" | "expired";

export interface ApprovalRequest {
  approval_request_id: string;
  recommendation_id: string;
  action_type: ActionType;
  approver_role: string;
  dual_approval_required: boolean;
  status: ApprovalStatus;
  approval_token?: string;
  expires_at: string;
  created_at: string;
}

export interface ActionRecord {
  action_id: string;
  action_type: ActionType;
  recommendation_id: string;
  approval_request_id: string;
  actor: string;
  actor_role: string;
  result: "success" | "failed" | "blocked";
  executed_at: string;
  step_functions_execution_arn?: string;
}
