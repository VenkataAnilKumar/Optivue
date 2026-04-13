# Optivue MVP Sprint Plan (12 Weeks)

## How to Use
- Sprint length: 2 weeks
- Total sprints: 6
- Status tags: Not Started, In Progress, Blocked, Done
- Use this file as your weekly execution tracker and interview evidence.

## Sprint 1 (Weeks 1-2): Scope, Foundation, and Platform Bootstrap
### Sprint Goal
Lock scope and stand up secure AWS foundation.

### Backlog
- [ ] Finalize P1 user stories from docs/05-user-stories.md
- [ ] Freeze MVP scope and non-goals
- [ ] Set KPI baseline and target metrics
- [ ] Initialize AWS CDK project structure
- [ ] Provision dev environment: Cognito, API Gateway, Lambda, DynamoDB, S3
- [ ] Configure IAM least privilege and Secrets Manager
- [ ] Set up CI pipeline skeleton (lint/test/deploy checks)

### Demo at Sprint End
- Show deployed API health endpoint with auth flow.

### Exit Criteria
- Dev environment deployable from CDK.
- Scope and KPI baseline signed off.

### Risks and Blockers
- IAM policy delays
- Missing access to cost data exports

---

## Sprint 2 (Weeks 3-4): Cost Intelligence APIs and Basic UI
### Sprint Goal
Deliver first user-facing value: spend Q and A plus anomaly explanation.

### Backlog
- [ ] Build Athena query module for spend by period/service/tag
- [ ] Integrate Cost Explorer adapter for trend summaries
- [ ] Integrate Cost Anomaly Detection adapter
- [ ] Create normalized data response schema
- [ ] Build Next.js query screen and response cards
- [ ] Add evidence and source fields in response
- [ ] Add basic API and UI tests

### Demo at Sprint End
- Ask: Why did cost increase this week?
- Show top cost drivers and one anomaly explanation.

### Exit Criteria
- Cost query and anomaly explanation flows work end-to-end.

### Risks and Blockers
- Data lag in source systems
- Incomplete tags reducing attribution quality

---

## Sprint 3 (Weeks 5-6): Recommendation Engine
### Sprint Goal
Generate and rank actionable savings recommendations.

### Backlog
- [ ] Integrate Compute Optimizer recommendation ingestion
- [ ] Integrate Trusted Advisor cost checks
- [ ] Add custom heuristic rules (idle and low utilization patterns)
- [ ] Implement recommendation ranking (savings, confidence, effort, risk)
- [ ] Persist recommendations in DynamoDB
- [ ] Build recommendation list and detail UI
- [ ] Add ranking logic unit tests

### Demo at Sprint End
- Show top 5 recommendations with savings estimate and confidence.

### Exit Criteria
- Ranked recommendation output available for pilot scope.

### Risks and Blockers
- High false positive recommendations
- Conflicting signals from multiple recommendation sources

---

## Sprint 4 (Weeks 7-8): Action Workflow and Approval Gate
### Sprint Goal
Complete insight-to-action workflow with safety controls.

### Backlog
- [ ] Implement explicit approval flow in API and UI
- [ ] Add Step Functions workflow for action orchestration
- [ ] Integrate Jira ticket creation adapter
- [ ] Integrate Slack/Teams notification adapter
- [ ] Store action history and status transitions
- [ ] Add audit log events for approvals and action outcomes
- [ ] Add integration tests for action pipeline

### Demo at Sprint End
- Approve recommendation -> create Jira ticket -> send Slack notification.

### Exit Criteria
- No action executes without explicit approval token.

### Risks and Blockers
- External API rate limits (Jira/Slack)
- Missing or invalid connector credentials

---

## Sprint 5 (Weeks 9-10): Quality, Safety, and Observability
### Sprint Goal
Harden product quality and operational visibility.

### Backlog
- [ ] Build CloudWatch dashboards and alarms
- [ ] Add structured logging and correlation IDs
- [ ] Add prompt/evaluation dataset and scoring run
- [ ] Execute safety tests for role access and approval requirements
- [ ] Tune ranking thresholds to reduce false positives
- [ ] Add fallback mode using fixture data for demo reliability
- [ ] Finalize KPI calculation module

### Demo at Sprint End
- Show observability dashboard and quality report.

### Exit Criteria
- P1 tests pass.
- Safety checks pass with zero violations.

### Risks and Blockers
- Evaluation instability across runs
- Latency regressions after feature additions

---

## Sprint 6 (Weeks 11-12): Pilot, Portfolio Packaging, and Final Demo
### Sprint Goal
Ship MVP and make portfolio interview-ready.

### Backlog
- [ ] Run pilot walkthrough on real or curated dataset
- [ ] Capture KPI snapshot: acceptance rate, triage time, identified vs realized savings
- [ ] Finalize docs pack and architecture diagram
- [ ] Record 5-7 minute demo video
- [ ] Complete README quick start and known limitations
- [ ] Add post-MVP roadmap notes

### Demo at Sprint End
- Full end-to-end product demo using scripted scenario.

### Exit Criteria
- MVP Definition of Done satisfied (see docs/08-implementation-roadmap-phases.md).
- Documentation complete and reproducible.

### Risks and Blockers
- Live integration instability during demo
- Scope creep in final week

---

## KPI Tracking Table
| KPI | Baseline | Target | Current | Notes |
| --- | --- | --- | --- | --- |
| Recommendation acceptance rate | 18% | >= 30% | 24% | Pilot dry-run with mock + partial real data |
| Recommendation completion rate | 8% | >= 20% | 12% | Dependent on ticket follow-through cadence |
| Anomaly triage time | 30 min | -15% | 24 min | Early gains from pre-filled anomaly context |
| Query latency P95 | 11.5s | <= 8s | 9.2s | Adapter caching in progress |
| Action safety violations | 0 | 0 | 0 | Approval gate enforced in all action flows |

## Weekly Status Update Template
- Week:
- Overall status: Green/Amber/Red
- Completed this week:
- In progress:
- Blockers:
- Help needed:
- Next week plan:

## Interview Narrative Template
- Problem solved:
- Why architecture choice is modern:
- How safety and governance were handled:
- Measurable outcomes achieved:
- What you would build next:

