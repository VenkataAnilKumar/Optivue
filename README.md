# Optivue

> An AWS-native, human-in-the-loop AI assistant that turns cloud cost data into actionable optimization workflows.

Engineering and finance teams spend significant time manually triaging cost spikes, writing up Jira tickets, and chasing down resource owners. Optivue replaces that toil with a conversational AI layer that queries live AWS cost data, explains anomalies, ranks savings opportunities, routes approvals, and notifies owners — all with a mandatory human gate before any change is made.

---

## Product Capabilities

| Capability | Description |
|---|---|
| **Natural language cost queries** | Ask spend questions by period, service, or tag in plain English |
| **Anomaly investigation** | AI-driven root cause explanation with top cost drivers |
| **Ranked recommendations** | Savings opportunities scored by impact, confidence, effort, and risk |
| **Approval-gated actions** | No write action executes without an explicit approval token |
| **Jira + Slack / Teams integration** | Ticket creation and owner notification flow from a single approval |
| **Spend forecasting** | Monthly and quarterly forecasts with confidence intervals via Cost Explorer |
| **Role-scoped dashboards** | Tailored views for FinOps analysts, engineering managers, finance, and leadership |
| **Demo mode** | All AWS calls replaced by fixture data when `DEMO_MODE=true` |

---

## Architecture

```
Browser / Next.js 15
        │
        ▼
Amazon API Gateway  ──►  FastAPI on AWS Lambda
                                │
                    ┌───────────┴────────────┐
                    ▼                        ▼
         Amazon Bedrock Agents          DynamoDB (4 tables)
         ┌──────────────────┐
         │  finops-supervisor│
         │  ├── cost-analysis│  ◄── Cost Explorer · Anomaly Detection · Athena
         │  ├── optimization │  ◄── Compute Optimizer · Trusted Advisor · Savings Plans
         │  └── governance   │  ◄── Budgets · IAM · Approval token validation
         └──────────────────┘
                    │
                    ▼
         AWS Step Functions
         ValidateApproval → CreateTicket → NotifyOwner → UpdateActionState
```

Cost data flows: **AWS Data Exports / CUR → S3 → Glue → Athena**

Infrastructure is defined entirely in **AWS CDK (TypeScript)** and deployed across six stacks: `FinOpsFoundation`, `FinOpsData`, `FinOpsAgent`, `FinOpsApi`, `FinOpsWorkflow`, `FinOpsFrontend`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 · TypeScript · Tailwind CSS · AWS Amplify Hosting |
| Auth | Amazon Cognito — groups: `finops-analyst`, `engineering-manager`, `finance`, `leadership` |
| API | FastAPI · AWS Lambda · Amazon API Gateway |
| AI / Agents | Amazon Bedrock Agents — supervisor + 3 specialist agents |
| Data | AWS CUR / Data Exports → S3 · Glue · Athena |
| State | Amazon DynamoDB (4 tables) |
| Workflow | AWS Step Functions · Amazon EventBridge |
| Notifications | Jira API · Slack / Teams webhooks |
| IaC | AWS CDK (TypeScript) |
| CI / CD | GitHub Actions |
| Observability | Amazon CloudWatch · Bedrock trace logging |
| Runtime | Python 3.12 (backend / agents) · Node.js 20 (CDK / frontend) |

---

## Agent Design

Three specialist agents operate under a supervisor. Each agent is scoped to a domain and exposes Bedrock action groups backed by Lambda adapters.

**cost-analysis-agent** — spend queries, anomaly explanation, budget variance, forecasting  
**optimization-agent** — rightsizing, idle resource detection, commitment purchase analysis  
**governance-agent** — tag compliance, budget policy enforcement, approval gating, risk evaluation

Every recommendation carries a `confidence_score`, `priority_score` (P1 / P2 / P3), `estimated_monthly_savings`, and a `data_freshness_timestamp`. Auto-routing only applies when `confidence_score >= 0.70`; anything below is flagged `needs_review: true`.

**Approval matrix** (abridged):

| Environment | Action | Required approvers |
|---|---|---|
| prod | rightsizing | engineering-manager + finops-analyst |
| prod | commitment purchase | finops-analyst + finance |
| prod | idle shutdown | engineering-manager |
| staging | any | finops-analyst |
| dev — low risk | any | auto-approved |

Approval tokens expire after 4 hours. Dual-approval requires both roles to confirm independently.

---

## Data Model

Four DynamoDB tables with prefixed keys:

| Table | Key prefix | Purpose |
|---|---|---|
| `finops-recommendations` | `REC#` | Recommendation lifecycle and payload |
| `finops-approvals` | `APPROVAL#` | Approval token records |
| `finops-action-history` | `ACTION#` / `HISTORY#` | Completed / failed action audit trail |
| `finops-kpi-metrics` | `KPI#` | Weekly / monthly KPI snapshots |

All tables have point-in-time recovery enabled. Full schema: [docs/03-design/04-database-schema.md](docs/03-design/04-database-schema.md).

---

## Project Documentation

### 01 — Discovery
- [Product Brief](docs/01-discovery/01-product-brief.md)
- [Open Questions Resolved](docs/01-discovery/02-open-questions-resolved.md)

### 02 — Definition
- [PRD Lite](docs/02-definition/01-prd-lite.md)
- [User Stories and Acceptance Criteria](docs/02-definition/02-user-stories.md)

### 03 — Design
- [Architecture Overview](docs/03-design/01-architecture-overview.md)
- [Bedrock Agent Instructions](docs/03-design/02-bedrock-agent-instructions.md)
- [Action Group OpenAPI Schemas](docs/03-design/03-action-group-schemas.md)
- [Database Schema](docs/03-design/04-database-schema.md)
- [Data and Tool Contract](docs/03-design/05-data-tool-contract.md)
- [Code Reference](docs/03-design/06-code-reference.md)
- [Repository Structure](docs/03-design/07-repo-structure.md)

### 04 — Delivery
- [Implementation Roadmap](docs/04-delivery/01-implementation-roadmap-phases.md)
- [Sprint Plan](docs/04-delivery/02-sprint-plan.md)
- [Test and Evaluation Plan](docs/04-delivery/03-test-evaluation-plan.md)
- [Demo Script](docs/04-delivery/04-demo-script.md)
- [Release Handoff Report](docs/04-delivery/06-release-handoff.md)

---

## Quick Start

### Prerequisites
- AWS account with Bedrock model access enabled
- Node.js 20+, Python 3.12+, AWS CLI v2
- CDK bootstrapped in target region

```bash
npm install -g aws-cdk
aws sts get-caller-identity      # confirm credentials
cdk bootstrap aws://<account>/<region>
```

### Environment variables

```bash
AWS_REGION=us-east-1
BEDROCK_AGENT_ID=<your-agent-id>
BEDROCK_AGENT_ALIAS_ID=<your-agent-alias-id>
ATHENA_DATABASE=<your-athena-db>
ATHENA_WORKGROUP=primary
COST_EXPORT_S3_BUCKET=<your-cost-export-bucket>
JIRA_BASE_URL=<your-jira-url>
JIRA_API_TOKEN=<secret-via-secrets-manager>
SLACK_WEBHOOK_URL=<secret-via-secrets-manager>
```

> All secrets must be stored in AWS Secrets Manager. No plaintext credentials in environment or code.

### Deploy

```bash
# From repo root
cd src/infra
npm ci
cdk deploy --all
```

### Run preflight checks

```bash
bash scripts/deploy/deploy-dev.sh    # backend 36 tests · infra 9 tests · CDK synth
bash scripts/deploy/deploy-prod.sh   # same checks + safety gate (no auto-deploy)
```

### Demo mode (no AWS required)

```bash
DEMO_MODE=true npm run dev
```

All AWS service calls return data from `fixtures/` when demo mode is active.

---

## Performance Targets

| Workload | P95 target |
|---|---|
| Standard analytics queries | ≤ 8 seconds |
| Deep anomaly investigation | ≤ 20 seconds |

**Action safety violations: 0 — hard requirement.**

---

## References

| Resource | Link |
|---|---|
| Amazon Bedrock Agents | https://aws.amazon.com/bedrock/agents/ |
| AWS Cost Explorer | https://aws.amazon.com/aws-cost-management/aws-cost-explorer/ |
| Cost Anomaly Detection | https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/ |
| AWS Budgets | https://aws.amazon.com/aws-cost-management/aws-budgets/ |
| Compute Optimizer | https://aws.amazon.com/compute-optimizer/ |
| Savings Plans | https://aws.amazon.com/savingsplans/ |
| Trusted Advisor | https://aws.amazon.com/premiumsupport/technology/trusted-advisor/ |
| Bedrock agent samples | https://github.com/aws-samples/amazon-bedrock-samples |
| AgentCore samples | https://github.com/awslabs/agentcore-samples |
| Agent evaluation | https://github.com/awslabs/agent-evaluation |

