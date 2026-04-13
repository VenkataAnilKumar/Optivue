# Optivue — GitHub Copilot Build Prompts (Phase by Phase)

## How to Use
1. Open GitHub Copilot Chat (`Ctrl+Shift+I`) or Copilot Workspace.
2. Copy the prompt for the current phase exactly as written.
3. Copilot reads `.github/copilot-instructions.md` automatically for full project context.
4. Run one phase prompt at a time. Complete all exit criteria before moving to the next.
5. After each phase, update `docs/04-delivery/02-sprint-plan.md` with completed items.

## Repo Structure Reference
All source code lives under `src/` with four packages:
- `src/frontend/`    — Next.js 15 + TypeScript + Tailwind
- `src/backend/`     — Python 3.12 + FastAPI on Lambda
- `src/infra/`       — AWS CDK (TypeScript)
- `src/shared/`      — Cross-package types and constants

Adapter grouping under `src/backend/adapters/`:
- `cost/`         — Cost Analysis Agent tools
- `optimization/` — Optimization Agent tools
- `governance/`   — Governance Agent tools
- `actions/`      — Action execution (Jira, Slack)

Full structure: `docs/03-design/07-repo-structure.md`

---

## Phase 0 — Foundation and Scope (Week 1)

```
@workspace

I am starting Phase 0 of the Optivue project.

Context:
- All documentation is complete in docs/ (01-discovery through 05-portfolio).
- Repo structure is defined in docs/03-design/07-repo-structure.md.
- All source code lives under src/ with four packages: frontend, backend, infra, shared.
- Tech stack: Next.js 15 + TypeScript (src/frontend), Python 3.12 + FastAPI on Lambda
  (src/backend), AWS CDK TypeScript (src/infra), GitHub Actions CI/CD.
- Key references:
    docs/03-design/01-architecture-overview.md
    docs/03-design/06-code-reference.md
    docs/03-design/07-repo-structure.md
    docs/02-definition/01-prd-lite.md

Phase 0 goal: Scaffold the full src/ directory structure, initialize all packages,
and set up CI/CD before writing any business logic.

Tasks:
1. Scaffold src/infra/ CDK project:
   - src/infra/cdk.json, src/infra/tsconfig.json
   - src/infra/package.json (aws-cdk-lib@2.145.0, constructs@10.3.0, typescript@5.4.5)
   - src/infra/bin/app.ts — registers all 6 stacks (empty implementations) in dependency order:
     FoundationStack → DataStack → AgentStack → ApiStack → WorkflowStack + FrontendStack
   - src/infra/lib/stacks/ — 6 empty stack files
   - src/infra/lib/constructs/ — 4 empty construct files

2. Scaffold src/backend/ FastAPI project:
   - src/backend/requirements.txt and src/backend/requirements-dev.txt
     (exact versions from docs/03-design/06-code-reference.md Section 3)
   - src/backend/app/main.py — FastAPI app + Mangum handler + /health endpoint only
   - src/backend/app/config.py — Pydantic Settings with all env vars from code reference
   - src/backend/app/routers/__init__.py, models/__init__.py, services/__init__.py
   - src/backend/adapters/ grouped subdirs: cost/, optimization/, governance/, actions/
     each with __init__.py only
   - src/backend/Makefile with targets: run, test, lint

3. Scaffold src/frontend/ Next.js project:
   - src/frontend/package.json (all dependencies from docs/03-design/06-code-reference.md Section 3)
   - src/frontend/next.config.ts, tailwind.config.ts, tsconfig.json
   - src/frontend/app/layout.tsx — root layout skeleton
   - src/frontend/app/page.tsx — role-aware redirect skeleton
   - src/frontend/lib/api.ts, auth.ts, types.ts, utils.ts — empty with TODOs

4. Scaffold src/shared/:
   - src/shared/types/ — recommendation.ts, anomaly.ts, cost.ts, action.ts (interfaces only)
   - src/shared/constants/roles.ts — COGNITO_GROUPS, ROLE_PERMISSIONS constants
   - src/shared/constants/config.ts — DEFAULT_CONFIDENCE_THRESHOLD=0.70, PRIORITY_WEIGHTS

5. Create CI/CD workflows:
   - .github/workflows/ci.yml — 3 jobs:
       backend: ruff check src/backend/ → mypy src/backend/app → pytest src/backend/tests/unit/
       frontend: eslint → tsc --noEmit → vitest run
       infra: tsc --noEmit → cdk synth --app "npx ts-node src/infra/bin/app.ts"
   - .github/workflows/deploy.yml — deploy on merge to main:
       cdk deploy --all --require-approval never --app "npx ts-node src/infra/bin/app.ts"
   - .github/workflows/eval.yml — weekly schedule (Monday 06:00 UTC):
       python src/backend/tests/eval/run_eval.py

6. Root config files:
   - .env.example — all backend env vars with comments, no values
   - src/frontend/.env.local.example — all frontend env vars with comments
   - .gitignore — covers .venv, node_modules, .env, cdk.out, __pycache__, .next, *.pyc
   - CHANGELOG.md — empty v0.1.0 placeholder

Exit criteria:
- cd src/infra && npx cdk synth runs without errors.
- cd src/backend && uvicorn app.main:app --reload starts and GET /health returns 200.
- cd src/frontend && npm run dev starts without errors.
- All 3 CI workflow YAML files are syntactically valid.
- No business logic implemented — scaffold only.
```

---

## Phase 1 — Core Platform Setup (Weeks 2–3)

```
@workspace

Phase 0 complete. src/ scaffold, tooling, and CI skeleton are in place.
Now starting Phase 1: provision the secure AWS cloud foundation via CDK.

Context:
- All CDK code lives in src/infra/.
- CDK stack design and construct patterns: docs/03-design/06-code-reference.md Section 5.
- DynamoDB table schema, GSIs, and access patterns: docs/03-design/04-database-schema.md.
- Security rules from .github/copilot-instructions.md:
    IAM least privilege on every Lambda and CDK resource.
    All secrets in Secrets Manager — never hardcoded.
    KMS encryption at rest for S3 and DynamoDB.
    Cognito RBAC with 4 groups: finops-analyst, engineering-manager, finance, leadership.

Tasks:
1. Implement src/infra/lib/constructs/cognito-pool.ts:
   - Cognito User Pool with email sign-in, password policy, no self-registration.
   - 4 user groups: finops-analyst, engineering-manager, finance, leadership.
   - App Client: no client secret (SPA), auth flows: USER_PASSWORD_AUTH + REFRESH_TOKEN.
   - Export userPoolId and clientId as stack outputs.

2. Implement src/infra/lib/stacks/foundation-stack.ts:
   - Use CognitoPool construct from above.
   - Secrets Manager placeholders (empty secret values) for:
       finops/jira-api-token
       finops/slack-webhook-url
   - IAM execution roles for each Lambda type (cost adapter, optimization adapter,
     governance adapter, action adapter, FastAPI backend) — least privilege per role.
   - Export all role ARNs.

3. Implement src/infra/lib/stacks/data-stack.ts:
   - S3 bucket: finops-cost-exports
       versioning on, KMS AWS managed encryption, block all public access.
   - S3 bucket: finops-athena-results
       KMS encryption, block public access, lifecycle rule: delete objects after 30 days.
   - AWS Glue Database: finops_cost_db.
   - Athena WorkGroup: primary — output location = s3://finops-athena-results/query-results/.

4. Implement src/infra/lib/constructs/dynamo-tables.ts:
   - All 4 tables with exact schema from docs/03-design/04-database-schema.md:
       finops-recommendations — pk/sk, GSI: by-owner-status-index, by-priority-created-index, TTL
       finops-approvals — pk/sk, GSI: by-recommendation-index, by-status-index, TTL
       finops-action-history — pk/sk, GSI: by-recommendation-index, by-actor-date-index, NO TTL
       finops-kpi-metrics — pk/sk, no GSI
   - All tables: PAY_PER_REQUEST, AWS_MANAGED encryption, pointInTimeRecovery: true.

5. Implement src/infra/lib/stacks/api-stack.ts (skeleton):
   - HTTP API Gateway with Cognito JWT authorizer (userPoolId from foundation-stack).
   - Lambda function: finops-api-handler
       Python 3.12, handler: app.main.handler, code from src/backend/
       All env vars from .env.example wired as Lambda environment.
       512MB memory, 30s timeout.
   - CloudWatch log group: /aws/lambda/finops-api-handler (retention: 30 days).
   - GET /health route — no auth required.

6. Update src/infra/bin/app.ts to wire all stacks with correct props and dependency order.

7. Add docs/01-discovery/03-security-baseline-checklist.md confirming:
   - No plaintext credentials anywhere in src/.
   - All S3 buckets have block public access enabled.
   - All DynamoDB tables use KMS encryption.
   - All IAM roles follow least privilege (no *, no AdministratorAccess).
   - Cognito MFA: optional for MVP, mandatory in Post-MVP.

8. Write CDK assertion tests:
   - src/infra/test/foundation.test.ts — asserts Cognito pool has 4 groups, secrets exist.
   - src/infra/test/dynamo-tables.test.ts — asserts all 4 tables, GSIs, TTL, encryption.

Exit criteria:
- cdk deploy FinOpsFoundation FinOpsData succeeds in dev AWS account.
- All 4 DynamoDB tables visible in AWS console with correct GSI names.
- Cognito User Pool with 4 groups created and visible.
- GET /health via API Gateway returns 200 with valid Cognito JWT in Authorization header.
- CDK assertion tests pass in CI.
- security-baseline-checklist.md signed off.
```

---

## Phase 2 — Cost Intelligence MVP (Weeks 4–5)

```
@workspace

Phase 1 complete. AWS foundation (Cognito, API Gateway, Lambda, DynamoDB, S3, Glue, Athena)
is live in dev via CDK.
Now starting Phase 2: deliver the first user-visible value —
natural language cost queries and anomaly explanation.

Context:
- All adapters live in src/backend/adapters/ grouped by agent.
  Cost Analysis Agent adapters go in: src/backend/adapters/cost/
- Bedrock action group Lambda response contract (MUST follow exactly):
    { "messageVersion": "1.0", "response": { "actionGroup": event["actionGroup"],
      "function": event["function"], "functionResponse": { "responseBody":
      { "TEXT": { "body": json.dumps(result) } } } } }
  Parameters arrive as: {p["name"]: p["value"] for p in event.get("parameters", [])}
- Action group OpenAPI schemas: docs/03-design/03-action-group-schemas.md
- Bedrock agent instructions: docs/03-design/02-bedrock-agent-instructions.md
- Data contracts: docs/03-design/05-data-tool-contract.md
- DEMO_MODE=true must serve from fixtures/ — no live AWS calls.
- Fixture files: fixtures/sample-cost-data.json, fixtures/sample-anomaly.json

Tasks:
1. Implement src/backend/adapters/cost/cost_query.py:
   - Bedrock action group handler: get_cost_by_period.
   - Parameters: start_date, end_date, granularity (DAILY/MONTHLY), service, environment.
   - Builds Athena SQL query, polls for completion, returns normalized cost payload.
   - Response: total_cost, currency, period, top_drivers[], data_freshness_timestamp,
     data_completeness_pct. Add warning if data_completeness_pct < 95%.
   - DEMO_MODE: return fixtures/sample-cost-data.json result field directly.
   - Wrap in exact Bedrock action group response shape.

2. Implement src/backend/adapters/cost/anomaly_explain.py:
   - Bedrock action group handler: get_anomaly_explanation.
   - Parameters: anomaly_id (optional), lookback_days (default 7).
   - Calls boto3 ce.get_anomalies(). If no anomaly_id, returns highest impact in window.
   - Response: anomaly_id, start_time, end_time, impact_amount, severity,
     root_cause_summary, likely_drivers[], likely_owner, data_freshness_timestamp.
   - DEMO_MODE: return fixtures/sample-anomaly.json directly.

3. Implement src/backend/adapters/cost/budget_variance.py:
   - Bedrock action group handler: get_budget_variance.
   - Calls boto3 budgets.describe_budgets() and describe_budget_performance_history().
   - Response: budget_name, budgeted_amount, actual_amount, variance_amount,
     variance_pct, status (under_budget/on_track/at_risk/over_budget), narrative.

4. Implement src/backend/adapters/cost/forecast.py:
   - Bedrock action group handler: get_forecast.
   - Calls ce.get_cost_forecast() with MONTHLY granularity and 80% prediction interval.
   - Computes error_band_pct from (upper_bound - lower_bound) / mean_forecast.
   - If error_band_pct > 15% for monthly, sets forecast_reliability: "low".
   - Response: forecast_month, mean_forecast, lower_bound, upper_bound,
     confidence_interval_pct, error_band_pct, forecast_reliability, model_basis.

5. Implement src/backend/app/services/bedrock_service.py:
   - invoke_agent(session_id, prompt, context) — calls Bedrock Agents Runtime.
   - Streams response, collects completion text and traces.
   - DEMO_MODE: calls _load_fixture_response(prompt) which pattern-matches on prompt
     keywords (anomaly/recommendation/cost) and returns matching fixture.
   - Returns: { response, session_id, traces }.

6. Implement src/backend/app/routers/cost.py:
   - POST /cost/query — body: { prompt: str }, requires valid Cognito JWT.
   - Extracts user role from JWT, passes to bedrock_service.invoke_agent with context.
   - Returns agent response with data_freshness_timestamp.

7. Implement src/backend/app/routers/anomalies.py:
   - POST /anomalies/explain — body: { anomaly_id?: str, lookback_days?: int }.
   - Requires valid Cognito JWT. All 4 roles can access (read-only).

8. Add Bedrock agent to src/infra/lib/stacks/agent-stack.ts:
   - Create CfnAgent resource: finops-supervisor.
   - Agent instruction: paste content from docs/03-design/02-bedrock-agent-instructions.md
     Supervisor Agent instruction section.
   - Action group: cost-analysis-tools
     Functions: get_cost_by_period, get_anomaly_explanation, get_budget_variance, get_forecast.
     Each function wired to its Lambda adapter in src/backend/adapters/cost/.
   - Model: anthropic.claude-sonnet-4-6 (or latest available in region).
   - Enable traces: true.

9. Build src/frontend/app/chat/page.tsx:
   - Text input + submit button + scrollable message thread.
   - Each response shows: agent answer, data_freshness_timestamp badge, source label.
   - Loading spinner during agent invocation.
   - Error state with retry button.
   - Uses src/frontend/lib/api.ts api.cost.query().

10. Write pytest unit tests (moto @mock_aws):
    - src/backend/tests/unit/test_cost_flow.py:
        Test cost_query returns correct Bedrock response shape.
        Test data_completeness warning when < 95%.
        Test DEMO_MODE returns fixture data without AWS calls.
    - src/backend/tests/unit/test_anomaly.py:
        Test anomaly_explain returns all required fields.
        Test DEMO_MODE returns fixture data.

Exit criteria:
- POST /cost/query with prompt "Why did cost increase this week?"
  returns total_cost, top_drivers[], data_freshness_timestamp.
- POST /anomalies/explain returns impact_amount, likely_drivers[], likely_owner, severity.
- DEMO_MODE=true serves all fixtures without any live AWS API calls (verified by test).
- All new tests pass in CI.
```

---

## Phase 3 — Recommendations Engine (Weeks 6–7)

```
@workspace

Phase 2 complete. Cost queries and anomaly explanation work end-to-end.
Now starting Phase 3: generate, score, rank, and persist savings recommendations.

Context:
- Optimization Agent adapters go in: src/backend/adapters/optimization/
- Priority scoring formula (implement exactly — do not modify weights):
    priority_score = (min(savings/1000, 1.0) × 0.35)
                   + (confidence_score × 0.20)
                   + ((1 - effort_norm) × 0.20)     effort: low=0.2, medium=0.5, high=0.9
                   + ((1 - risk_norm) × 0.15)        risk:   low=0.1, medium=0.5, high=0.9
                   + (strategic_alignment × 0.10)    default: 0.5
  Priority tier: P1 ≥ 0.70 | P2 0.40–0.69 | P3 < 0.40
  needs_review: true when confidence_score < 0.70 (from src/shared/constants/config.ts)
- Recommendation contract: docs/03-design/05-data-tool-contract.md Section 3.
- DynamoDB schema for finops-recommendations: docs/03-design/04-database-schema.md Table 1.
  Keys: pk=REC#{recommendation_id}, sk=METADATA. History: sk=HISTORY#{iso8601_timestamp}.
- Fixture: fixtures/sample-recommendations.json.

Tasks:
1. Implement src/backend/adapters/optimization/recommendations.py:
   - Bedrock action group handler: get_recommendations.
   - Parameters: top_n (default 5), min_confidence (default 0.70), recommendation_type, environment.
   - Fetches from 3 sources in parallel (use concurrent.futures.ThreadPoolExecutor):
       Compute Optimizer: boto3 compute_optimizer.get_ec2_instance_recommendations()
       Trusted Advisor: boto3 support.describe_trusted_advisor_check_result() for cost checks
       Custom idle heuristic: Athena query — resources with 0 connections/invocations in 21 days
   - Merges and deduplicates by resource_id.
   - Applies priority_score formula to each recommendation.
   - Assigns priority_tier (P1/P2/P3).
   - Sets needs_review: true for confidence_score < settings.recommendation_confidence_threshold.
   - Sets suggested_owner: resource tag "owner" → tag "cost-center" → "unassigned".
   - Sets recommended_due_date: P1=today+14, P2=today+30, P3=today+60.
   - Returns top_n sorted by priority_score descending.
   - DEMO_MODE: return fixtures/sample-recommendations.json recommendations field.

2. Implement src/backend/adapters/optimization/commitments.py:
   - Bedrock action group handler: get_commitment_opportunities.
   - Calls ce.get_savings_plans_purchase_recommendation().
   - If utilization data < 30 days, sets minimum_baseline_met: false — do not return recommendation.
   - Returns savings_plans_recommendations[], utilization_baseline_days, minimum_baseline_met.

3. Implement src/backend/adapters/optimization/idle_resources.py:
   - Bedrock action group handler: get_idle_resources.
   - Runs Athena query for EC2/RDS/Lambda with 0 usage metrics over last 21 days.
   - Returns idle resource list with resource_id, service, region, estimated_monthly_savings.

4. Implement src/backend/app/services/dynamo_service.py (recommendations section):
   - save_recommendation(rec: Recommendation) → PutItem pk=REC#{id}, sk=METADATA.
   - get_recommendations_for_owner(owner, top_n, priority_tier):
       If owner provided → GSI by-owner-status-index (KeyCondition: owner=owner AND status=open).
       If priority_tier provided → GSI by-priority-created-index.
       Default → GSI by-priority-created-index with priority_tier=P1.
   - update_recommendation_status(id, new_status, actor, actor_role, comment):
       UpdateItem on METADATA to set status and updated_at.
       PutItem new HISTORY#{now} record (append-only).

5. Implement src/backend/app/models/recommendation.py:
   - Pydantic v2 models: Recommendation, RecommendationListResponse.
   - All fields from docs/03-design/05-data-tool-contract.md Section 3.
   - Validators: confidence_score 0.0–1.0, priority_score 0.0–1.0, priority_tier enum.

6. Implement src/backend/app/routers/recommendations.py:
   - GET /recommendations/ — role filtering:
       finops-analyst: all open recommendations, sorted by priority_score.
       engineering-manager: own team only via GSI1 (owner = user's team from JWT claim).
       finance, leadership: read-only, same as analyst view.
   - GET /recommendations/{id} — returns single recommendation with full evidence_refs.
   - POST /recommendations/{id}/approve — initiates governance flow (calls governance agent).
     Requires finops-analyst or engineering-manager role. Returns 403 otherwise.

7. Build src/frontend/app/(analyst)/recommendations/page.tsx:
   - Fetches recommendations via api.recommendations.list().
   - Groups by priority_tier: P1 section (red badge), P2 (amber), P3 (grey).
   - Filter bar: priority_tier, recommendation type, needs_review toggle.
   - Each card uses src/frontend/components/recommendations/RecommendationCard.tsx.

8. Build src/frontend/components/recommendations/RecommendationCard.tsx:
   - Shows: type badge, priority_tier badge, estimated_monthly_savings (formatted $),
     confidence_score (% bar), effort_level, risk_level, suggested_owner, rationale.
   - needs_review flag shows amber warning banner: "Needs manual review before routing".
   - "Approve" button opens ApprovalModal.

9. Build src/frontend/components/recommendations/ApprovalModal.tsx (step 1 — display only):
   - Shows: rationale, savings estimate, risk level, blast_radius (from risk eval), rollback_path.
   - "Confirm" button placeholder — full implementation in Phase 4.

10. Write pytest tests (src/backend/tests/unit/test_scoring.py):
    - Test priority_score formula: known inputs → expected output to 2 decimal places.
    - Test P1/P2/P3 boundary values: score=0.70 → P1, score=0.69 → P2, score=0.40 → P2,
      score=0.39 → P3.
    - Test needs_review=true when confidence=0.69, needs_review=false when confidence=0.70.
    - Test suggested_owner fallback chain: owner tag → cost-center tag → "unassigned".
    - Test DEMO_MODE returns fixture data without AWS calls.

Exit criteria:
- GET /recommendations/ returns top 5 recommendations with correct priority_score values.
- All recommendation fields present: priority_score, priority_tier, suggested_owner,
  recommended_due_date, needs_review, evidence_refs.
- PK pattern REC#{id} verified in DynamoDB.
- needs_review: true for confidence_score < 0.70 — confirmed by unit test.
- All new tests pass in CI.
```

---

## Phase 4 — Action Orchestration (Weeks 8–9)

```
@workspace

Phase 3 complete. Recommendations generated, scored, ranked, and persisted in DynamoDB.
Now starting Phase 4: the full insight-to-action workflow with approval gate,
Jira ticket creation, Slack notification, Step Functions orchestration, and audit trail.

Context:
- HARD REQUIREMENT: No action executes without a valid approval token. Return 403 if missing.
- Governance Agent adapters go in: src/backend/adapters/governance/
- Action adapters go in: src/backend/adapters/actions/
- Approval matrix from docs/01-discovery/02-open-questions-resolved.md Q2:
    prod + rightsizing → dual approval: engineering-manager + finops-analyst
    prod + idle_shutdown → single: engineering-manager
    prod + commitment_purchase → dual: finops-analyst + finance
    staging → single: finops-analyst
    dev low-risk → auto-approved
    dev high-risk → single: finops-analyst
- Step Functions state machine: ValidateApproval → CreateTicket → NotifyOwner
  → UpdateActionState | ApprovalBlocked (Fail).
- Approval tokens expire after 4 hours. Tokens stored in finops-approvals DynamoDB table.
- All Jira/Slack credentials from Secrets Manager — never hardcoded.
- Action history table is append-only — never update or delete records.

Tasks:
1. Implement src/backend/adapters/governance/risk_eval.py:
   - Bedrock action group handler: evaluate_action_risk.
   - Parameters: action_type, resource_id, environment.
   - Classifies risk using approval matrix above.
   - Returns: risk_level, blast_radius, rollback_path, approval_required,
     approver_role, dual_approval_required, policy_blocked, block_reason.
   - ALWAYS block (policy_blocked: true) for action_type=deletion AND environment=prod.

2. Implement src/backend/adapters/governance/approval.py:
   - Bedrock action group handler: request_approval.
   - Creates record in finops-approvals: pk=APPROVAL#{uuid}, sk=METADATA.
   - Fields: approval_request_id, recommendation_id, action_type, action_payload,
     approver_role, dual_approval_required, status=pending, expires_at=now+4h, ttl.
   - Returns: approval_request_id, status=pending, approval_token=None, expires_at.
   - Bedrock action group handler: get_approval_status.
   - Reads approval record. If expired → return status=expired, token=None.
   - If status=approved → return approval_token.

3. Implement src/backend/adapters/governance/tag_compliance.py:
   - Bedrock action group handler: check_tag_compliance.
   - Runs Athena query: resources missing required tags (product, environment, owner).
   - Returns: total_checked, compliant_count, non_compliant_count,
     missing_tag_keys (top 3), non_compliant_resources[].

4. Implement src/backend/adapters/actions/create_ticket.py:
   - Bedrock action group handler: create_ticket.
   - FIRST: validate approval_token parameter is present and not expired (DynamoDB lookup).
     If invalid or missing: return { "status": "blocked", "reason": "valid approval token required" }.
   - Reads Jira token from Secrets Manager key: settings.jira_secret_name.
   - POST to {JIRA_BASE_URL}/rest/api/3/issue with issuetype=Task, priority from priority_tier.
   - Returns: ticket_id, ticket_url, status=created, created_at.
   - On Jira API failure: log error, return status=failed — do NOT raise exception.

5. Implement src/backend/adapters/actions/notify_owner.py:
   - Bedrock action group handler: notify_owner.
   - Reads webhook from Secrets Manager key: settings.slack_secret_name.
   - For channel_type=slack: POST to webhook with Slack Block Kit message body.
     Include: recommendation summary, estimated_monthly_savings, ticket_url, owner name.
   - For channel_type=teams: POST to Teams webhook with Adaptive Card body.
   - Returns: delivery_status (sent/failed/queued), message_id, sent_at.
   - On webhook failure: log error, return delivery_status=failed — do NOT raise.

6. Implement src/infra/lib/stacks/workflow-stack.ts:
   - Step Functions state machine: finops-action-workflow.
   - States:
       ValidateApproval (LambdaInvoke — calls approval.get_approval_status adapter)
       Choice: $.approved == true?
         → YES: CreateTicket (LambdaInvoke) → NotifyOwner (LambdaInvoke)
                → UpdateActionState (DynamoPutItem to finops-action-history)
         → NO:  ApprovalBlocked (Fail state, error=ApprovalRequired)
   - CloudWatch log group: ALL level, include execution data.
   - X-Ray tracing enabled.
   - EventBridge rule: trigger on custom event source "finops.approval" with detail-type
     "ApprovalConfirmed".

7. Implement src/backend/app/routers/actions.py:
   - POST /actions/approve/{recommendation_id}:
       Requires finops-analyst or engineering-manager role (403 otherwise).
       Calls governance agent: evaluate_action_risk → request_approval.
       Stores approval request. Returns approval_request_id, status=pending.
   - POST /actions/execute/{recommendation_id}:
       Validates approval_token in request body. 403 if missing or expired.
       Starts Step Functions execution via boto3 sfn.start_execution().
       Writes initial record to finops-action-history: pk=ACTION#{uuid}, sk=METADATA.
       Returns: action_id, execution_arn, status=started.
   - GET /actions/status/{action_id}:
       Reads from finops-action-history. Returns current status.
       All 4 roles can read status.

8. Write audit log on every action state transition:
   - finops-action-history PutItem: pk=ACTION#{action_id}, sk=METADATA.
   - Fields: action_id, action_type, recommendation_id, approval_request_id,
     approval_token, actor, actor_role, payload, result, error_message,
     executed_at, step_functions_execution_arn.
   - This table is APPEND-ONLY — never call UpdateItem or DeleteItem on it.

9. Build src/frontend/components/recommendations/ApprovalModal.tsx (full implementation):
   - Step 1 — Risk review: shows blast_radius, rollback_path, risk_level badge.
   - Step 2 — Confirmation: checkbox "I understand this action is logged and irreversible".
     Approve button disabled until checkbox checked.
   - Step 3 — Execution: calls api.recommendations.approve() then api.actions.execute().
     Shows progress spinner → success state with Jira ticket URL and Slack confirmation.
     Shows error state with reason and retry button on failure.

10. Write integration tests (src/backend/tests/integration/test_action_flow.py, moto @mock_aws):
    - Test: POST /actions/execute without approval_token → 403 Forbidden.
    - Test: POST /actions/execute with expired approval token → 403 Forbidden.
    - Test: POST /actions/execute with valid token → Step Functions execution started.
    - Test: create_ticket with no approval_token → returns status=blocked.
    - Test: action history record written after successful execution.
    - Test: finance role POST /actions/approve → 403 Forbidden.
    - Test: prod deletion → risk_eval returns policy_blocked=true.

Exit criteria:
- POST /actions/execute with valid approval token → Jira ticket created + Slack sent end-to-end.
- finops-action-history has complete audit record for every execution.
- No action executes without valid, non-expired approval token (all 6 safety tests pass).
- action_safety_violations KPI = 0 confirmed by test run.
- All new tests pass in CI.
```

---

## Phase 5 — Evaluation, Safety, and Observability (Weeks 10–11)

```
@workspace

Phase 4 complete. Full insight-to-action workflow operational with approval gating and audit trail.
Now starting Phase 5: harden quality, enforce safety, add observability, and make demo-ready.

Context:
- Structured logging: every Lambda/router must use JSON logging with correlation_id.
  No print() statements anywhere.
- CloudWatch dashboard name: finops-agent-dashboard.
- KPI targets from .github/copilot-instructions.md:
    acceptance rate ≥ 30%, completion rate ≥ 20%, P95 ≤ 8s, safety violations = 0.
- Eval framework: https://github.com/awslabs/agent-evaluation
- DEMO_MODE=true: all 5 demo script flows must work entirely from fixtures/.
- All safety tests 100% pass. All P1 functional tests 100% pass.

Tasks:
1. Implement src/backend/app/services/auth_service.py (full):
   - Validates Cognito JWT: signature (JWKS from Cognito), expiry, issuer URL.
   - Extracts cognito:groups claim → maps to internal role string.
   - FastAPI dependency: get_current_user() → returns CurrentUser(sub, email, role, team).
   - FastAPI dependency: require_role(allowed_roles: list[str]) → raises 403 if not in list.
   - Returns 401 for missing/malformed token. Returns 403 for insufficient role.

2. Implement src/backend/app/middleware/logging.py:
   - Generates correlation_id (UUID) per request, stores in context var.
   - JSON log format for every request: correlation_id, user_sub, role, method, path,
     status_code, duration_ms.
   - JSON log for every Bedrock invocation: correlation_id, session_id, prompt_length,
     response_length, trace_count, duration_ms.
   - JSON log for every action: correlation_id, recommendation_id, action_type,
     approval_token_present, outcome.
   - No print() statements in any file under src/backend/.

3. Add CloudWatch resources to src/infra/lib/stacks/api-stack.ts:
   - Dashboard: finops-agent-dashboard with metric widgets:
       Lambda invocation count + error rate (last 24h).
       API Gateway P95 latency — target line at 8000ms.
       Alarm status widget for all alarms.
   - Alarms:
       LambdaErrorRate: errors/invocations > 5% for 2 consecutive minutes → SNS.
       ApiLatencyHigh: P95 > 8000ms for 3 consecutive minutes → SNS.
       SafetyViolation: custom metric finops/ActionSafetyViolations > 0 → SNS CRITICAL.
   - CloudWatch custom metric: finops/ActionSafetyViolations
     Emitted by actions router whenever action executes without valid approval token.

4. Create src/backend/tests/eval/prompts.json with 32 prompts:
   - cost_query (8): normal monthly query, filter by service, by environment, by account,
     future date (expect graceful error), missing date params, YoY comparison, top drivers only.
   - anomaly (6): explain latest anomaly, specific anomaly_id, no anomaly in window (empty result),
     anomaly with missing owner, high-severity only, lookback 30 days.
   - recommendations (8): top 5 all types, only rightsizing, only idle, P1 only,
     confidence below threshold (expect needs_review), filter by environment, filter by team,
     no recommendations found (expect empty list not error).
   - safety (10): action without approval token, action with expired token, prod deletion attempt,
     finance role approve action, leadership role approve action, double-approve same token,
     forge approval token format, action with missing recommendation_id, rate limit attempt,
     SQL injection attempt in anomaly_id.
   Each prompt: { "id", "category", "input", "expected_contains": [], "expected_not_contains": [],
                  "priority": "P1"|"P2" }

5. Implement src/backend/tests/eval/run_eval.py:
   - Loads prompts.json. For each prompt, calls bedrock_service.invoke_agent().
   - Checks response string against expected_contains (all must be present)
     and expected_not_contains (none must be present).
   - Reports per-category pass rate and total pass rate.
   - Prints summary table: category | total | passed | failed | pass_rate.
   - Exit code 1 if safety pass rate < 100% or any P1 category < 80%.
   - Writes results to src/backend/tests/eval/results_latest.json.

6. Implement src/backend/app/services/kpi_service.py:
   - compute_weekly_kpis(): queries finops-recommendations and finops-action-history tables.
   - Computes: recommendation_acceptance_rate, recommendation_completion_rate,
     anomaly_triage_time_minutes (from anomaly detected_at to owner_routed_at),
     identified_savings_usd, realized_savings_usd, false_positive_recommendation_rate,
     action_safety_violations (MUST be 0).
   - Writes each metric to finops-kpi-metrics:
     pk=KPI#{metric_type}, sk=PERIOD#{YYYY-MM} (monthly) or PERIOD#{YYYY-WW} (weekly).
   - EventBridge trigger: every Monday 06:00 UTC.

7. Full safety test sweep (src/backend/tests/integration/test_safety.py):
   - No action executes without approval token — test all 3 action endpoints.
   - Finance role: cannot POST /actions/approve or /actions/execute → 403.
   - Leadership role: cannot POST /actions/approve or /actions/execute → 403.
   - Prod deletion: risk_eval returns policy_blocked=true — verify no Step Functions started.
   - Expired approval token (set expires_at to past in DynamoDB): execute → 403.
   - All 5 tests must pass. Any failure blocks Phase 6.

8. Verify DEMO_MODE=true covers all 5 demo script flows:
   - cost query → fixtures/sample-cost-data.json
   - anomaly explanation → fixtures/sample-anomaly.json
   - recommendations → fixtures/sample-recommendations.json
   - approval + ticket + notify → mock responses (no live Jira/Slack calls)
   - KPI snapshot → hardcoded KPI values from seed fixture
   Add src/scripts/seed/seed-dynamo.py to load fixture recommendations into dev DynamoDB.

Exit criteria:
- CloudWatch dashboard deployed with all metric widgets visible.
- Eval suite: safety category 100% pass, cost/anomaly/rec/action categories ≥ 80% pass.
- API P95 latency ≤ 8s for cost query (verified from CloudWatch after 10 test requests).
- action_safety_violations = 0 across all safety tests.
- DEMO_MODE=true: all 5 demo flows work without live AWS API calls.
- All P1 tests pass 100% in CI.
```

---

## Phase 6 — Pilot and Portfolio Launch (Week 12)

```
@workspace

Phase 5 complete. Quality, safety, and observability are hardened and verified.
Now starting Phase 6: run the pilot, capture KPI outcomes, finalize all docs,
and package for portfolio and interviews.

Context:
- Demo script: docs/04-delivery/04-demo-script.md (5–7 minute flow).
- Portfolio docs: docs/05-portfolio/.
- DEMO_MODE=true + fixtures/ ensures demo reliability without live dependencies.
- MVP Definition of Done: docs/04-delivery/01-implementation-roadmap-phases.md (end of file).
- Interview checklist: Optivue-Document-Pack.md Interview-Ready Completion Checklist.

Tasks:
1. Run the full demo script end-to-end (docs/04-delivery/04-demo-script.md):
   - Step 1: POST /cost/query "Why did my AWS cost increase this week?"
     → returns total_cost delta, top_drivers[], data_freshness_timestamp.
   - Step 2: POST /anomalies/explain
     → returns root_cause_summary, likely_drivers[], likely_owner.
   - Step 3: GET /recommendations/?top_n=5
     → returns 5 ranked cards with P1/P2 tiers, savings, confidence.
   - Step 4: Approve recommendation → POST /actions/approve + POST /actions/execute
     → Jira ticket URL returned.
   - Step 5: Slack notification → delivery_status: sent.
   - Step 6: GET /kpi/snapshot → identified_savings_usd, acceptance_rate, safety_violations=0.
   - Confirm all 6 steps work with DEMO_MODE=true from fixtures/ as fallback.

2. Capture KPI outcome snapshot:
   - Update docs/04-delivery/02-sprint-plan.md KPI Tracking Table with actual values.
   - Metrics to record: acceptance_rate, completion_rate, anomaly_triage_time,
     P95 query latency, action_safety_violations, identified_savings_usd.

3. Finalize README.md:
   - Verify Quick Start instructions work on a clean machine (no prior setup).
   - Add ## Architecture section with reference to docs/images/architecture-mvp.md.
   - Add ## Sample Prompts section — 5 copy-paste demo queries.
   - Add ## Known Limitations section:
       Single AWS account only (no multi-account in MVP).
       No multi-cloud execution (analysis only via FOCUS mapping).
       No autonomous production deletion.
       Bedrock Knowledge Base deferred to Post-MVP Phase 7.
   - Add ## Future Improvements section:
       FOCUS multi-cloud ingestion (Expansion D).
       Shift-left FinOps CI checks (Expansion A).
       Commitment optimization automation (Expansion C).
       Advanced statistical forecasting (Expansion B).
       Executive scorecards and unit economics (Expansion E).

4. Final cross-reference validation — confirm all paths resolve:
   - All links in README.md → files exist in docs/ or src/.
   - All paths in .github/copilot-instructions.md → files exist.
   - All paths in Optivue-Document-Pack.md → files exist.
   - Run: find docs/ -name "*.md" | xargs grep -l "\.md" to surface broken links.

5. Verify Interview-Ready Completion Checklist (Optivue-Document-Pack.md):
   - All 17+ documents created and internally consistent.
   - Every FR (FR-1 to FR-7) mapped to at least one AWS doc or code sample.
   - Bedrock agent instructions defined (docs/03-design/02-bedrock-agent-instructions.md).
   - Action group schemas defined (docs/03-design/03-action-group-schemas.md).
   - DynamoDB schema and access patterns documented (docs/03-design/04-database-schema.md).
   - All 5 open questions answered (docs/01-discovery/02-open-questions-resolved.md).
   - Demo script rehearsed with fixture fallback confirmed.
   - KPI values captured for at least one pilot run.
   - README reproducible by recruiter in under 10 minutes.

6. Finalize CHANGELOG.md at repo root:
   - ## [0.1.0] — MVP Release
   - ### Added — list all 7 FRs delivered.
   - ### Known Limitations — 4 items from README.
   - ### Coming Next — 5 Post-MVP expansions.

Exit criteria — MVP Definition of Done (all must be true):
- User can ask cost questions and get grounded, sourced responses.
- User can view anomalies with root cause and owner routing.
- User can view ranked recommendations with P1/P2/P3 tiers.
- User can approve and trigger ticket + notification workflow.
- System tracks recommendation lifecycle and realized savings.
- action_safety_violations = 0 throughout pilot.
- All docs complete, all cross-references valid, README reproducible.
```

---

## Phase 7 — Post-MVP Expansion (Optional)

```
@workspace

MVP shipped and pilot-validated. Starting Post-MVP Phase 7.
Build each expansion independently behind a feature flag.
Feature flags live in src/backend/app/config.py and default to false.

FEATURE_SHIFT_LEFT_CHECKS=false
FEATURE_ADVANCED_FORECASTING=false
FEATURE_COMMITMENT_AUTOMATION=false
FEATURE_MULTI_CLOUD=false
FEATURE_EXECUTIVE_SCORECARDS=false

--- Expansion A — Shift-Left FinOps (CI/CD cost guardrails) ---
When FEATURE_SHIFT_LEFT_CHECKS=true:
- Create .github/workflows/finops-guardrail.yml (reusable workflow).
- Trigger: pull_request paths: ["src/infra/**"].
- Use Infracost CLI to estimate monthly cost delta from CDK diff.
- If delta > $500/month: add PR comment with breakdown + request finops-analyst review.
- If delta > $2000/month: block merge until finops-analyst adds "cost-approved" label.

--- Expansion B — Advanced Forecasting ---
When FEATURE_ADVANCED_FORECASTING=true:
- Implement src/backend/app/services/forecast_service.py:
    train(account_id, service): pulls 90 days of daily Athena cost data, fits Prophet model.
    predict(account_id, service, months): returns forecast with 80% confidence interval.
    error_band_pct = (upper-lower) / mean. If > 15% monthly → forecast_reliability: low.
- Replace Cost Explorer GetCostForecast call in src/backend/adapters/cost/forecast.py
  with forecast_service.predict() when feature flag enabled.
- Monthly target: error_band_pct ≤ 15%. Quarterly: ≤ 25%.

--- Expansion C — Commitment Optimization Automation ---
When FEATURE_COMMITMENT_AUTOMATION=true:
- EventBridge weekly schedule → Lambda: analyze On-Demand vs commitment utilization.
- Auto-generate commitment_purchase recommendation (type=commitment, dual-approval required:
  finops-analyst + finance per approval matrix).
- Track commitment_utilization_pct in finops-kpi-metrics weekly.
- Alert if utilization drops below 70% for 2 consecutive weeks.

--- Expansion D — Multi-Cloud Ingestion (FOCUS normalization) ---
When FEATURE_MULTI_CLOUD=true:
- Add src/backend/adapters/cost/azure_cost_query.py (Azure Cost Management REST API).
- Add src/backend/adapters/cost/gcp_cost_query.py (GCP Billing BigQuery export).
- Normalize all provider data to FOCUS schema
  (mapping defined in docs/03-design/05-data-tool-contract.md Section 7).
- Update all Athena queries in cost adapters to query FOCUS-normalized tables.
- Update recommendation engine resource identifiers to handle multi-cloud formats.
- Update src/shared/types/cost.ts with FOCUS-aligned fields.

--- Expansion E — Executive Scorecards and Unit Economics ---
When FEATURE_EXECUTIVE_SCORECARDS=true:
- Build src/frontend/app/(leadership)/snapshot/page.tsx (full implementation):
    CPAU chart: total cost / monthly active users (MAU).
    CPT chart: total cost / total transactions.
    CPS table: cost per product/service from product tag in CUR.
    Month-over-month trend arrows for each metric.
    (MAU and transaction counts fed from CloudWatch custom metrics or analytics source.)
- Add PDF export button using react-pdf.
- Add /kpi/unit-economics endpoint in src/backend/app/routers/kpi.py.
- Metrics reference: docs/01-discovery/02-open-questions-resolved.md Q3.
```

---

## Quick Reference — Phase Checklist

| Phase | Weeks | Key Files Created | Exit Gate |
|-------|-------|------------------|-----------|
| 0 — Scaffold | 1 | src/ structure, CI YAML, .gitignore | `cdk synth` + `/health` 200 |
| 1 — Platform | 2–3 | CDK stacks, DynamoDB, Cognito | 4 tables + Cognito live in AWS |
| 2 — Cost Intel | 4–5 | adapters/cost/*, routers/cost.py, chat UI | Cost query + anomaly E2E |
| 3 — Recs Engine | 6–7 | adapters/optimization/*, dynamo_service.py | Priority scores + P1/P2/P3 correct |
| 4 — Actions | 8–9 | adapters/governance/*, adapters/actions/*, workflow-stack.ts | Approval gate + audit trail |
| 5 — Eval + Obs | 10–11 | prompts.json, run_eval.py, CloudWatch, kpi_service.py | Safety 100%, P95 ≤ 8s |
| 6 — Pilot | 12 | README final, CHANGELOG, KPI snapshot | MVP Definition of Done |
| 7 — Post-MVP | Optional | Feature-flagged expansions | Per-expansion exit criteria |
| 8 — Deploy + Go-Live | Post-build | `.env.deploy`, CDK outputs, Secrets Manager, Bedrock alias, Cognito users | All 6 stacks live · `/health` 200 · Safety gate 403 · 0 violations |

