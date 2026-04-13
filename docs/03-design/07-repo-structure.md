# Optivue — Repository Structure

## Overview
Monorepo with a single `src/` root containing four packages:
`frontend`, `backend`, `infra`, and `shared`.
Each package is independently deployable and testable.

---

## Full Structure

```
finops-agent/
│
├── src/                                    # All application source code
│   │
│   ├── frontend/                           # Next.js 15 + TypeScript + Tailwind
│   │   ├── app/                            # Next.js App Router
│   │   │   ├── layout.tsx                  # Root layout (Amplify auth provider)
│   │   │   ├── page.tsx                    # Role-aware home redirect
│   │   │   ├── (analyst)/                  # FinOps analyst route group
│   │   │   │   ├── dashboard/page.tsx      # Anomaly queue + savings backlog
│   │   │   │   ├── anomalies/page.tsx      # Anomaly triage view
│   │   │   │   └── recommendations/page.tsx # Ranked recommendations list
│   │   │   ├── (engineering)/              # Engineering manager route group
│   │   │   │   └── inbox/page.tsx          # Action inbox + ticket status
│   │   │   ├── (leadership)/               # Leadership route group
│   │   │   │   └── snapshot/page.tsx       # KPI + unit economics dashboard
│   │   │   ├── chat/page.tsx               # Natural language query interface
│   │   │   └── api/agent/route.ts          # Next.js API route → FastAPI proxy
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx           # Message thread + input
│   │   │   │   └── MessageBubble.tsx       # Single message with source badge
│   │   │   ├── recommendations/
│   │   │   │   ├── RecommendationCard.tsx  # P1/P2/P3 card with savings + confidence
│   │   │   │   └── ApprovalModal.tsx       # 3-step approval confirmation dialog
│   │   │   ├── anomalies/
│   │   │   │   └── AnomalyCard.tsx         # Anomaly with root cause + owner
│   │   │   ├── kpi/
│   │   │   │   └── KPIDashboard.tsx        # Acceptance rate, savings, latency charts
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx              # Top nav with role badge + sign out
│   │   │   │   └── Sidebar.tsx             # Role-aware navigation links
│   │   │   └── ui/                         # Primitive design system components
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       └── Badge.tsx               # P1/P2/P3 + risk level badges
│   │   ├── lib/
│   │   │   ├── api.ts                      # Typed fetch wrappers for all endpoints
│   │   │   ├── auth.ts                     # Cognito Amplify helpers + getUserRole()
│   │   │   ├── types.ts                    # Frontend TypeScript types (imports shared/)
│   │   │   └── utils.ts                    # formatCurrency, formatDate, cn()
│   │   ├── public/                         # Static assets
│   │   ├── __tests__/
│   │   │   ├── ApprovalModal.test.tsx      # Vitest + Testing Library
│   │   │   └── RecommendationCard.test.tsx
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   ├── backend/                            # Python 3.12 + FastAPI on Lambda
│   │   ├── app/
│   │   │   ├── main.py                     # FastAPI app + Mangum handler + routers
│   │   │   ├── config.py                   # Pydantic Settings from env vars
│   │   │   ├── routers/
│   │   │   │   ├── cost.py                 # POST /cost/query
│   │   │   │   ├── anomalies.py            # GET  /anomalies/explain
│   │   │   │   ├── recommendations.py      # GET  /recommendations/, POST /approve
│   │   │   │   ├── actions.py              # POST /actions/execute, GET /status
│   │   │   │   └── kpi.py                  # GET  /kpi/snapshot
│   │   │   ├── services/
│   │   │   │   ├── bedrock_service.py      # invoke_agent() + demo mode fallback
│   │   │   │   ├── dynamo_service.py       # DynamoDB read/write + GSI queries
│   │   │   │   ├── auth_service.py         # JWT validation + role extraction
│   │   │   │   └── kpi_service.py          # Weekly KPI computation job
│   │   │   ├── models/
│   │   │   │   ├── cost.py                 # CostQueryResponse, CostDriver
│   │   │   │   ├── anomaly.py              # AnomalyEvent, AnomalyResponse
│   │   │   │   ├── recommendation.py       # Recommendation, RecommendationList
│   │   │   │   ├── action.py               # ApprovalRequest, ActionResult
│   │   │   │   └── kpi.py                  # KPISnapshot, KPIMetric
│   │   │   └── middleware/
│   │   │       ├── logging.py              # Structured JSON logging + correlation ID
│   │   │       └── auth.py                 # Cognito JWT middleware
│   │   ├── adapters/                       # Bedrock action group Lambda handlers
│   │   │   ├── cost/
│   │   │   │   ├── cost_query.py           # get_cost_by_period → Athena
│   │   │   │   ├── anomaly_explain.py      # get_anomaly_explanation → Cost Anomaly Detection
│   │   │   │   ├── budget_variance.py      # get_budget_variance → AWS Budgets
│   │   │   │   └── forecast.py             # get_forecast → Cost Explorer
│   │   │   ├── optimization/
│   │   │   │   ├── recommendations.py      # get_recommendations → Compute Optimizer + Trusted Advisor
│   │   │   │   ├── commitments.py          # get_commitment_opportunities → Savings Plans API
│   │   │   │   └── idle_resources.py       # get_idle_resources → Athena heuristic
│   │   │   ├── governance/
│   │   │   │   ├── risk_eval.py            # evaluate_action_risk → policy rules
│   │   │   │   ├── approval.py             # request_approval → DynamoDB
│   │   │   │   └── tag_compliance.py       # check_tag_compliance → Athena
│   │   │   └── actions/
│   │   │       ├── create_ticket.py        # create_ticket → Jira REST API v3
│   │   │       └── notify_owner.py         # notify_owner → Slack / Teams webhook
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   │   ├── test_recommendations.py # Priority score formula, tier assignment
│   │   │   │   ├── test_scoring.py         # Boundary values P1/P2/P3, needs_review
│   │   │   │   └── test_approval.py        # Approval gate, token expiry, dual-approval
│   │   │   ├── integration/
│   │   │   │   ├── test_cost_flow.py       # Cost query → Bedrock → response (moto)
│   │   │   │   └── test_action_flow.py     # Approve → ticket → notify → audit log
│   │   │   └── eval/
│   │   │       ├── prompts.json            # 20–40 eval prompts with expected outputs
│   │   │       └── run_eval.py             # Runs prompts against live agent, reports pass rate
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   └── Makefile                        # make test, make lint, make run
│   │
│   ├── infra/                              # AWS CDK (TypeScript)
│   │   ├── bin/
│   │   │   └── app.ts                      # CDK app entry — registers all 6 stacks
│   │   ├── lib/
│   │   │   ├── stacks/
│   │   │   │   ├── foundation-stack.ts     # Cognito, IAM roles, Secrets Manager
│   │   │   │   ├── data-stack.ts           # S3 buckets, Glue DB, Athena workgroup
│   │   │   │   ├── agent-stack.ts          # Bedrock Agents + 4 action groups
│   │   │   │   ├── api-stack.ts            # API Gateway, Lambda FastAPI, CloudWatch
│   │   │   │   ├── workflow-stack.ts       # Step Functions, EventBridge rules
│   │   │   │   └── frontend-stack.ts       # Amplify Hosting + build config
│   │   │   └── constructs/
│   │   │       ├── bedrock-agent.ts        # Reusable Bedrock agent + action group construct
│   │   │       ├── dynamo-tables.ts        # All 4 DynamoDB tables + GSIs
│   │   │       ├── lambda-adapter.ts       # Reusable Lambda adapter construct
│   │   │       └── cognito-pool.ts         # User pool + 4 groups + app client
│   │   ├── test/
│   │   │   ├── foundation.test.ts          # CDK assertions for Cognito + IAM
│   │   │   └── dynamo-tables.test.ts       # CDK assertions for table schema + GSIs
│   │   ├── cdk.json
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   └── shared/                             # Cross-package types and constants
│       ├── types/
│       │   ├── recommendation.ts           # Recommendation, PriorityTier, RecommendationType
│       │   ├── anomaly.ts                  # AnomalyEvent, AnomalySeverity
│       │   ├── cost.ts                     # CostRecord, CostDriver (FOCUS-aligned)
│       │   └── action.ts                   # ApprovalRequest, ActionResult, ActionStatus
│       ├── constants/
│       │   ├── roles.ts                    # COGNITO_GROUPS, ROLE_PERMISSIONS
│       │   └── config.ts                   # DEFAULT_CONFIDENCE_THRESHOLD, PRIORITY_WEIGHTS
│       └── schemas/
│           ├── recommendation.json         # JSON Schema for recommendation contract
│           └── anomaly.json                # JSON Schema for anomaly event contract
│
├── docs/                                   # Project documentation
│   ├── 01-discovery/
│   ├── 02-definition/
│   ├── 03-design/
│   ├── 04-delivery/
│   ├── 05-portfolio/
│   └── images/
│
├── fixtures/                               # Sample data for DEMO_MODE + tests
│   ├── sample-cost-data.json
│   ├── sample-anomaly.json
│   └── sample-recommendations.json
│
├── scripts/
│   ├── setup/
│   │   ├── bootstrap.sh                    # CDK bootstrap + prerequisite checks
│   │   └── seed-fixtures.sh                # Load fixture data into dev DynamoDB
│   ├── deploy/
│   │   ├── deploy-dev.sh                   # cdk deploy --all to dev account
│   │   └── deploy-prod.sh                  # cdk deploy --all to prod with approval
│   └── seed/
│       └── seed-dynamo.py                  # Python script to seed DynamoDB tables
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                          # PR checks: lint + test + type-check + synth
│   │   ├── deploy.yml                      # Deploy on merge to main
│   │   └── eval.yml                        # Weekly agent eval run (scheduled)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── copilot-instructions.md             # GitHub Copilot workspace context
│
├── .gitignore
├── .env.example                            # All required env vars (no values)
├── CHANGELOG.md
└── README.md
```

---

## Package Responsibilities

| Package | Language | Deployed As | Key Dependency |
|---------|----------|-------------|----------------|
| `src/frontend` | TypeScript | AWS Amplify Hosting | Next.js 15, AWS Amplify JS |
| `src/backend` | Python 3.12 | AWS Lambda (Mangum) | FastAPI, boto3, Pydantic |
| `src/infra` | TypeScript | AWS CDK deploy | aws-cdk-lib 2.x |
| `src/shared` | TypeScript | Imported by frontend + infra | — |

---

## Adapter Grouping by Agent

```
src/backend/adapters/
│
├── cost/               ← Cost Analysis Agent tools
│   ├── cost_query.py           get_cost_by_period
│   ├── anomaly_explain.py      get_anomaly_explanation
│   ├── budget_variance.py      get_budget_variance
│   └── forecast.py             get_forecast
│
├── optimization/       ← Optimization Agent tools
│   ├── recommendations.py      get_recommendations
│   ├── commitments.py          get_commitment_opportunities
│   └── idle_resources.py       get_idle_resources
│
├── governance/         ← Governance Agent tools
│   ├── risk_eval.py            evaluate_action_risk
│   ├── approval.py             request_approval / get_approval_status
│   └── tag_compliance.py       check_tag_compliance
│
└── actions/            ← Action execution (Step Functions invoked)
    ├── create_ticket.py        create_ticket → Jira
    └── notify_owner.py         notify_owner → Slack / Teams
```

---

## CDK Stack Dependency Order

```
foundation-stack        (Cognito, IAM, Secrets Manager)
       │
       ▼
  data-stack             (S3, Glue, Athena)
       │
       ▼
  agent-stack            (Bedrock Agents + action groups)
       │
       ▼
  api-stack              (API Gateway, Lambda FastAPI)
       │
    ┌──┴───────┐
    ▼          ▼
workflow-stack  frontend-stack
(Step Fn)      (Amplify)
```

---

## CI/CD Workflow Jobs

### ci.yml (runs on every PR)
```
backend-check
  ├── ruff check src/backend/
  ├── mypy src/backend/app
  └── pytest src/backend/tests/unit/ src/backend/tests/integration/

frontend-check
  ├── eslint src/frontend/
  ├── tsc --noEmit
  └── vitest run src/frontend/__tests__/

infra-check
  ├── tsc --noEmit (src/infra/)
  └── cdk synth --all
```

### deploy.yml (runs on merge to main)
```
deploy
  └── cdk deploy --all --require-approval never
```

### eval.yml (runs weekly — scheduled)
```
agent-eval
  └── python src/backend/tests/eval/run_eval.py
      → Posts pass rate report as workflow summary
```

---

## Key File Conventions

| Convention | Rule |
|-----------|------|
| DynamoDB keys | `ENTITY#id` — e.g. `REC#rec-001`, `APPROVAL#apr-001` |
| Lambda adapter response | Always return `messageVersion: "1.0"` + `functionResponse.responseBody.TEXT.body` |
| Env vars | All uppercase snake case — read via `src/backend/app/config.py` Settings class |
| Secrets | Never in code — always `secretsmanager.get_secret_value(SecretId=name)` |
| Feature flags | `FEATURE_*` prefix in config — `false` by default |
| DEMO_MODE | `DEMO_MODE=true` → all adapters serve from `fixtures/` |
| Tests | Unit tests use `@mock_aws` (moto). Integration tests hit real dev infra. |
| CDK resource IDs | `kebab-case` — e.g. `finops-recommendations`, `finops-action-workflow` |

---

## Local Development Commands

```bash
# Bootstrap (one-time)
bash scripts/setup/bootstrap.sh

# Backend
cd src/backend
make run          # uvicorn with hot reload on :8000
make test         # pytest unit + integration
make lint         # ruff + mypy

# Frontend
cd src/frontend
npm run dev       # Next.js on :3000
npm run test      # vitest

# Infra
cd src/infra
npm run build     # tsc compile check
cdk synth         # synthesize CloudFormation
cdk deploy --all  # deploy all stacks to dev

# Seed dev DynamoDB with fixture data
bash scripts/setup/seed-fixtures.sh
```

---

## References
- Architecture: docs/03-design/01-architecture-overview.md
- Code patterns: docs/03-design/06-code-reference.md
- Build prompts: docs/04-delivery/05-copilot-build-prompts.md
- Copilot context: .github/copilot-instructions.md

