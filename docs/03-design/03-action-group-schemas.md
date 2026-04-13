# Bedrock Action Group — OpenAPI Schemas

## Overview
Each tool available to the Bedrock agents is defined as a Lambda-backed action group.
The schemas below are the OpenAPI 3.0 definitions that Bedrock uses to understand each function's inputs and outputs.

---

## Action Group 1: Cost Analysis Tools

### Function: get_cost_by_period

```yaml
openapi: "3.0.0"
info:
  title: "get_cost_by_period"
  version: "1.0"
paths:
  /get_cost_by_period:
    post:
      summary: "Query AWS cloud spend for a given period and scope"
      operationId: "get_cost_by_period"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - start_date
                - end_date
              properties:
                start_date:
                  type: string
                  format: date
                  description: "Start of query period in YYYY-MM-DD format"
                end_date:
                  type: string
                  format: date
                  description: "End of query period in YYYY-MM-DD format"
                account_id:
                  type: string
                  description: "Optional AWS account ID filter"
                service:
                  type: string
                  description: "Optional AWS service filter (e.g. AmazonEC2)"
                environment:
                  type: string
                  enum: [prod, staging, dev, all]
                  description: "Optional environment tag filter"
                granularity:
                  type: string
                  enum: [DAILY, MONTHLY]
                  default: MONTHLY
      responses:
        "200":
          description: "Cost query result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_cost:
                    type: number
                  currency:
                    type: string
                  period:
                    type: string
                  top_drivers:
                    type: array
                    items:
                      type: object
                      properties:
                        service:
                          type: string
                        cost:
                          type: number
                        percentage:
                          type: number
                  data_freshness_timestamp:
                    type: string
                    format: date-time
                  data_completeness_pct:
                    type: number
```

---

### Function: get_anomaly_explanation

```yaml
openapi: "3.0.0"
info:
  title: "get_anomaly_explanation"
  version: "1.0"
paths:
  /get_anomaly_explanation:
    post:
      summary: "Retrieve and explain a detected cost anomaly"
      operationId: "get_anomaly_explanation"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                anomaly_id:
                  type: string
                  description: "Optional specific anomaly ID. If omitted, returns highest severity anomaly in window."
                lookback_days:
                  type: integer
                  default: 7
                  description: "Number of days to look back for anomalies"
      responses:
        "200":
          description: "Anomaly explanation"
          content:
            application/json:
              schema:
                type: object
                properties:
                  anomaly_id:
                    type: string
                  start_time:
                    type: string
                    format: date-time
                  end_time:
                    type: string
                    format: date-time
                  impact_amount:
                    type: number
                  severity:
                    type: string
                    enum: [low, medium, high, critical]
                  root_cause_summary:
                    type: string
                  likely_drivers:
                    type: array
                    items:
                      type: string
                  likely_owner:
                    type: string
                  monitor_scope:
                    type: string
                  data_freshness_timestamp:
                    type: string
                    format: date-time
```

---

### Function: get_budget_variance

```yaml
openapi: "3.0.0"
info:
  title: "get_budget_variance"
  version: "1.0"
paths:
  /get_budget_variance:
    post:
      summary: "Compare actual spend against budget for a given scope"
      operationId: "get_budget_variance"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - period
              properties:
                period:
                  type: string
                  description: "Budget period in YYYY-MM format"
                account_id:
                  type: string
                cost_center:
                  type: string
      responses:
        "200":
          description: "Budget variance result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  budget_name:
                    type: string
                  budgeted_amount:
                    type: number
                  actual_amount:
                    type: number
                  variance_amount:
                    type: number
                  variance_pct:
                    type: number
                  status:
                    type: string
                    enum: [under_budget, on_track, at_risk, over_budget]
                  narrative:
                    type: string
```

---

### Function: get_forecast

```yaml
openapi: "3.0.0"
info:
  title: "get_forecast"
  version: "1.0"
paths:
  /get_forecast:
    post:
      summary: "Return monthly spend forecast with confidence interval"
      operationId: "get_forecast"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - forecast_month
              properties:
                forecast_month:
                  type: string
                  description: "Target forecast month in YYYY-MM format"
                account_id:
                  type: string
                service:
                  type: string
      responses:
        "200":
          description: "Forecast result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  forecast_month:
                    type: string
                  mean_forecast:
                    type: number
                  lower_bound:
                    type: number
                    description: "Lower bound at 80% confidence"
                  upper_bound:
                    type: number
                    description: "Upper bound at 80% confidence"
                  confidence_interval_pct:
                    type: number
                    default: 80
                  error_band_pct:
                    type: number
                    description: "Expected forecast error as percentage (target <= 15% monthly)"
                  model_basis:
                    type: string
                    description: "Data window used for forecast model"
```

---

## Action Group 2: Optimization Tools

### Function: get_recommendations

```yaml
openapi: "3.0.0"
info:
  title: "get_recommendations"
  version: "1.0"
paths:
  /get_recommendations:
    post:
      summary: "Return ranked savings recommendations from all optimization sources"
      operationId: "get_recommendations"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                top_n:
                  type: integer
                  default: 5
                  description: "Number of recommendations to return"
                min_confidence:
                  type: number
                  default: 0.70
                  description: "Minimum confidence score threshold"
                recommendation_type:
                  type: string
                  enum: [rightsizing, idle, commitment, tagging, all]
                  default: all
                environment:
                  type: string
                  enum: [prod, staging, dev, all]
                  default: all
      responses:
        "200":
          description: "Ranked recommendations list"
          content:
            application/json:
              schema:
                type: object
                properties:
                  recommendations:
                    type: array
                    items:
                      type: object
                      properties:
                        recommendation_id:
                          type: string
                        type:
                          type: string
                          enum: [rightsizing, idle, commitment, tagging]
                        estimated_monthly_savings:
                          type: number
                        confidence_score:
                          type: number
                        effort_level:
                          type: string
                          enum: [low, medium, high]
                        risk_level:
                          type: string
                          enum: [low, medium, high]
                        priority_score:
                          type: number
                          description: "Weighted composite score (0.00-1.00)"
                        priority_tier:
                          type: string
                          enum: [P1, P2, P3]
                        rationale:
                          type: string
                        evidence_refs:
                          type: array
                          items:
                            type: string
                        suggested_owner:
                          type: string
                        recommended_due_date:
                          type: string
                          format: date
                        needs_review:
                          type: boolean
                          description: "True if confidence is below threshold"
                  total_estimated_monthly_savings:
                    type: number
                  generated_at:
                    type: string
                    format: date-time
```

---

### Function: get_commitment_opportunities

```yaml
openapi: "3.0.0"
info:
  title: "get_commitment_opportunities"
  version: "1.0"
paths:
  /get_commitment_opportunities:
    post:
      summary: "Retrieve Savings Plans and Reserved Instance purchase recommendations"
      operationId: "get_commitment_opportunities"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                lookback_days:
                  type: integer
                  enum: [7, 14, 30, 60]
                  default: 30
                payment_option:
                  type: string
                  enum: [NO_UPFRONT, PARTIAL_UPFRONT, ALL_UPFRONT]
                  default: NO_UPFRONT
      responses:
        "200":
          description: "Commitment recommendations"
          content:
            application/json:
              schema:
                type: object
                properties:
                  savings_plans_recommendations:
                    type: array
                    items:
                      type: object
                      properties:
                        plan_type:
                          type: string
                        hourly_commitment:
                          type: number
                        estimated_monthly_savings:
                          type: number
                        estimated_coverage_pct:
                          type: number
                  utilization_baseline_days:
                    type: integer
                  minimum_baseline_met:
                    type: boolean
                    description: "False if utilization data < 30 days — recommendation blocked"
```

---

## Action Group 3: Action Execution Tools

### Function: create_ticket

```yaml
openapi: "3.0.0"
info:
  title: "create_ticket"
  version: "1.0"
paths:
  /create_ticket:
    post:
      summary: "Create a Jira ticket for an approved recommendation"
      operationId: "create_ticket"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - recommendation_id
                - owner
                - summary
                - approval_token
              properties:
                recommendation_id:
                  type: string
                owner:
                  type: string
                  description: "Jira assignee username or team handle"
                summary:
                  type: string
                  description: "Ticket title (max 255 chars)"
                description:
                  type: string
                  description: "Full ticket body with rationale and evidence"
                acceptance_criteria:
                  type: string
                priority:
                  type: string
                  enum: [P1, P2, P3]
                approval_token:
                  type: string
                  description: "Token from governance agent approval. Required. Action blocked without valid token."
      responses:
        "200":
          description: "Ticket created"
          content:
            application/json:
              schema:
                type: object
                properties:
                  ticket_id:
                    type: string
                  ticket_url:
                    type: string
                  status:
                    type: string
                    enum: [created, failed]
                  created_at:
                    type: string
                    format: date-time
```

---

### Function: notify_owner

```yaml
openapi: "3.0.0"
info:
  title: "notify_owner"
  version: "1.0"
paths:
  /notify_owner:
    post:
      summary: "Send owner notification via Slack or Microsoft Teams"
      operationId: "notify_owner"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - channel_type
                - owner
                - message
                - recommendation_id
              properties:
                channel_type:
                  type: string
                  enum: [slack, teams]
                owner:
                  type: string
                  description: "Slack username or Teams UPN"
                channel:
                  type: string
                  description: "Optional channel override (default: owner's DM)"
                message:
                  type: string
                  description: "Notification message body"
                recommendation_id:
                  type: string
                ticket_url:
                  type: string
                  description: "Jira ticket URL to include in notification"
      responses:
        "200":
          description: "Notification result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  delivery_status:
                    type: string
                    enum: [sent, failed, queued]
                  message_id:
                    type: string
                  sent_at:
                    type: string
                    format: date-time
```

---

## Action Group 4: Governance Tools

### Function: evaluate_action_risk

```yaml
openapi: "3.0.0"
info:
  title: "evaluate_action_risk"
  version: "1.0"
paths:
  /evaluate_action_risk:
    post:
      summary: "Classify the risk level of a proposed action"
      operationId: "evaluate_action_risk"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - action_type
                - resource_id
                - environment
              properties:
                action_type:
                  type: string
                  enum: [rightsizing, idle_shutdown, commitment_purchase, tag_update]
                resource_id:
                  type: string
                environment:
                  type: string
                  enum: [prod, staging, dev]
                estimated_impact:
                  type: string
      responses:
        "200":
          description: "Risk evaluation result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  risk_level:
                    type: string
                    enum: [low, medium, high, blocked]
                  blast_radius:
                    type: string
                  rollback_path:
                    type: string
                  approval_required:
                    type: boolean
                  approver_role:
                    type: string
                  policy_blocked:
                    type: boolean
                  block_reason:
                    type: string
```

---

### Function: request_approval

```yaml
openapi: "3.0.0"
info:
  title: "request_approval"
  version: "1.0"
paths:
  /request_approval:
    post:
      summary: "Issue an approval request for a proposed action"
      operationId: "request_approval"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - action_type
                - action_payload
                - approver_role
                - risk_level
              properties:
                action_type:
                  type: string
                action_payload:
                  type: object
                  description: "The full action parameters that will be executed upon approval"
                approver_role:
                  type: string
                  enum: [finops-analyst, engineering-manager, finance]
                risk_level:
                  type: string
                  enum: [low, medium, high]
                blast_radius:
                  type: string
                dual_approval_required:
                  type: boolean
                  default: false
                expiry_hours:
                  type: integer
                  default: 4
      responses:
        "200":
          description: "Approval request created"
          content:
            application/json:
              schema:
                type: object
                properties:
                  approval_request_id:
                    type: string
                  status:
                    type: string
                    enum: [pending, approved, denied, expired]
                  approval_token:
                    type: string
                    description: "Token returned only when status is approved"
                  approval_timestamp:
                    type: string
                    format: date-time
                  approver:
                    type: string
                  reason:
                    type: string
                  expires_at:
                    type: string
                    format: date-time
```

---

## Lambda Function Mapping

| Function | Lambda Name | IAM Permissions Required |
|----------|-------------|--------------------------|
| get_cost_by_period | `finops-agent-cost-query` | athena:StartQueryExecution, s3:GetObject |
| get_anomaly_explanation | `finops-agent-anomaly` | ce:GetAnomalies, ce:GetAnomalyMonitors |
| get_budget_variance | `finops-agent-budget` | budgets:ViewBudget |
| get_forecast | `finops-agent-forecast` | ce:GetCostForecast |
| get_recommendations | `finops-agent-recommendations` | compute-optimizer:GetEC2InstanceRecommendations, trustedadvisor:GetChecks |
| get_commitment_opportunities | `finops-agent-commitments` | ce:GetSavingsPlansPurchaseRecommendation |
| create_ticket | `finops-agent-jira` | secretsmanager:GetSecretValue (Jira token) |
| notify_owner | `finops-agent-notify` | secretsmanager:GetSecretValue (Slack/Teams webhook) |
| evaluate_action_risk | `finops-agent-risk-eval` | dynamodb:GetItem (policy table) |
| request_approval | `finops-agent-approval` | dynamodb:PutItem, dynamodb:GetItem, sns:Publish |

---

## References
- Bedrock Agents function calling: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-create.html
- Bedrock samples — function calling: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling
