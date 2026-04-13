# Architecture Overview

## 1. System Context
Users authenticate into a web app and ask cost questions in natural language. The backend orchestrates Bedrock agent workflows, queries AWS cost services, ranks optimization opportunities, and routes approved actions to Jira and Slack/Teams. Cost and action data are stored for lifecycle tracking and KPI reporting.

## 2. High-Level Components
- UI Layer: Next.js 15 + TypeScript + Tailwind, deployed on AWS Amplify Hosting
- Auth Layer: Amazon Cognito (user auth and role claims; groups: finops-analyst, engineering-manager, finance, leadership)
- API Layer: FastAPI on AWS Lambda behind Amazon API Gateway
- Agent Layer: Amazon Bedrock Agents — supervisor agent orchestrating three specialist agents:
  - Cost Analysis Agent: spend queries, anomaly explanation, budget variance, forecasting
  - Optimization Agent: recommendation ranking, rightsizing, idle detection, commitments
  - Governance Agent: tag policy compliance, budget policy checks, risk evaluation, approval gating
- Tool Adapter Layer: Lambda adapters for Cost Explorer, Cost Anomaly Detection, Compute Optimizer, Budgets, Trusted Advisor, Jira, Slack/Teams
- Data Layer: AWS Data Exports or CUR in Amazon S3 + AWS Glue Data Catalog + Amazon Athena
- State Layer: Amazon DynamoDB — four tables: finops-recommendations, finops-approvals, finops-action-history, finops-kpi-metrics
- Workflow Layer: AWS Step Functions + Amazon EventBridge for asynchronous action pipelines
- Observability Layer: Amazon CloudWatch logs/metrics/alarms + Bedrock traces
- Knowledge Base: Not in MVP scope. Deferred to Post-MVP Phase 7 for historical runbook and policy document grounding.

## 3. Data Flow
1. User asks query.
2. API validates identity and role.
3. Bedrock Agent orchestrates tool calls through adapters.
4. Adapters query Athena/Cost APIs and return normalized payloads.
5. Agent responds with explanation, recommendations, confidence, and evidence.
6. User approves action from recommendation panel.
7. Step Functions executes action workflow: create Jira ticket, notify Slack/Teams, persist lifecycle state.
8. KPI metrics and logs are written for reporting.

## 4. Security and Controls
- IAM least privilege
- Approval gate on sensitive actions
- Role-based output filtering
- Audit logging enabled
- Secrets in AWS Secrets Manager
- Encryption at rest (S3, DynamoDB) with KMS-managed keys

## 5. Suggested Tech Stack
- Backend: Python 3.12 + FastAPI on Lambda
- Agent SDK: Amazon Bedrock Agents Runtime APIs (with optional AgentCore upgrade path)
- Data store: S3 + Athena + DynamoDB
- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Deployment: AWS CDK (TypeScript) + GitHub Actions CI/CD

## 6. Architecture Diagram
Diagram source and rendered files:
- [Rendered (GitHub)](docs/images/architecture-mvp.md)
- [Mermaid source](docs/images/architecture-mvp.mmd)

Component grouping:
- Client: Browser, Next.js App (Amplify)
- Edge/API: API Gateway, Lambda FastAPI
- AI: Bedrock Agent + Knowledge Base (optional)
- Cost Data: S3 Data Exports/CUR, Glue, Athena
- Actions: Step Functions, Lambda Integrations, Jira, Slack/Teams
- Ops: CloudWatch, EventBridge, DynamoDB

## 7. References
AWS docs:
- https://aws.amazon.com/bedrock/agents/
- https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- https://aws.amazon.com/premiumsupport/technology/trusted-advisor/

Code references:
- https://github.com/awslabs/agentcore-samples
- https://github.com/aws/agentcore-cli
