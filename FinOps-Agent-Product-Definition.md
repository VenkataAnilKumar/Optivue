# Optivue Product Definition (PRD)

## 1) Document Control
- Product: Optivue
- Version: 1.0
- Date: 2026-04-13
- Status: Draft for stakeholder review
- Product Type: AI-native FinOps operations assistant and action orchestrator

## 2) Executive Summary
FinOps teams still spend too much time in manual analysis, dashboard stitching, and follow-up coordination before optimization actions happen. The Optivue closes that gap by moving from observation to orchestration: it explains spend, detects and investigates anomalies, recommends ranked optimizations, and routes approved actions into engineering workflows.

The product combines:
- Natural language analytics for cloud cost and value
- Agentic workflows for root cause and owner mapping
- Human-in-the-loop controls for safe execution
- Continuous measurement of identified and realized savings

Core business outcome: reduce cloud waste and time-to-action while increasing accountability at team and product scope.

## 3) Problem Statement
### Current Pain
- FinOps analysts spend significant time extracting and normalizing data before insights can be acted on.
- Engineering teams receive generic recommendations with low context and low action rates.
- Cost anomaly alerts are often noisy or not routed to the right owner quickly.
- Savings opportunities are identified but not tracked to execution and realization.
- Leadership lacks consistent unit economics and forecast confidence.

### Why Now
- Cloud and AI spend volatility is increasing.
- FinOps Foundation guidance in 2026 emphasizes AI-for-FinOps and agentic use cases.
- Cloud providers now expose APIs for anomaly detection, rightsizing, commitments, and recommendations that can be orchestrated by agents.

## 4) Opportunity and Product Thesis
If we provide a Optivue that can:
1. Understand spend and business context,
2. Investigate anomalies and waste autonomously,
3. Route recommendations to the right owners with evidence,
4. Enforce human approvals for risky actions,

then organizations can improve realized savings, reduce investigation toil, and improve cloud unit economics without scaling headcount linearly.

## 5) Research Synthesis (Deep Research Findings)
### 5.1 FinOps Framework Alignment
Research from FinOps Foundation confirms six governing principles, especially:
- Teams need to collaborate.
- Business value drives technology decisions.
- Everyone takes ownership.
- Data must be timely and accurate.
- FinOps is enabled centrally.

Implication for product:
- The agent must be collaborative by design (Finance, Engineering, Product, Leadership views).
- Optimization ranking must include business-value context, not cost-only sorting.
- Ownership and chargeback metadata must be first-class in every recommendation.

### 5.2 FinOps Capability Coverage
FinOps capabilities most relevant to this product:
- Data Ingestion
- Allocation
- Reporting and Analytics
- Anomaly Management
- Forecasting
- Budgeting
- KPIs and Benchmarking
- Unit Economics
- Usage Optimization
- Rate Optimization
- Governance, Policy and Risk

Implication for product:
- The MVP should not attempt all 22 capabilities equally.
- V1 should prioritize high-frequency workflows: anomaly triage, waste discovery, prioritization, and action tracking.

### 5.3 Agentic FinOps Direction (2026)
FinOps Foundation insights on agentic use cases show emerging patterns:
- Natural-language financial reconciliation
- Autonomous waste discovery with owner assignment
- Shift-left cost guardrails in CI/CD
- Personalized outreach through collaboration tools
- Human-in-the-loop remains mandatory for trust and risk controls

Implication for product:
- Human confirmation and policy gates are hard requirements, not optional UX details.
- Messaging personalization and owner targeting are key to recommendation acceptance rate.

### 5.4 AWS Cost Management and Optimization Tooling
AWS service research indicates strong API-ready building blocks:
- Cost Explorer: trend analysis, forecasting, custom dimensions
- Cost Anomaly Detection: ML-based anomaly detection and root cause context
- Cost and Usage Reports / Data Exports: granular billing source of truth
- Budgets: threshold alerts and control workflows
- Compute Optimizer: rightsizing and resource optimization recommendations
- Savings Plans: commitment-based discount opportunities
- Trusted Advisor: best-practice optimization and remediation checks

Implication for product:
- The Optivue should orchestrate existing systems rather than replicate them.
- Primary defensibility is workflow intelligence, contextualization, and realization tracking.

### 5.5 Data Standardization
FOCUS (FinOps Open Cost and Usage Specification) provides normalized billing semantics across providers.

Implication for product:
- Build a provider-agnostic data model around FOCUS concepts from day one.
- This reduces lock-in and enables future multi-cloud expansion.

## 6) Target Users and Personas
### Core Personas
1. FinOps Practitioner
- Needs: fast anomaly triage, opportunity backlog, realized savings tracking
- Pain: manual reporting, fragmented tools

2. Engineering Manager / Service Owner
- Needs: prioritized recommendations with clear impact and low-risk paths
- Pain: generic advisories without workload context

3. Finance / FP and A
- Needs: forecast confidence, variance explanation, budget control
- Pain: lagging explanations and low granularity

4. Leadership (CTO/CFO/VP Eng)
- Needs: unit economics, trend clarity, accountability signals
- Pain: inconsistent KPI narrative across teams

### Allied Personas
- Procurement: commitment strategy
- Security and Platform Governance: policy controls and risk boundaries

## 7) Jobs To Be Done
1. When spend spikes unexpectedly, I want immediate root-cause analysis and owner routing so we can contain impact quickly.
2. When reviewing optimization opportunities, I want ranked actions by savings, effort, and risk so teams execute the right work first.
3. When budgeting and forecasting, I want confidence bounds and variance narratives so finance and engineering stay aligned.
4. When recommendations are published, I want execution tracking and realized savings evidence so outcomes are measurable.

## 8) Product Scope
### In Scope (V1)
- Natural-language spend and usage analysis
- Anomaly detection triage and explanation
- Waste discovery and recommendation ranking
- Owner mapping and automated ticket creation
- Weekly FinOps report generation
- Human approval workflow for sensitive actions

### Out of Scope (V1)
- Fully autonomous resource deletion in production
- Direct mutation of high-risk production resources without explicit approval
- Multi-cloud optimization execution (analysis can be extensible but execution starts AWS-first)

## 9) Solution Overview
### 9.1 Agent System Design
A supervisor agent coordinates three specialist agents:
1. Cost Analysis Agent
- Spend breakdown, trend decomposition, budget and forecast variance

2. Optimization Agent
- Rightsizing, idle resource identification, commitment opportunities, prioritization

3. Governance Agent
- Tag policy adherence, budget policy checks, approval and risk guardrails

### 9.2 Key Product Modules
1. Data Fabric
- CUR/Data Exports ingestion
- Cost Explorer and optimization APIs
- Resource and ownership metadata
- Ticketing and chat system integrations

2. Insight Engine
- Anomaly explanation
- Opportunity scoring
- Forecast generation
- Unit economics computation

3. Action Orchestrator
- Ticket generation and assignment
- Notification workflows
- Approval and policy gating
- Execution status tracking

4. Measurement Layer
- Recommendation lifecycle and realized savings
- KPI dashboards for each persona
- Agent quality metrics (accuracy, acceptance, precision)

## 10) Functional Requirements
### FR-1 Conversational Cost Analytics
- User can query spend by time, account, service, tag, product, and environment.
- System returns answer with numeric summary, trend comparison, and top drivers.
- Responses include data freshness timestamp and source references.

### FR-2 Anomaly Triage and Root Cause
- System surfaces anomalies by monitor scope and severity.
- Agent produces probable root cause hypothesis and impacted scopes.
- Agent identifies candidate owner and recommends next action.

### FR-3 Opportunity Discovery and Prioritization
- Agent compiles optimization opportunities from provider recommendations and custom heuristics.
- Each recommendation includes estimated monthly savings, confidence score, effort estimate, and risk class.
- Recommendations are ranked by expected value score.

### FR-4 Action Workflow and Accountability
- Agent can create tickets in Jira/ServiceNow with evidence and acceptance criteria.
- Agent can notify owners in Slack/Teams with contextual summary.
- Agent tracks status transitions: open, acknowledged, in-progress, completed, verified.

### FR-5 Forecasting and Budget Variance Narratives
- Agent provides monthly forecast and confidence interval.
- Agent explains variance versus budget and prior period.
- Agent can generate weekly and monthly executive summaries.

### FR-6 Human-in-the-Loop and Safety Controls
- Mutating actions require explicit user confirmation.
- Policy engine blocks prohibited action types by environment or role.
- Every recommendation must include rationale and evidence trace.

### FR-7 FinOps KPI and Realization Tracking
- Track identified savings versus realized savings.
- Track recommendation acceptance and completion rates.
- Support reporting by scope: product, cost center, environment.

## 11) Non-Functional Requirements
1. Security
- Least-privilege IAM
- Role-based access by persona
- Encryption in transit and at rest

2. Reliability
- 99.9% monthly availability target for core query and recommendation APIs
- Graceful degradation when external provider APIs fail

3. Performance
- P95 response time under 8 seconds for standard analytics queries
- P95 under 20 seconds for deep anomaly investigation workflows

4. Auditability
- Full trace of prompts, tool calls, policy decisions, and user confirmations
- Immutable audit logs for governance-sensitive actions

5. Explainability
- Every recommendation has plain-language explanation, confidence, and evidence links

## 12) Data Model and Standards
### Canonical Dimensions
- Provider, account/subscription/project
- Service and SKU family
- Region
- Product/cost-center/environment tags
- Owner identity
- Time bucket (hour/day/month)

### Data Standardization
- Use FOCUS-compatible normalized schema where feasible.
- Preserve source-native fields for forensic analysis.

### Data Freshness Targets
- Daily baseline ingestion for full-cost data
- Near-real-time anomaly and operational telemetry where available

## 13) Decisioning and Ranking Logic
Each opportunity is scored with weighted factors:
- Estimated savings value (weight 35%)
- Confidence in recommendation (weight 20%)
- Engineering effort to remediate (weight 20%)
- Operational risk and blast radius (weight 15%)
- Strategic alignment or policy urgency (weight 10%)

Score output:
- Priority tier: P1, P2, P3
- Recommended due date
- Suggested owner and escalation path

## 14) UX Requirements
1. Role-aware home views
- FinOps analyst queue
- Engineering team action inbox
- Leadership snapshot

2. Query experience
- Natural language with optional structured filters
- Drill-down from summary to resource-level evidence

3. Action experience
- One-click ticket creation from recommendation cards
- Human confirmation modal for sensitive actions
- Execution progress timeline

4. Reporting
- Weekly digest
- Monthly executive narrative
- Team-level scorecards

## 15) Integrations (AWS-first V1)
### Cost and Optimization Data
- AWS Cost Explorer
- AWS Cost Anomaly Detection
- AWS Cost and Usage Reports / AWS Data Exports
- AWS Compute Optimizer
- AWS Budgets
- AWS Trusted Advisor
- Savings Plans utilization and recommendation surfaces

### Enterprise Integrations
- Jira or ServiceNow
- Slack or Microsoft Teams
- Optional CMDB/ownership graph source

## 16) KPI Framework
### Product KPIs
1. Time-to-insight for anomaly investigation
2. Recommendation acceptance rate
3. Recommendation completion rate
4. Median cycle time from recommendation to remediation
5. Identified monthly savings
6. Realized monthly savings

### FinOps Outcome KPIs
1. Budget variance reduction
2. Increase in tagged cost coverage
3. Improvement in commitment coverage/utilization
4. Unit economics improvement for selected products

### Agent Quality KPIs
1. Recommendation precision (accepted and beneficial)
2. Recommendation recall (coverage of true opportunities)
3. False-positive anomaly rate
4. Hallucination or unsupported-claim rate

## 17) Rollout Strategy (Crawl, Walk, Run)
### Crawl (0-8 weeks)
- One business unit, AWS-only
- Read-only analytics plus ticket creation
- Human confirmation required for any mutating operation
- Weekly steering review with FinOps and Engineering

### Walk (2-4 months)
- Expand to multiple business units and environments
- Add personalized outreach and escalation automation
- Introduce shift-left policy checks in CI/CD for IaC changes

### Run (4-9 months)
- Organization-wide adoption
- Multi-agent collaboration at scale
- Multi-cloud ingestion using FOCUS normalization
- Selective low-risk auto-remediation in non-production

## 18) Pricing and Commercial Model (If External SaaS)
### Packaging
1. Team Plan
- Cost analytics + anomaly triage + limited actions

2. Business Plan
- Full recommendation lifecycle + workflow integrations + advanced forecasting

3. Enterprise Plan
- Policy engine, private deployment options, advanced governance and audit

### Suggested Pricing Driver
- Tiered by monthly cloud spend managed and number of active action workflows

## 19) Risks and Mitigations
1. Trust gap for autonomous actions
- Mitigation: strict human approvals, transparent evidence, staged autonomy

2. Data quality and tagging gaps
- Mitigation: confidence scoring, data quality health checks, owner fallback logic

3. Alert fatigue
- Mitigation: adaptive thresholds, suppression logic, recommendation deduping

4. Recommendation irrelevance to engineering context
- Mitigation: workload metadata enrichment, owner feedback loop, closed-loop learning

5. Security and governance concerns
- Mitigation: least privilege, policy-as-code, role-aware outputs, full audits

## 20) MVP Milestones and Exit Criteria
### Milestone A: Foundations
- Ingestion pipeline established
- Query and anomaly APIs connected
- Baseline dashboards available

Exit criteria:
- Data completeness above 95% for in-scope accounts

### Milestone B: Actionability
- Opportunity ranking operational
- Ticketing integration live
- Weekly report automation live

Exit criteria:
- At least 30% recommendation acceptance in pilot cohort

### Milestone C: Realization
- Savings tracking verified with finance
- KPI scorecards by team enabled

Exit criteria:
- Demonstrated realized savings in pilot and reduction in investigation time

## 21) Open Questions
1. What minimum confidence threshold is required before a recommendation can be auto-routed?
2. Which teams own final approval for production-impacting changes?
3. What unit economics metrics are mandatory for executive reporting?
4. Is the first deployment internal-only or customer-facing SaaS?
5. What is the acceptable forecast error band by business unit?

## 22) Implementation Blueprint (Recommended)
### Phase 1
- Build data fabric and canonical model
- Implement conversational analytics and anomaly triage

### Phase 2
- Add recommendation ranking, owner mapping, and workflow integrations

### Phase 3
- Add policy engine, shift-left checks, and advanced realization analytics

## 23) Source Notes
Research references used in this PRD synthesis:
- FinOps Foundation Principles: https://www.finops.org/framework/principles/
- FinOps Framework and Capabilities: https://www.finops.org/framework/ and https://www.finops.org/framework/capabilities/
- FinOps Agentic Use Cases Insight (2026): https://www.finops.org/insights/ai-for-finops-agentic-use-cases/
- FOCUS specification hub: https://focus.finops.org/
- AWS Cost Explorer: https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- AWS Cost Anomaly Detection: https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/
- AWS Cost and Usage Reports / Data Exports context: https://aws.amazon.com/aws-cost-management/aws-cost-and-usage-reporting/
- AWS Budgets: https://aws.amazon.com/aws-cost-management/aws-budgets/
- AWS Compute Optimizer: https://aws.amazon.com/compute-optimizer/
- AWS Savings Plans: https://aws.amazon.com/savingsplans/
- AWS Trusted Advisor: https://aws.amazon.com/premiumsupport/technology/trusted-advisor/

## 24) Final Recommendation
Proceed with an AWS-first, human-in-the-loop Optivue MVP focused on anomaly triage, ranked optimization recommendations, and action lifecycle tracking. This scope has the highest probability of near-term realized savings and the lowest operational risk while establishing the data and governance foundations needed for broader autonomous FinOps operations.

