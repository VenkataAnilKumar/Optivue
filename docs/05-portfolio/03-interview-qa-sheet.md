# Interview Q and A Sheet: Optivue

Use this sheet for recruiter screens, technical rounds, and system design interviews.

## 1) Recruiter and Hiring Manager Questions
### Q1. What problem does this project solve?
A. FinOps teams can see cost issues but often fail to execute remediation quickly. This project closes that gap by converting cost insights into approved actions, including ticket creation and owner notification.

### Q2. Why is this project valuable to a business?
A. It reduces investigation toil, improves optimization follow-through, and tracks identified versus realized savings so outcomes can be measured.

### Q3. What was your role?
A. I designed the product scope, selected the architecture, built key integration flows, and created delivery artifacts from PRD through sprint execution and evaluation.

### Q4. What did you ship in MVP?
A. Natural-language cost analysis, anomaly explanation, ranked recommendations, approval gate, Jira ticket creation, Slack/Teams notification, and lifecycle tracking.

## 2) Architecture and System Design Questions
### Q5. Why did you choose this stack?
A. I used Next.js plus TypeScript for modern UI, Python plus FastAPI for AI-friendly backend development, and AWS serverless services for scalable and low-ops execution. Bedrock Agents provided orchestration and tool-calling patterns aligned with the use case.

### Q6. How does data flow end to end?
A.
1. User asks a question in the web app.
2. Backend calls Bedrock Agent orchestration.
3. Tool adapters query Athena/Cost APIs.
4. Agent returns grounded analysis and recommendations.
5. User approval triggers Step Functions action workflow.
6. Jira ticket and Slack/Teams notification are sent.
7. Action status is stored and KPI metrics are updated.

### Q7. How did you ensure scalability?
A. The system uses stateless API functions on Lambda, asynchronous orchestration with Step Functions and EventBridge, and managed data services (S3, Athena, DynamoDB) that scale independently.

### Q8. How did you design for reliability?
A. I added graceful degradation for external integrations, retry patterns in action workflows, and fixture-data fallback for demo continuity.

## 3) AI and Agent Questions
### Q9. Why Bedrock Agents over a custom orchestration loop?
A. Bedrock Agents accelerate secure tool orchestration, reduce boilerplate, and provide a production-ready pattern for multi-step task execution.

### Q10. How do you prevent unsafe actions?
A. All mutation paths require explicit human approval. Role checks, least-privilege IAM, and auditable event logs enforce governance.

### Q11. How do you evaluate AI quality?
A. I use a test dataset for prompt scenarios and track acceptance rate, false positives, and anomaly explanation quality with a repeatable evaluation flow.

### Q12. How do you reduce hallucinations?
A. Responses include evidence and source context from cost data systems, plus confidence scoring and conservative thresholds for actions.

## 4) Security and Governance Questions
### Q13. How is security handled?
A. Authentication via Cognito, authorization through role-aware policy checks, secrets in Secrets Manager, and least-privilege IAM at every integration boundary.

### Q14. What about compliance and auditability?
A. Every approval and action transition is logged with actor and timestamp, enabling full audit trails and post-incident review.

## 5) Product and Delivery Questions
### Q15. How did you prioritize MVP scope?
A. I prioritized features that complete the insight-to-action loop and excluded autonomous remediation and multi-cloud complexity from MVP.

### Q16. How do you measure success?
A.
- Recommendation acceptance rate
- Recommendation completion rate
- Anomaly triage time reduction
- Identified versus realized savings
- Safety incidents (target zero)

### Q17. What tradeoffs did you make?
A. I traded broad feature coverage for strong execution quality on a narrow but high-value workflow. This improved demo reliability and interview clarity.

### Q18. What would you build next?
A.
1. Shift-left cost checks in IaC pull requests.
2. Advanced forecasting and commitment optimization.
3. Multi-cloud normalization with FOCUS-style schema.

## 6) Technical Deep-Dive Prompts You Should Practice
- Explain how you modeled recommendation confidence and ranking.
- Explain how your adapter layer isolates cloud APIs from business logic.
- Explain failure handling in Step Functions and notification retries.
- Explain how DynamoDB schema supports recommendation lifecycle and reporting.
- Explain why you chose serverless versus containerized runtime for MVP.

## 7) Behavioral Interview Framing
### STAR Story 1: Ambiguity to plan
- Situation: Broad FinOps optimization idea.
- Task: Convert into a job-ready, buildable MVP.
- Action: Produced PRD, architecture, roadmap, sprint plan, and KPI model.
- Result: Clear 12-week execution plan and interview-ready artifact set.

### STAR Story 2: Safety versus speed
- Situation: Need to automate actions without introducing production risk.
- Task: Balance automation and governance.
- Action: Implemented explicit approval gate and role-based control model.
- Result: Safe automation path with measurable delivery velocity.

### STAR Story 3: Business impact focus
- Situation: Optimization insights often not executed.
- Task: Improve realization, not just reporting.
- Action: Integrated Jira plus Slack workflows and lifecycle tracking.
- Result: Actionable path from recommendation to tracked execution.

## 8) 60-Second Project Pitch
I built a Optivue on AWS that turns cloud cost insights into approved engineering actions. It uses Bedrock Agents for orchestration, Athena and AWS cost services for grounded analysis, and Step Functions to route approved recommendations into Jira and Slack. The design is secure and auditable with role checks, approval gates, and lifecycle metrics so teams can track identified versus realized savings.

