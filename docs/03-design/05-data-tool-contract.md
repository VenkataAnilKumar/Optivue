# Data and Tool Contract

## 1. Canonical Cost Record
Example fields:
- provider
- account_id
- service
- region
- usage_start_time
- usage_end_time
- blended_cost
- unblended_cost
- tags (product, environment, owner)

Example JSON:
```json
{
	"provider": "aws",
	"account_id": "123456789012",
	"service": "AmazonEC2",
	"region": "us-east-1",
	"usage_start_time": "2026-04-10T00:00:00Z",
	"usage_end_time": "2026-04-10T01:00:00Z",
	"blended_cost": 12.45,
	"unblended_cost": 13.02,
	"tags": {
		"product": "payments-api",
		"environment": "prod",
		"owner": "team-payments"
	}
}
```

## 2. Anomaly Event Contract
Input:
- anomaly_id
- start_time
- end_time
- impact_amount
- monitor_scope

Output:
- root_cause_summary
- likely_drivers[]
- likely_owner
- severity

Example JSON:
```json
{
	"anomaly_id": "an-1042",
	"root_cause_summary": "EC2 On-Demand spike in us-east-1",
	"likely_drivers": [
		"New c7i.4xlarge instances",
		"Auto Scaling min capacity increase"
	],
	"likely_owner": "team-payments",
	"severity": "high"
}
```

## 3. Recommendation Contract
- recommendation_id
- type (rightsizing/idle/commitment/tagging)
- estimated_monthly_savings
- confidence_score
- effort_level (low/medium/high)
- risk_level (low/medium/high)
- priority_score (0.00–1.00, weighted composite)
- priority_tier (P1/P2/P3)
- suggested_owner
- recommended_due_date
- needs_review (true if confidence < threshold)
- rationale
- evidence_refs[]

### Priority Scoring Formula
priority_score = (estimated_savings_normalized × 0.35) + (confidence_score × 0.20) + ((1 − effort_normalized) × 0.20) + ((1 − risk_normalized) × 0.15) + (strategic_alignment_score × 0.10)

Where:
- estimated_savings_normalized = min(estimated_monthly_savings / 1000, 1.0)
- effort_normalized: low=0.2, medium=0.5, high=0.9
- risk_normalized: low=0.1, medium=0.5, high=0.9
- strategic_alignment_score: default 0.5 (overridden by governance policy tags)

Priority tier assignment:
- P1: priority_score >= 0.70
- P2: priority_score 0.40–0.69
- P3: priority_score < 0.40

Example JSON:
```json
{
	"recommendation_id": "rec-2026-0041",
	"type": "rightsizing",
	"estimated_monthly_savings": 842.15,
	"confidence_score": 0.83,
	"effort_level": "medium",
	"risk_level": "low",
	"priority_score": 0.74,
	"priority_tier": "P1",
	"suggested_owner": "team-payments",
	"recommended_due_date": "2026-05-01",
	"needs_review": false,
	"rationale": "CPU p95 below 18% for 14 days",
	"evidence_refs": [
		"athena://cost_usage/ec2_utilization",
		"compute-optimizer://instance/i-0abc123"
	]
}
```

## 4. Action Contract: Create Ticket
Request:
- recommendation_id
- owner
- summary
- acceptance_criteria

Response:
- ticket_id
- ticket_url
- status

Example JSON:
```json
{
	"ticket_id": "FINOPS-214",
	"ticket_url": "https://your-domain.atlassian.net/browse/FINOPS-214",
	"status": "created"
}
```

## 5. Action Contract: Notify Owner
Request:
- channel
- owner
- message
- recommendation_id

Response:
- delivery_status
- message_id

Example JSON:
```json
{
	"delivery_status": "sent",
	"message_id": "slack-17011223344"
}
```

## 6. Approval Contract
Request:
- action_type
- action_payload
- approver

Response:
- approved (true/false)
- approval_timestamp
- reason

Example JSON:
```json
{
	"approved": true,
	"approval_timestamp": "2026-04-13T10:22:00Z",
	"reason": "Low-risk rightsizing approved"
}
```

## 7. FOCUS Field Mapping

FOCUS (FinOps Open Cost and Usage Specification) normalization for multi-cloud future-proofing.
The canonical cost record maps to FOCUS columns as follows:

| Canonical Field | FOCUS Column | Notes |
|----------------|-------------|-------|
| provider | BillingAccountProvider | "aws", "azure", "gcp" |
| account_id | SubAccountId | AWS Account ID |
| service | ServiceName | e.g. "Amazon EC2" |
| region | RegionName | e.g. "us-east-1" |
| usage_start_time | ChargePeriodStart | ISO8601 UTC |
| usage_end_time | ChargePeriodEnd | ISO8601 UTC |
| blended_cost | BilledCost | Blended rate applied |
| unblended_cost | EffectiveCost | On-demand / unblended |
| tags.product | x-product | Custom dimension tag |
| tags.environment | x-environment | Custom dimension tag |
| tags.owner | x-owner | Custom dimension tag |
| service (SKU) | ServiceCategory | Broad category grouping |
| region | AvailabilityZone | AZ-level when available |

AWS CUR → FOCUS reference: https://focus.finops.org/

For MVP, retain source-native CUR fields alongside FOCUS-mapped fields in Athena.
Full FOCUS compliance (all 40+ columns) is deferred to Post-MVP multi-cloud expansion.

## 8. Reference APIs
AWS docs:
- https://aws.amazon.com/aws-cost-management/aws-cost-explorer/
- https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/
- https://aws.amazon.com/compute-optimizer/
- https://aws.amazon.com/aws-cost-management/aws-budgets/

Code references:
- https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-and-function-calling
