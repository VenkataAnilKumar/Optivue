# Optivue — GitHub Copilot Workspace Instructions

## Product Identity
**Optivue** — An AWS-first, human-in-the-loop AI assistant that turns cloud cost data into actionable optimization workflows. It combines natural language analytics, agentic anomaly investigation, ranked savings recommendations, and safe action execution with approval gating.

## Stack and Services
| Layer | Technology |
|---|---|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS, deployed on AWS Amplify Hosting |
| Auth | Amazon Cognito (groups: `finops-analyst`, `engineering-manager`, `finance`, `leadership`) |
| API | FastAPI on AWS Lambda behind Amazon API Gateway |
| AI/Agent | Amazon Bedrock Agents — supervisor + 3 specialist agents |
| Data | AWS CUR/Data Exports → S3 + AWS Glue + Amazon Athena |
| State | Amazon DynamoDB (4 tables — see schema) |
| Workflow | AWS Step Functions + Amazon EventBridge |
| Notifications | Jira API, Slack/Teams webhooks |
| IaC | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions |
| Observability | Amazon CloudWatch + Bedrock traces |
| Runtime | Python 3.12 (backend/agents), TypeScript (CDK/frontend) |

## Agent Architecture
```
finops-supervisor
├── cost-analysis-agent       # spend queries, anomaly explanation, budget variance, forecasting
├── optimization-agent        # recommendations, rightsizing, idle detection, commitments
└── governance-agent          # tag compliance, budget policy, approval gating, risk eval
```
Tool adapters invoke: Cost Explorer, Cost Anomaly Detection, Compute Optimizer, Budgets, Trusted Advisor, Jira, Slack/Teams.

## DynamoDB Tables
- `finops-recommendations` — recommendation lifecycle and payload
- `finops-approvals` — approval token records
- `finops-action-history` — completed/failed action audit trail
- `finops-kpi-metrics` — weekly/monthly KPI snapshots

## Key Design Rules (enforce in all code)
1. **Human-in-the-loop is non-negotiable.** No write action (ticket creation, notification, resource mutation) without an explicit approval token in session context.
2. **No production deletions.** The system must never autonomously delete production resources. Return `policy_blocked` if attempted.
3. **Grounded responses only.** Agents must base all cost figures on tool-returned data. Never infer or hallucinate dollar amounts.
4. **IAM least privilege.** Every Lambda/CDK resource gets the minimum permissions needed.
5. **Role-based output filtering.** `finance` and `leadership` roles are read-only; account numbers are redacted for roles below `finops-analyst`.
6. **Confidence scoring is mandatory.** Every recommendation must include a confidence score and rationale with evidence refs. Auto-route only if `confidence_score >= 0.70`; below that, set `needs_review: true`.
7. **Data freshness.** Every cost response must include a `data_freshness_timestamp` indicating data recency.
8. **Graceful degradation.** Handle external API failures without crashing the primary query path.
9. **Dual-approval for production.** All prod mutations require two approvers: `engineering-manager` + `finops-analyst`. Staging requires single approval. Dev low-risk actions are auto-approved.
10. **Demo mode fallback.** When `DEMO_MODE=true`, all service calls must return data from `fixtures/` instead of calling live AWS APIs.

## Personas and Permissions
| Cognito Group | Capabilities |
|---|---|
| `finops-analyst` | Full read, triage, ticket creation, notifications, single approvals |
| `engineering-manager` | Read own-team recommendations, acknowledge/complete actions, single approvals |
| `finance` | Read-only: reports, forecasts, budget variance |
| `leadership` | Read-only: executive dashboard, KPI snapshots |

## Functional Requirements (MVP)
- FR-1: Natural-language spend queries by period/service/tag
- FR-2: Anomaly explanation with top drivers
- FR-3: Ranked savings recommendations with confidence and estimated impact
- FR-4: Approve recommendation → create Jira ticket
- FR-5: Owner notification via Slack/Teams
- FR-6: All mutating actions require explicit confirmation
- FR-7: Monthly spend forecast with confidence interval and variance narrative

## Performance Targets
- P95 ≤ 8s for standard analytics queries
- P95 ≤ 20s for deep anomaly investigation workflows

## Recommendation Priority Scoring
Every recommendation must compute `priority_score` using this formula:

```
priority_score = (estimated_savings_normalized × 0.35)
              + (confidence_score × 0.20)
              + ((1 - effort_normalized) × 0.20)
              + ((1 - risk_normalized) × 0.15)
              + (strategic_alignment_score × 0.10)

estimated_savings_normalized = min(estimated_monthly_savings / 1000, 1.0)
effort_normalized:  low=0.2  medium=0.5  high=0.9
risk_normalized:    low=0.1  medium=0.5  high=0.9
strategic_alignment_score: default 0.5
```

Priority tier: `P1` ≥ 0.70 | `P2` 0.40–0.69 | `P3` < 0.40

## Approval Matrix
| Environment | Action Type | Approvers | Mode |
|-------------|-------------|-----------|------|
| prod | rightsizing | engineering-manager + finops-analyst | dual |
| prod | idle_shutdown | engineering-manager | single |
| prod | commitment_purchase | finops-analyst + finance | dual |
| staging | any | finops-analyst | single |
| dev | low-risk | — | auto-approved |
| dev | high-risk | finops-analyst | single |

Approval tokens expire after 4 hours. Dual-approval requires both roles to confirm independently.

## Forecast Error Bands
- Monthly forecast: acceptable error ≤ ±15%
- Quarterly forecast: acceptable error ≤ ±25%
- If `error_band_pct` exceeds target, set `forecast_reliability: low` in response.

## Unit Economics Metrics (Mandatory for Leadership Dashboard)
| Metric | Definition |
|--------|-----------|
| CPAU | Total cloud cost / Monthly active users |
| CPT | Total cloud cost / Total transactions processed |
| CPS | Cloud cost per product/service (derived from `product` tag in CUR) |

## KPIs
| Metric | Target |
|--------|--------|
| Recommendation acceptance rate | ≥ 30% in pilot |
| Recommendation completion rate | ≥ 20% in first cycle |
| Anomaly triage time reduction | ≥ 15% |
| Standard query P95 latency | ≤ 8s |
| Deep anomaly investigation P95 | ≤ 20s |
| **Action safety violations** | **0 — hard requirement** |
| Identified and realized savings | Tracked weekly/monthly |

## Project Layout
```
docs/
  01-discovery/    # product brief, resolved questions
  02-definition/   # PRD Lite, user stories
  03-design/       # architecture, agent instructions, schemas, contracts
  04-delivery/     # roadmap, sprint plan, test plan, demo script
  05-portfolio/    # hiring assets
fixtures/          # sample JSON data for testing
```

## Coding Conventions
- Python: `ruff` for linting, type hints on all public functions, descriptive docstrings on agent tool handlers
- TypeScript/CDK: strict mode, named exports, resource IDs use `kebab-case`
- DynamoDB key prefixes: `REC#` (recommendations), `APPROVAL#` (approvals), `ACTION#` (action history), `KPI#` (metrics), `HISTORY#` (status trail), `CONFIG#` (runtime config)
- Lambda handlers follow: validate input → call service → return normalized response
- All secrets via AWS Secrets Manager; no plaintext credentials anywhere
- Infrastructure deployed via CDK; do not use console-only changes

## Bedrock Action Group Lambda Contract
All Lambda adapters for Bedrock action groups must follow this exact response shape:
```python
return {
    "messageVersion": "1.0",
    "response": {
        "actionGroup": event["actionGroup"],
        "function": event["function"],
        "functionResponse": {
            "responseBody": {
                "TEXT": {
                    "body": json.dumps(result)   # result is a plain dict
                }
            }
        }
    }
}
```
Parameters arrive as: `{p["name"]: p["value"] for p in event.get("parameters", [])}`

## Step Functions Action Workflow
Action execution always runs through this state machine — never call Jira/Slack directly from the API layer:
```
ValidateApproval → [approved?]
  ├── YES → CreateTicket → NotifyOwner → UpdateActionState
  └── NO  → ApprovalBlocked (Fail state)
```

## Test Tooling
| Layer | Tool | Usage |
|-------|------|-------|
| Python unit/integration | `pytest` + `moto` | Mock all AWS services with `@mock_aws` |
| Python linting | `ruff` | Run in CI on every PR |
| Python type checking | `mypy` | Run in CI on every PR |
| Frontend unit | `vitest` + `@testing-library/react` | Component and hook tests |
| Frontend linting | `eslint` | Run in CI on every PR |
| Agent evaluation | `agent-evaluation` (awslabs) | Prompt quality and safety tests |

## Out of Scope (MVP)
- Autonomous production deletion
- Broad enterprise policy engine
- Knowledge Base / RAG (deferred to Post-MVP Phase 7)
- Advanced statistical forecasting (uses Cost Explorer forecast API in MVP)

## Key References
- [Architecture Overview](docs/03-design/01-architecture-overview.md)
- [Agent Instructions](docs/03-design/02-bedrock-agent-instructions.md)
- [Action Group Schemas](docs/03-design/03-action-group-schemas.md)
- [Database Schema](docs/03-design/04-database-schema.md)
- [PRD Lite](docs/02-definition/01-prd-lite.md)
- [Implementation Roadmap](docs/04-delivery/01-implementation-roadmap-phases.md)

