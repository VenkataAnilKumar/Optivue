# Hiring Manager Summary: Optivue

## Candidate Project Snapshot
Optivue is an AWS-first, human-in-the-loop FinOps platform that helps organizations reduce cloud waste by converting cost visibility into governed execution. It combines AI-powered anomaly investigation, prioritized optimization recommendations, and approval-gated workflows to accelerate realized savings while maintaining operational control and auditability.

## Why this project matters
Cloud cost optimization often breaks at the handoff between analysis and execution. Teams can identify issues, but action routing, ownership, and follow-through are usually manual and slow. This project solves that bottleneck with an end-to-end, human-in-the-loop workflow.

## Business Problem Solved
- Slow anomaly triage and root-cause investigation
- Low recommendation adoption due to weak context
- Manual Jira and chat follow-up for optimization tasks
- Poor visibility from identified savings to realized savings

## Solution Delivered
### Core capabilities
- Natural language cloud cost analysis
- Anomaly explanation with impact and likely drivers
- Ranked savings recommendations with confidence and effort/risk context
- Human approval gate before actions
- Jira ticket creation and Slack/Teams owner notification
- Recommendation lifecycle tracking for KPI reporting

### Modern AWS architecture
- Frontend: Next.js 15 + TypeScript + Tailwind
- Backend: Python 3.12 + FastAPI on Lambda + API Gateway
- AI orchestration: Amazon Bedrock Agents
- Data: S3 Data Exports/CUR + Glue + Athena
- Workflow and state: Step Functions + EventBridge + DynamoDB
- Security and ops: Cognito + IAM least privilege + Secrets Manager + CloudWatch
- IaC/CI: AWS CDK + GitHub Actions

## Engineering Quality and Safety
- Serverless-first design for low cost and scalable demos
- Explicit approval required for action execution
- Role-aware responses and auditable action history
- Structured logging, observability dashboards, and evaluation plan
- Reproducible documentation pack from product brief to sprint tracker

## Product Delivery Approach
- Phase-based roadmap (12-week MVP)
- Sprint-level plan with entry/exit criteria
- KPI-driven acceptance gates
- Demo script with fixture fallback for reliability

## Measurable Outcomes Tracked
- Recommendation acceptance rate
- Recommendation completion rate
- Anomaly triage time reduction
- Query latency P95
- Identified vs realized savings
- Safety violations (target: zero)

## What this demonstrates about me
- I can translate business problems into buildable product scope.
- I can design modern cloud-native and AI-enabled architecture on AWS.
- I can implement delivery rigor: requirements, testing, roadmap, and execution tracking.
- I can build with security, governance, and observability as first-class concerns.

## Portfolio Navigation
- Product and requirements: docs/01-product-brief.md, docs/02-prd-lite.md
- Architecture and contracts: docs/03-architecture-overview.md, docs/04-data-tool-contract.md
- Execution and quality: docs/08-implementation-roadmap-phases.md, docs/09-sprint-plan.md, docs/07-test-evaluation-plan.md
- Demo flow: docs/06-demo-script.md

