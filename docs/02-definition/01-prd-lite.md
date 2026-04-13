# PRD Lite

## 1. Overview
- Product: Optivue MVP
- Objective: Build an AWS-first, human-in-the-loop AI assistant that turns cost analysis into actionable optimization workflows.
- Release target: 12-week MVP (internal demo + pilot-ready)

## 2. Users and Personas
- Persona 1: FinOps Analyst (investigates spend and prioritizes savings backlog)
- Persona 2: Engineering Manager / Service Owner (owns remediation actions and delivery follow-through)
- Persona 3: Finance / FP&A (forecast confidence, budget variance, variance narratives)
- Persona 4: Leadership — CTO/CFO/VP Eng (unit economics, trend clarity, accountability signals)

Cognito Groups and Permitted Actions:

| Group | Permitted Actions |
|-------|------------------|
| finops-analyst | Full read, recommendation triage, ticket creation, notifications, single approvals |
| engineering-manager | View recommendations for own team, acknowledge/complete actions, single approvals |
| finance | Read-only cost reports, forecasts, budget variance; no action execution |
| leadership | Read-only executive dashboard and KPI snapshots; no action execution |

## 3. Functional Requirements
- FR-1: User can query spend in natural language by period/service/tag.
- FR-2: System explains detected anomalies with top drivers.
- FR-3: System returns ranked savings recommendations with confidence and estimated impact.
- FR-4: User can approve a recommendation and create a Jira ticket.
- FR-5: System sends owner notification to Slack/Teams.
- FR-6: Mutating actions require explicit user confirmation.
- FR-7: System provides monthly spend forecast with confidence interval and budget variance narrative. (MVP scope: AWS Cost Explorer forecast API; advanced statistical forecasting deferred to Post-MVP.)

## 4. Non-Functional Requirements
- Security: least privilege IAM, audit logs, Cognito role-based access control.
- Performance: P95 response under 8 seconds for standard analytics queries; P95 under 20 seconds for deep anomaly investigation workflows.
- Reliability: graceful degradation when external APIs fail.
- Explainability: every recommendation includes rationale and source.
- Maintainability: infrastructure managed via AWS CDK and version-controlled CI/CD.

## 5. Non-Goals
- No autonomous production deletion.
- No broad enterprise policy engine in MVP.

## 6. KPIs
- Acceptance rate: >= 30% in pilot
- Recommendation completion rate: >= 20% in first cycle
- Anomaly triage time reduction: >= 15%
- Identified savings: tracked weekly by recommendation class
- Realized savings: tracked monthly from closed actions

## 7. Risks and Mitigations
- Data quality risk -> data quality checks + confidence scoring.
- Trust risk -> human approval gate.
- Alert fatigue -> dedupe + thresholding.

## 8. Dependencies
- AWS account and permissions
- Jira project/API token
- Slack/Teams webhook or app integration
- Amazon Cognito setup for user authentication
- Access to CUR/Data Exports in S3 and Athena query permissions

## 9. References
AWS docs:
- https://aws.amazon.com/bedrock/agents/
- https://aws.amazon.com/bedrock/knowledge-bases/
- https://aws.amazon.com/aws-cost-management/aws-cost-and-usage-reporting/

Code references:
- https://github.com/aws-samples/amazon-bedrock-samples
- https://github.com/awslabs/agent-evaluation

