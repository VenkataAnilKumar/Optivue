# Spoken Interview Scripts: Optivue

Two ready-to-speak scripts. Practice out loud. Time yourself. Aim for natural pacing — do not rush.

---

## Script A: 2-Minute Recruiter Screen

**Use when:** Phone or video recruiter screen, "tell me about a project you built."

**Target time:** 90–120 seconds

---

"I built a Optivue using AWS and Amazon Bedrock Agents.

The problem I was solving is that FinOps teams can see cloud cost issues in dashboards, but the actual work of investigating anomalies, prioritizing fixes, and routing actions to engineers is still slow and manual. That gap between insight and action is where a lot of savings potential gets lost.

So I built an end-to-end AI assistant that lets you ask cost questions in plain English — things like 'why did my AWS bill spike this week' — and get back an explanation, ranked savings recommendations, and then act on them directly. You can approve a recommendation, create a Jira ticket, and notify the owner in Slack, all from one interface. Every action requires an explicit approval so nothing touches production without a human check.

For the stack I used Next.js and TypeScript for the frontend, Python FastAPI on AWS Lambda for the backend, Amazon Bedrock Agents for AI orchestration, and AWS cost services like Cost Explorer, Anomaly Detection, and Athena-backed cost reports for data. Infrastructure is managed with AWS CDK and deployed through GitHub Actions.

In a pilot dry-run I got recommendation acceptance up to 24 percent against a baseline of 18, identified around 3,800 dollars monthly in optimization potential, and the P95 query response was 9 seconds working down toward an 8-second target.

I documented the full product from PRD and architecture to sprint plan and test evaluation — because I wanted this to demonstrate not just that I can build AI systems, but that I can ship products end-to-end."

---

## Script B: 5-Minute Technical Panel

**Use when:** Technical panel, hiring manager round, or portfolio walkthrough. "Walk us through a technical project you built."

**Target time:** 4.5–5.5 minutes

**Tip:** Pause naturally between sections. Invite questions after the architecture section if the panel is interactive.

---

### Opening — Problem and Context (30 seconds)

"I want to walk you through an end-to-end product I built called Optivue. The core problem is that cloud cost optimization consistently breaks at the handoff between analysis and execution. Teams have dashboards that show spend anomalies and savings opportunities, but the actual steps — figuring out the root cause, identifying the right owner, creating a ticket, following up — are manual and slow. I built a Bedrock-powered agent that closes that loop."

---

### What I Built — Core Capabilities (60 seconds)

"The MVP delivers five things.

First, natural language cost analysis. You can ask questions like 'show me the top cost drivers this month by team' and get a grounded response with evidence from Athena-backed cost data.

Second, anomaly explanation. When a spike is detected, the agent explains the likely drivers and suggests an owner candidate.

Third, ranked recommendations. The system pulls from Compute Optimizer, Trusted Advisor, and custom heuristics, ranks them by estimated savings, confidence, effort, and risk, and surfaces the top five.

Fourth, an approval gate. No action executes without explicit user confirmation. This was a deliberate governance decision — especially important for a tool that creates tickets and sends notifications on behalf of the user.

And fifth, action orchestration. Once approved, a Step Functions workflow creates the Jira ticket, sends the Slack or Teams notification, persists the lifecycle state in DynamoDB, and writes KPI events for reporting."

---

### Architecture — Stack and Data Flow (90 seconds)

"Let me walk through the architecture.

The frontend is Next.js 15 with TypeScript and Tailwind, hosted on AWS Amplify. Users authenticate through Amazon Cognito.

API calls go to a FastAPI application on Lambda behind API Gateway. The AI orchestration layer is Amazon Bedrock Agents with a supervisor-plus-specialist agent pattern. I use tool adapters — Lambda functions — as the interface between the Bedrock agent and AWS cost services like Cost Explorer, Anomaly Detection, and Compute Optimizer.

For data, I set up an Athena pipeline over S3-backed Data Exports and a Glue catalog. That gives the agent SQL-queryable access to detailed cost records.

For state I used DynamoDB to track recommendation status, approvals, and action history. For async workflows, Step Functions and EventBridge handle the action pipeline.

Infrastructure is entirely AWS CDK in TypeScript. GitHub Actions handles CI checks, linting, and deployment.

For observability I added CloudWatch dashboards, structured logging with correlation IDs, and a Bedrock trace path so you can see what tool calls the agent made for any given query."

---

### Engineering Decisions and Tradeoffs (60 seconds)

"A few decisions I want to highlight.

I chose Bedrock Agents over a custom orchestration loop because it gave me secure tool-calling, retry handling, and trace visibility out of the box. For an MVP with a limited team, that's a significant productivity advantage.

I chose serverless Lambda over containers for the backend because the access pattern is request-response, team size is small, and cold start latency was acceptable given I was caching adapter responses.

I made a deliberate choice not to build autonomous remediation in MVP — no automatic instance resizing or budget enforcement without a human in the loop. Trust and auditability matter more early on than automation breadth.

I also built in a fixture-data fallback path from day one so the demo flow is reliable regardless of live API availability during a presentation."

---

### Measurable Outcomes and What I Would Build Next (45 seconds)

"On outcomes — in a pilot dry-run, recommendation acceptance reached 24 percent against an 18 percent baseline, working toward a 30 percent target. I identified roughly 3,800 dollars monthly in optimization potential. P95 latency was 9.2 seconds. And zero unauthorized actions executed across all test runs — the approval gate held.

What I would build next: shift-left cost checks in IaC pull requests so teams catch waste before deploying, advanced forecasting and commitment optimization, and a FOCUS-aligned canonical schema to extend the model to multi-cloud data.

Happy to go deeper on any part — the agent architecture, ranking logic, safety controls, or the data pipeline."

---

## Delivery Tips

- **Pace:** Speak at 130–150 words per minute. Most people rush — slow down on the architecture section.
- **Pauses:** Pause visibly after "five things" and after the architecture walkthrough. It signals confidence.
- **Eye contact:** Look up when naming business outcomes. Look at notes when citing specific numbers.
- **Backup:** If asked to shorten, cut Script B to just Opening + Core Capabilities + Architecture + Outcomes. Skip tradeoffs.
- **If interrupted:** That is a good sign. Interviewers interrupt when they are interested. Answer the question fully, then offer to continue.

