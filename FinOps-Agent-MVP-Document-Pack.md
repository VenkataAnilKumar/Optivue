# FinOps Agent MVP Document Pack (Job-Focused)

## Purpose
This document defines the minimum documentation set required to build and present a job-ready FinOps Agent MVP. It includes direct AWS documentation and code references for implementation.

## Scope
MVP capabilities:
- Natural language cost analysis
- Anomaly explanation
- Top optimization recommendations
- Ticket creation (Jira)
- Notification (Slack/Teams)
- Human approval gate before actions

---

## 1) Product Brief (1 page)
### Must include
- Problem statement
- Target users (FinOps analyst, engineering manager)
- Value proposition
- MVP boundary (what is in / out)
- Expected business impact

### AWS docs to cite
- AWS Cost Explorer: https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- AWS Cost Anomaly Detection: https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/

### Code references
- Bedrock Agents samples: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling/bedrock-agents

---

## 2) PRD Lite
### Must include
- Functional requirements (FR)
- Non-functional requirements (NFR)
- Success metrics
- Non-goals
- Risks and mitigations

### AWS docs to cite
- Bedrock Agents overview: https://aws.amazon.com/bedrock/agents/
- Bedrock best practices part 1: https://aws.amazon.com/blogs/machine-learning/best-practices-for-building-robust-generative-ai-applications-with-amazon-bedrock-agents-part-1/
- Bedrock best practices part 2: https://aws.amazon.com/blogs/machine-learning/best-practices-for-building-robust-generative-ai-applications-with-amazon-bedrock-agents-part-2/

### Code references
- Agent blueprints and examples: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling/bedrock-agents

---

## 3) Architecture Overview
### Must include
- Components: UI, Agent Orchestrator, AWS cost adapters, action connectors
- Data flow from user query to recommendation to action
- Security boundaries and approval points

### AWS docs to cite
- Bedrock Knowledge Bases: https://aws.amazon.com/bedrock/knowledge-bases/
- AWS Cost and Usage Reports / Data Exports: https://aws.amazon.com/aws-cost-management/aws-cost-and-usage-reporting/
- AWS Trusted Advisor: https://aws.amazon.com/premiumsupport/technology/trusted-advisor/

### Code references
- AgentCore samples (end-to-end and infrastructure): https://github.com/awslabs/agentcore-samples

---

## 4) Data and Tool Contract
### Must include
- Input schema: cost records, anomaly events, owner metadata
- Output schema: recommendation payload, confidence, estimated savings
- Tool contract for each integration (Cost Explorer, Anomaly, Jira, Slack)

### AWS docs to cite
- AWS Budgets: https://aws.amazon.com/aws-cost-management/aws-budgets/
- AWS Compute Optimizer: https://aws.amazon.com/compute-optimizer/
- Savings Plans: https://aws.amazon.com/savingsplans/

### Code references
- Bedrock function-calling examples: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling

---

## 5) User Stories and Acceptance Criteria
### Must include
- 8-12 user stories
- Given/When/Then acceptance checks
- Story priority (P1/P2)

### Suggested stories
- Ask monthly spend and top drivers
- Explain anomaly and likely owner
- Generate top 5 savings opportunities
- Create Jira ticket for selected recommendation
- Send Slack notification to owner
- Require explicit approval before write action

### AWS docs to cite
- Cost Explorer user guide entry point: https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html
- Anomaly Detection user guide entry point: https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html

---

## 6) Demo Script
### Must include
- 5-7 minute walkthrough
- Input prompts and expected output snapshots
- Contingency flow if integration is unavailable (use fixture data)

### Demo flow
1. Query: "Why did cost increase this week?"
2. Show anomaly explanation
3. Show ranked recommendations with savings estimate
4. Approve one recommendation
5. Create Jira ticket and send Slack message

### AWS docs to cite
- Bedrock Agents capability overview: https://aws.amazon.com/bedrock/agents/

### Code references
- Test-agent examples: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling/bedrock-agents/test-agent

---

## 7) Test and Evaluation Plan
### Must include
- Functional tests
- Prompt quality tests
- Safety tests (approval required)
- KPI validation tests

### Metrics to track
- Recommendation acceptance rate
- Time-to-insight for anomaly triage
- False positive recommendation rate
- Identified vs realized savings

### AWS docs to cite
- Bedrock traces and observability (best practices part 2): https://aws.amazon.com/blogs/machine-learning/best-practices-for-building-robust-generative-ai-applications-with-amazon-bedrock-agents-part-2/

### Code references
- Agent Evaluation framework: https://github.com/awslabs/agent-evaluation
- Bedrock observability custom solution: https://github.com/aws-samples/amazon-bedrock-samples/tree/main/evaluation-observe/Custom-Observability-Solution

---

## 8) README (Portfolio-first)
### Must include
- What problem this solves
- Architecture image
- Quick start instructions
- Environment variables
- Sample prompts
- Screenshots / GIF links
- Known limitations
- Future improvements

### AWS docs to cite
- Bedrock documentation landing: https://docs.aws.amazon.com/bedrock/
- Cost Management landing: https://aws.amazon.com/aws-cost-management/

### Code references
- AgentCore CLI: https://github.com/aws/agentcore-cli
- Bedrock AgentCore SDK Python: https://github.com/aws/bedrock-agentcore-sdk-python

---

## Recommended File Structure

```
FinOps/
├── README.md
├── FinOps-Agent-Product-Definition.md
├── FinOps-Agent-MVP-Document-Pack.md
├── docs/
│   ├── 01-discovery/
│   │   ├── 01-product-brief.md
│   │   └── 02-open-questions-resolved.md
│   ├── 02-definition/
│   │   ├── 01-prd-lite.md
│   │   └── 02-user-stories.md
│   ├── 03-design/
│   │   ├── 01-architecture-overview.md
│   │   ├── 02-bedrock-agent-instructions.md
│   │   ├── 03-action-group-schemas.md
│   │   ├── 04-database-schema.md
│   │   ├── 05-data-tool-contract.md
│   │   └── 06-code-reference.md
│   ├── 04-delivery/
│   │   ├── 01-implementation-roadmap-phases.md
│   │   ├── 02-sprint-plan.md
│   │   ├── 03-test-evaluation-plan.md
│   │   └── 04-demo-script.md
│   ├── 05-portfolio/
│   │   ├── 01-hiring-manager-summary.md
│   │   ├── 02-resume-bullet-pack.md
│   │   ├── 03-interview-qa-sheet.md
│   │   └── 04-spoken-interview-scripts.md
│   └── images/
│       ├── architecture-mvp.md
│       └── architecture-mvp.mmd
└── fixtures/
    ├── sample-cost-data.json
    ├── sample-anomaly.json
    └── sample-recommendations.json
```

---

## Interview-Ready Completion Checklist
- All 17 documents created and internally consistent
- Every requirement mapped to at least one AWS doc or code sample
- Bedrock agent instructions and action group schemas defined
- DynamoDB table schema and access patterns documented
- All 5 open questions answered with implementation decisions
- Demo script rehearsed with fixture fallback
- KPI values available for at least one sample dataset run
- README can be followed by recruiter in under 10 minutes

---

## Source Reference Set (curated)
- Bedrock Agents: https://aws.amazon.com/bedrock/agents/
- Bedrock Knowledge Bases: https://aws.amazon.com/bedrock/knowledge-bases/
- Cost Explorer: https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- Cost Anomaly Detection: https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/
- Cost and Usage Reports: https://aws.amazon.com/aws-cost-management/aws-cost-and-usage-reporting/
- AWS Budgets: https://aws.amazon.com/aws-cost-management/aws-budgets/
- Compute Optimizer: https://aws.amazon.com/compute-optimizer/
- Savings Plans: https://aws.amazon.com/savingsplans/
- Trusted Advisor: https://aws.amazon.com/premiumsupport/technology/trusted-advisor/
- Bedrock samples repo: https://github.com/aws-samples/amazon-bedrock-samples
- AgentCore samples repo: https://github.com/awslabs/agentcore-samples
- Agent Evaluation: https://github.com/awslabs/agent-evaluation
