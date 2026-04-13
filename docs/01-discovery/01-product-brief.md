# Product Brief

## 1. Project Summary
- Product name: Optivue
- Type: Job-focused MVP portfolio project
- Version: 0.1
- Date: 2026-04-13
- Owner: Venkata

## 2. Problem Statement
FinOps teams, platform engineers, and finance stakeholders struggle to move from cloud cost insight to cost action.
- Who has the problem: FinOps analysts, engineering managers, and cloud platform teams.
- What they are doing manually: investigating spend spikes in dashboards, correlating anomalies with owners, creating tickets, and following up in chat.
- Why this is costly: analysis-to-action is slow, recommendations are not contextualized, and many savings opportunities are not realized.

## 3. Target Users
- Primary user 1: FinOps Analyst
- Primary user 2: Engineering Manager / Service Owner
- Secondary user 1: Finance / FP&A Business Partner
- Secondary user 2: Leadership (CTO / CFO / VP Engineering)

## 4. Value Proposition
In one sentence:
- This product helps FinOps and engineering teams reduce cloud waste and investigation time by using a Bedrock-powered agent that explains spend, prioritizes savings actions, and routes approved actions into delivery workflows.

## 5. MVP Scope
In scope:
- Natural language cost analysis
- Anomaly explanation
- Top optimization recommendations
- Jira ticket creation
- Slack/Teams notification
- Human approval before action

Out of scope:
- Full autonomous remediation
- Multi-cloud execution
- Enterprise governance workflows

## 6. Success Metrics
- Recommendation acceptance rate target: >= 30% in pilot
- Time-to-insight target: <= 5 minutes for anomaly triage
- False positive recommendation target: <= 15%
- Identified vs realized savings tracking enabled: Yes

## 7. Key Risks
- Risk 1: Data quality and incomplete tags reduce recommendation confidence.
- Risk 2: User trust gap for autonomous actions.
- Risk 3: Alert fatigue from low-value recommendations.

## 8. AWS Docs and Code References
AWS docs:
- https://aws.amazon.com/bedrock/agents/
- https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/

Code references:
- https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling/bedrock-agents
- https://github.com/awslabs/agentcore-samples

