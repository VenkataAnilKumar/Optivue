# Database Schema

## Overview
The Optivue uses Amazon DynamoDB for operational state — recommendation lifecycle,
approval records, action history, and KPI metrics. S3 + Athena handles the analytical
cost data (read via CUR/Data Exports).

---

## Table 1: Recommendations

### Purpose
Stores each recommendation's full payload, current lifecycle state, and metadata.

### Table Name
`finops-recommendations`

### Key Design
| Key | Attribute | Type | Description |
|-----|-----------|------|-------------|
| Partition Key | `pk` | String | `REC#{recommendation_id}` |
| Sort Key | `sk` | String | `METADATA` |

### GSI 1: by-owner-status-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `owner` |
| Sort Key | `status` |
Purpose: query all open recommendations for a specific team or owner.

### GSI 2: by-priority-created-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `priority_tier` |
| Sort Key | `created_at` |
Purpose: query P1 recommendations sorted by creation date for analyst queue.

### Attributes

```json
{
  "pk": "REC#rec-2026-0041",
  "sk": "METADATA",
  "recommendation_id": "rec-2026-0041",
  "type": "rightsizing",
  "estimated_monthly_savings": 842.15,
  "confidence_score": 0.83,
  "priority_score": 0.74,
  "priority_tier": "P1",
  "effort_level": "medium",
  "risk_level": "low",
  "rationale": "CPU p95 below 18% for 14 days",
  "evidence_refs": [
    "athena://cost_usage/ec2_utilization",
    "compute-optimizer://instance/i-0abc123"
  ],
  "suggested_owner": "team-payments",
  "recommended_due_date": "2026-05-01",
  "status": "open",
  "needs_review": false,
  "environment": "prod",
  "account_id": "123456789012",
  "resource_id": "i-0abc123",
  "service": "AmazonEC2",
  "region": "us-east-1",
  "created_at": "2026-04-13T09:00:00Z",
  "updated_at": "2026-04-13T09:00:00Z",
  "ttl": 1775462400
}
```

### Status Lifecycle
`open` → `acknowledged` → `in_progress` → `completed` | `dismissed`

### TTL
- Set to 90 days from `created_at` for dismissed recommendations.
- No TTL for completed recommendations (retained for realized savings reporting).

---

## Table 2: Recommendation History

### Purpose
Immutable audit trail of all status transitions on a recommendation.

### Table Name
`finops-recommendations` (same table, different SK pattern)

### Key Design
| Key | Attribute | Type | Description |
|-----|-----------|------|-------------|
| Partition Key | `pk` | String | `REC#{recommendation_id}` |
| Sort Key | `sk` | String | `HISTORY#{iso8601_timestamp}` |

### Attributes

```json
{
  "pk": "REC#rec-2026-0041",
  "sk": "HISTORY#2026-04-13T10:22:00Z",
  "previous_status": "open",
  "new_status": "acknowledged",
  "actor": "user@example.com",
  "actor_role": "engineering-manager",
  "comment": "Assigned to sprint 42",
  "timestamp": "2026-04-13T10:22:00Z"
}
```

---

## Table 3: Approvals

### Purpose
Stores approval requests, their status, and the approval tokens used to authorize actions.

### Table Name
`finops-approvals`

### Key Design
| Key | Attribute | Type | Description |
|-----|-----------|------|-------------|
| Partition Key | `pk` | String | `APPROVAL#{approval_request_id}` |
| Sort Key | `sk` | String | `METADATA` |

### GSI 1: by-recommendation-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `recommendation_id` |
| Sort Key | `created_at` |
Purpose: look up all approval requests for a given recommendation.

### GSI 2: by-status-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `status` |
| Sort Key | `created_at` |
Purpose: query all pending approvals for dashboard view.

### Attributes

```json
{
  "pk": "APPROVAL#apr-2026-0017",
  "sk": "METADATA",
  "approval_request_id": "apr-2026-0017",
  "recommendation_id": "rec-2026-0041",
  "action_type": "rightsizing",
  "action_payload": {
    "resource_id": "i-0abc123",
    "current_instance_type": "c7i.4xlarge",
    "recommended_instance_type": "c7i.xlarge"
  },
  "risk_level": "low",
  "blast_radius": "Single EC2 instance in prod/payments-api",
  "rollback_path": "Resize back to c7i.4xlarge via console or CLI within 30 minutes",
  "approver_role": "engineering-manager",
  "dual_approval_required": false,
  "status": "pending",
  "approval_token": null,
  "approver": null,
  "approval_timestamp": null,
  "reason": null,
  "requested_by": "user@example.com",
  "created_at": "2026-04-13T10:00:00Z",
  "expires_at": "2026-04-13T14:00:00Z",
  "ttl": 1744574400
}
```

### TTL
- Set to 24 hours from `expires_at` for expired/denied approvals.
- Approved approvals retained for 90 days for audit purposes.

---

## Table 4: Action History

### Purpose
Immutable log of every action executed (ticket creation, notification, resource mutation).
This is the primary audit table for governance and compliance.

### Table Name
`finops-action-history`

### Key Design
| Key | Attribute | Type | Description |
|-----|-----------|------|-------------|
| Partition Key | `pk` | String | `ACTION#{action_id}` |
| Sort Key | `sk` | String | `METADATA` |

### GSI 1: by-recommendation-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `recommendation_id` |
| Sort Key | `executed_at` |

### GSI 2: by-actor-date-index
| Key | Attribute |
|-----|-----------|
| Partition Key | `actor` |
| Sort Key | `executed_at` |

### Attributes

```json
{
  "pk": "ACTION#act-2026-0091",
  "sk": "METADATA",
  "action_id": "act-2026-0091",
  "action_type": "create_ticket",
  "recommendation_id": "rec-2026-0041",
  "approval_request_id": "apr-2026-0017",
  "approval_token": "tok-abc123xyz",
  "actor": "user@example.com",
  "actor_role": "finops-analyst",
  "payload": {
    "ticket_id": "FINOPS-214",
    "ticket_url": "https://your-domain.atlassian.net/browse/FINOPS-214",
    "owner": "team-payments"
  },
  "result": "success",
  "error_message": null,
  "executed_at": "2026-04-13T10:22:05Z",
  "step_functions_execution_arn": "arn:aws:states:us-east-1:123456789012:execution:finops-action-workflow:exec-0041"
}
```

### Notes
- This table is append-only. No items are ever updated or deleted.
- TTL is not set — retained indefinitely for compliance.

---

## Table 5: KPI Metrics

### Purpose
Stores weekly and monthly computed KPI snapshots for reporting dashboards.

### Table Name
`finops-kpi-metrics`

### Key Design
| Key | Attribute | Type | Description |
|-----|-----------|------|-------------|
| Partition Key | `pk` | String | `KPI#{metric_type}` |
| Sort Key | `sk` | String | `PERIOD#{YYYY-MM}` or `PERIOD#{YYYY-WW}` |

### Attributes

```json
{
  "pk": "KPI#recommendation_acceptance_rate",
  "sk": "PERIOD#2026-04",
  "metric_type": "recommendation_acceptance_rate",
  "period": "2026-04",
  "period_type": "monthly",
  "value": 0.34,
  "numerator": 17,
  "denominator": 50,
  "target": 0.30,
  "status": "on_target",
  "scope": "all",
  "computed_at": "2026-05-01T00:05:00Z"
}
```

### Tracked Metrics (pk values)
| Metric Key | Description | Target |
|------------|-------------|--------|
| `recommendation_acceptance_rate` | Accepted / Total recommendations | >= 0.30 |
| `recommendation_completion_rate` | Completed / Accepted recommendations | >= 0.20 |
| `anomaly_triage_time_minutes` | Median minutes from detection to owner routing | <= 5 |
| `identified_savings_usd` | Sum of estimated savings for open+accepted recs | Tracked |
| `realized_savings_usd` | Sum of verified savings from completed recs | Tracked |
| `false_positive_recommendation_rate` | Dismissed / Total recommendations | <= 0.15 |
| `action_safety_violations` | Actions executed without valid approval token | 0 |
| `tagged_cost_coverage_pct` | Cost with required tags / Total cost | Increasing |

---

## Access Pattern Summary

| Access Pattern | Table | Key Strategy |
|----------------|-------|--------------|
| Get recommendation by ID | finops-recommendations | pk=REC#{id}, sk=METADATA |
| Get all recs for an owner | finops-recommendations | GSI1: owner + status |
| Get P1 recs by date | finops-recommendations | GSI2: priority_tier + created_at |
| Get history for a rec | finops-recommendations | pk=REC#{id}, sk begins_with HISTORY# |
| Get approval by ID | finops-approvals | pk=APPROVAL#{id}, sk=METADATA |
| Get all pending approvals | finops-approvals | GSI2: status=pending |
| Get approval for a rec | finops-approvals | GSI1: recommendation_id |
| Get action history for a rec | finops-action-history | GSI1: recommendation_id |
| Get monthly KPI | finops-kpi-metrics | pk=KPI#{metric}, sk=PERIOD#{YYYY-MM} |

---

## CDK Construct Notes

```typescript
// Example CDK table definition for finops-recommendations
const recommendationsTable = new dynamodb.Table(this, 'RecommendationsTable', {
  tableName: 'finops-recommendations',
  partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  encryption: dynamodb.TableEncryption.AWS_MANAGED,
  pointInTimeRecovery: true,
  timeToLiveAttribute: 'ttl',
});

recommendationsTable.addGlobalSecondaryIndex({
  indexName: 'by-owner-status-index',
  partitionKey: { name: 'owner', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'status', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});

recommendationsTable.addGlobalSecondaryIndex({
  indexName: 'by-priority-created-index',
  partitionKey: { name: 'priority_tier', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});
```

---

## References
- DynamoDB single-table design patterns: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- DynamoDB CDK construct: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_dynamodb.Table.html

