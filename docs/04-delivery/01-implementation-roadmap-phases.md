# Optivue Implementation Roadmap (Multi-Phase)

## Roadmap Summary
- Product: Optivue MVP
- Duration: 12 weeks (MVP) + optional post-MVP expansion
- Approach: AWS-first, serverless-first, human-in-the-loop action model
- Primary outcome: move from cost insight to measurable savings actions

## Phase 0: Foundation and Scope (Week 1)
### Objective
Create a clear, measurable delivery baseline before writing production code.

### Key Activities
- Finalize MVP scope and non-goals.
- Lock top 10 user scenarios and P1 user stories.
- Confirm architecture and stack decisions.
- Define KPIs and baseline measurement method.
- Set repo standards, branch strategy, and CI checks.

### Entry Criteria
- Product brief and PRD Lite available.

### Exit Criteria
- Scope sign-off complete.
- KPI baseline documented.
- Architecture and security assumptions approved.

### Deliverables
- Scope sign-off note
- KPI baseline sheet
- Finalized architecture decision log

### Risks
- Scope creep early in project.
- Unclear success criteria.

### Mitigation
- Freeze MVP scope for 12-week cycle.
- Weekly change control review.

---

## Phase 1: Core Platform Setup (Weeks 2-3)
### Objective
Provision secure and deployable cloud foundation for the product.

### Key Activities
- Provision infra via AWS CDK.
- Set up Cognito, API Gateway, Lambda, DynamoDB, S3.
- Set up Glue catalog and Athena access path.
- Configure IAM least privilege and Secrets Manager.
- Set up environment tiers: dev and demo.

### Entry Criteria
- Phase 0 exit complete.
- AWS account and IAM permissions available.

### Exit Criteria
- Infrastructure deploys from pipeline successfully.
- Auth and API skeleton endpoints live.
- Security baseline checklist passes.

### Deliverables
- IaC repository structure
- Environment bootstrap scripts
- Security baseline checklist

### Risks
- IAM misconfiguration blocks progress.
- Environment drift between local and cloud.

### Mitigation
- Least-privilege templates and policy review.
- Mandatory IaC-only changes.

---

## Phase 2: Cost Intelligence MVP (Weeks 4-5)
### Objective
Deliver spend analysis and anomaly explanation as the first user-visible value.

### Key Activities
- Build cost query APIs over Athena and Cost Explorer.
- Integrate Cost Anomaly Detection ingestion and explanation.
- Normalize cost and anomaly payloads for downstream recommendation logic.
- Build initial chat plus dashboard views in Next.js.

### Entry Criteria
- Platform and auth live.

### Exit Criteria
- Top P1 query flows working end-to-end.
- Anomaly explanation returns impact, likely drivers, and owner candidate.

### Deliverables
- Cost insights API
- Anomaly explanation API
- Initial UI with query and results panel

### Risks
- Data completeness issues.
- Inconsistent tagging reducing owner mapping quality.

### Mitigation
- Add data quality checks and confidence scoring.
- Add fallback owner resolution rules.

---

## Phase 3: Recommendations Engine (Weeks 6-7)
### Objective
Turn analysis into prioritized savings opportunities.

### Key Activities
- Generate recommendations from Compute Optimizer, Trusted Advisor, and custom heuristics.
- Rank recommendations by savings, confidence, effort, and risk.
- Add rationale/evidence to recommendation cards.
- Persist recommendation lifecycle states in DynamoDB.

### Entry Criteria
- Cost and anomaly APIs stable.

### Exit Criteria
- Top 5 recommendations generated per evaluation run.
- Recommendation schema and evidence trace complete.

### Deliverables
- Recommendation service
- Scoring and ranking module
- Lifecycle state model

### Risks
- High false positive recommendations.
- Low confidence from incomplete metadata.

### Mitigation
- Add threshold controls and suppression.
- Introduce review feedback loop.

---

## Phase 4: Action Orchestration (Weeks 8-9)
### Objective
Complete insight-to-action workflow with safety controls.

### Key Activities
- Implement approval gate before action execution.
- Integrate Jira ticket creation.
- Integrate Slack/Teams owner notifications.
- Orchestrate actions with Step Functions and EventBridge.

### Entry Criteria
- Recommendations available and stable.

### Exit Criteria
- Approved recommendation creates ticket and sends notification.
- Every action has an auditable event trail.

### Deliverables
- Action orchestration workflow
- Jira adapter
- Slack/Teams adapter

### Risks
- Connector failures or API quota issues.
- Unsafe action execution path.

### Mitigation
- Retry and dead-letter handling.
- Block all writes without explicit approval token.

---

## Phase 5: Evaluation, Safety, Observability (Weeks 10-11)
### Objective
Validate quality and make product demo and pilot ready.

### Key Activities
- Set up CloudWatch dashboards, logs, and alarms.
- Add agent trace and evaluation harness.
- Run functional, integration, and safety tests.
- Tune prompts, ranking thresholds, and action policies.

### Entry Criteria
- Full flow from query to action available.

### Exit Criteria
- P1 test suite passes.
- Safety controls verified.
- KPI reporting ready for pilot run.

### Deliverables
- Test report
- Evaluation metrics summary
- Observability dashboard

### Risks
- Evaluation results inconsistent.
- Latency above desired threshold.

### Mitigation
- Cache stable lookup paths.
- Isolate and optimize slow adapters.

---

## Phase 6: Pilot and Portfolio Launch (Week 12)
### Objective
Launch MVP for pilot use and package project for interviews.

### Key Activities
- Execute guided pilot scenario with sample or real data.
- Capture KPI outcomes and lessons learned.
- Finalize docs and architecture diagram.
- Record 5-7 minute product demo.

### Entry Criteria
- Testing and observability pass from Phase 5.

### Exit Criteria
- Pilot walkthrough completed successfully.
- Portfolio pack is complete and reproducible.

### Deliverables
- Demo video
- Final README and doc pack
- KPI outcome snapshot

### Risks
- Demo instability due to live dependency outages.

### Mitigation
- Keep fixture-data fallback mode and scripted demo path.

---

## Post-MVP Phase 7: Expansion (Optional)
### Objective
Move from MVP to advanced capability and stronger production posture.

### Candidate Enhancements
- Shift-left FinOps checks in IaC pull requests.
- Advanced forecasting and confidence intervals.
- Commitment optimization automation for Savings Plans.
- Executive views and unit economics scorecards.
- Multi-cloud ingestion using FOCUS-aligned model.

---

## KPI Targets by End of MVP
- Recommendation acceptance rate: >= 30%
- Recommendation completion rate: >= 20%
- Anomaly triage time reduction: >= 15%
- Standard query response latency P95: <= 8 seconds
- Action safety violations: 0

## Governance Cadence
- Daily: ingestion health and anomaly queue checks.
- Weekly: recommendation review with FinOps + engineering.
- Monthly: identified vs realized savings and roadmap reprioritization.

## Dependencies
- AWS account with Bedrock and cost tools access.
- Jira and Slack/Teams integration credentials.
- Defined ownership model (tags, cost center, team mapping).
- Sample dataset for fallback demo mode.

## Definition of MVP Done
- User can ask cost questions and get grounded responses.
- User can view anomalies and ranked recommendations.
- User can approve and trigger ticket plus notification workflow.
- System tracks recommendation lifecycle and basic realized savings metrics.
- Documentation and demo assets are complete for interview showcase.

