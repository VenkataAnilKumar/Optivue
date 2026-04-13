# Demo Script (5-7 Minutes)

## 1. Demo Goal
Show end-to-end value:
- Ask cost question
- Explain anomaly
- Generate recommendation
- Approve action
- Create ticket and notify owner

## 2. Pre-Demo Checklist
- App running locally or deployed
- AWS credentials configured
- Sample dataset ready (fallback)
- Jira integration connected
- Slack/Teams integration connected

## 3. Script
### Step 1: Cost insight query
Prompt:
- Why did my AWS cost increase this week?
Expected output:
- Total delta
- Top cost drivers
- Affected services/accounts

### Step 2: Anomaly explanation
Prompt:
- Explain the highest anomaly from last 7 days.
Expected output:
- Impact amount
- Root cause hypothesis
- Suggested owner

### Step 3: Recommendation generation
Prompt:
- Show top 5 savings opportunities with impact and confidence.
Expected output:
- Ranked list with savings estimate and rationale

### Step 4: Approval and action
Action:
- Approve recommendation 1 for ticket creation.
Expected output:
- Confirmation required
- Jira ticket created with link

### Step 5: Notification
Action:
- Notify owner on Slack.
Expected output:
- Message sent confirmation

### Step 6: KPI snapshot
Show:
- Identified vs realized savings chart
- Recommendation status summary

## 4. Fallback Plan
If AWS/Jira/Slack integration fails:
- Use fixture data and mock connectors
- Continue flow to prove product behavior

## 5. References
- https://aws.amazon.com/bedrock/agents/
- https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling/bedrock-agents/test-agent
