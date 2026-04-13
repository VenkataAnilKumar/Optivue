# Optivue — Next Phases Roadmap (Post-MVP)

**Date:** April 13, 2026  
**Status:** Planning  
**Reference:** [Build a FinOps agent using Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/build-a-finops-agent-using-amazon-bedrock-agentcore/) (March 31, 2026)

---

## Context: What the AWS Blog Introduces

The AWS ML blog published a reference FinOps agent architecture using the new **Amazon Bedrock AgentCore** platform. This introduces several capabilities that Optivue should adopt in its next development cycle.

| Capability | Current Optivue (MVP) | AWS AgentCore Reference |
|---|---|---|
| Agent runtime | Classic Bedrock Agents + Lambda action groups | **AgentCore Runtime** (container-based, OCI) |
| Agent framework | Custom supervisor + 3 specialist agents | **Strands Agent SDK** (open-source Python) |
| Tool protocol | Custom action group schemas (OpenAPI) | **MCP servers** (AWS Labs Billing + Pricing MCP) |
| Conversation memory | Session-scoped only | **AgentCore Memory** (30-day persistent context) |
| Tool auth | API Gateway SigV4 | **AgentCore Gateway + AgentCore Identity** (OAuth 2.0 M2M) |
| Model | Bedrock Agents default routing | **Claude Sonnet 4.5** explicit |
| Tool surface | ~8 custom adapters | **24 tools** across Billing + Pricing MCP servers |

---

## Recommended Phase Sequence

```
Phase 8  — AWS Deploy + Go-Live                      ← Complete (see 06-aws-deploy-runbook.md)
    ↓
Phase 9  — AgentCore Migration + MCP Adoption        ← Start here
    ↓
Phase 10 — Multi-Account and Org-Level Intelligence
    ↓
Phase 11 — Commitment Optimization Automation
    ↓
Phase 12 — Shift-Left FinOps (IaC Cost Gates)
    ↓
Phase 13 — Knowledge Base / RAG for Policy Docs
    ↓
Phase 14 — Multi-Cloud with FOCUS Alignment
```

---

## Phase 9 — AgentCore Migration + MCP Adoption

**Effort:** 3–4 weeks  
**Priority:** P1 — Highest leverage gain  
**Reference Implementation:** [github.com/aws-samples/sample-finops-agent-amazon-bedrock-agentcore](https://github.com/aws-samples/sample-finops-agent-amazon-bedrock-agentcore)

### Objective

Replace the classic Bedrock Agents + Lambda action-group pattern with the AgentCore Runtime + MCP stack, gaining 24 pre-built cost tools while preserving Optivue's human-in-the-loop approval model.

### Architecture Changes

The blog deploys five CloudFormation stacks. Optivue should mirror this structure:

| New CDK Stack | Replaces | Purpose |
|---|---|---|
| `FinOpsAuthStack` | Existing Cognito config in FinOpsFoundation | Cognito User Pool, Identity Pool, M2M client, resource server |
| `FinOpsImageStack` | N/A (new) | CodeBuild pipeline to build MCP server container images → ECR |
| `FinOpsMCPRuntimeStack` | FinOpsAgent (3 specialist agents) | Two AgentCore Runtimes: Billing MCP + Pricing MCP servers |
| `FinOpsAgentCoreGatewayStack` | FinOpsApi (action group routing) | AgentCore Gateway with IAM auth + OAuth credential provider |
| `FinOpsAgentRuntimeStack` | FinOpsAgent (supervisor) | Main Strands agent on AgentCore Runtime + AgentCore Memory |

### Agent Architecture

```
User
  └── Frontend (Next.js / Amplify)
        └── InvokeAgentRuntime (IAM SigV4)
              └── AgentCore Runtime [Strands Agent + Claude Sonnet 4.5]
                    ├── AgentCore Memory  (30-day conversation context)
                    └── InvokeGateway
                          └── AgentCore Gateway
                                ├── AgentCore Identity (OAuth 2.0 token exchange)
                                ├── Billing MCP Runtime  (14 tools)
                                │     └── Cost Explorer, Budgets, Compute Optimizer
                                └── Pricing MCP Runtime  (10 tools)
                                      └── AWS Price List API
```

Optivue's approval gate is preserved as a **custom MCP tool** registered in the  
`FinOpsAgentCoreGatewayStack` that calls the existing Step Functions workflow.

### Key Activities

- [ ] Fork and adapt `sample-finops-agent-amazon-bedrock-agentcore` CDK stacks into `src/infra/lib/stacks/`
- [ ] Build Strands agent with custom `approve_recommendation` and `create_ticket` tools wrapping existing Step Functions ARN
- [ ] Configure AgentCore Memory with `sessionId` tied to Cognito `sub` claim
- [ ] Replace `ai-agent` Lambda adapter invocations with `InvokeAgentRuntime` in FastAPI routes
- [ ] Update `src/frontend` to pass Cognito Identity Pool credentials to `InvokeAgentRuntime`
- [ ] Add Container image build pipeline (CodeBuild + ECR) for MCP server images (ARM64 Graviton)
- [ ] Remove or archive: `src/backend/adapters/cost/`, `adapters/optimization/`, `adapters/governance/` after confirming MCP tool coverage
- [ ] Update CDK `bin/app.ts` stack order to match new dependency graph

### MCP Server Tool Inventory (24 tools)

**Billing and Cost Management MCP Server:**
- `get_cost_and_usage` — spend by service/region/tag/period
- `get_cost_forecast` — projected spend with confidence interval
- `get_anomalies` — cost anomaly detection results
- `get_anomaly_monitors` — active anomaly monitor configs
- `get_rightsizing_recommendations` — EC2 rightsizing candidates
- `get_savings_plans_recommendations` — Savings Plans purchase suggestions
- `get_savings_plans_utilization` — current Savings Plans coverage
- `get_reservation_recommendations` — Reserved Instance suggestions
- `get_reservation_utilization` — RI coverage and utilization
- `get_compute_optimizer_recommendations` — cross-service compute optimization
- `get_budgets` — budget list with current spend vs. threshold
- `get_budget_notifications` — active budget alerts
- `get_cost_categories` — cost allocation rules
- `get_tags` — CUR dimension values for filtering

**Pricing MCP Server:**
- `get_products` — real-time pricing for any AWS service/region
- `get_services` — AWS service list with pricing attributes
- `get_attribute_values` — valid values for pricing filters
- `describe_services` — service metadata for cost estimation
- `get_price_list_file_url` — bulk price list download
- `estimate_ec2_cost` — monthly cost estimate for EC2 configuration
- `compare_instance_pricing` — side-by-side instance type comparison
- `get_spot_price_history` — EC2 Spot pricing trends
- `get_savings_plans_offerings` — available Savings Plans products
- `get_reserved_instance_offerings` — RI marketplace listings

### Exit Criteria

- [ ] All 24 MCP tools respond correctly in integration tests
- [ ] Approval gate preserved: no action executes without approval token
- [ ] AgentCore Memory retains context across session breaks (verified by follow-up question test)
- [ ] P95 standard query latency ≤ 8s
- [ ] All existing backend pytest and frontend vitest tests pass

---

## Phase 10 — Multi-Account and Org-Level Intelligence

**Effort:** 3 weeks  
**Priority:** P1 — Core enterprise differentiator

### Objective

Extend Optivue from single-account to AWS Organizations scope, enabling cross-account cost visibility, ownership attribution, and org-level anomaly correlation.

### Key Activities

- [ ] Enable consolidated billing CUR export at payer (management) account level
- [ ] Add `account_id`, `account_name`, `ou_path` dimensions to all Athena query templates
- [ ] Build `organization_service.py` — fetches org tree (Accounts, OUs) via `organizations:ListAccounts`
- [ ] Tag-based ownership resolver: `product` tag → team slug → `finops-recommendations` owner field
- [ ] Leadership dashboard: org rollup with unit economics (CPAU, CPT, CPS) — weekly KPI snapshots to `finops-kpi-metrics`
- [ ] Multi-account anomaly correlation: flag anomalies present across >1 linked account as "org-wide"
- [ ] Account-scoped RBAC: `engineering-manager` sees only their team's accounts

### Data Model Changes

```
finops-kpi-metrics (existing table)
  Add: account_id (GSI partition key for per-account queries)
  Add: ou_path (for OU-level rollups)
  Add: cpau, cpt, cps (unit economics fields)
```

### Exit Criteria

- [ ] Query "Show me costs for the data-platform team" routes to correct linked accounts
- [ ] `engineering-manager` role cannot see accounts outside their team tag
- [ ] KPI dashboard displays org-level CPAU, CPT, CPS on the leadership view
- [ ] Org-wide anomaly correctly identified as multi-account in response

---

## Phase 11 — Commitment Optimization Automation

**Effort:** 2–3 weeks  
**Priority:** P1 — Direct realized savings impact

### Objective

Automate the analysis and safe execution of Savings Plans and Reserved Instance purchases, with dual-approval controls per the existing approval matrix.

### Key Activities

- [ ] **Savings Plans analyzer** — pull `GetSavingsPlansPurchaseRecommendation`, model 1-year vs 3-year tradeoffs with projected savings and confidence intervals
- [ ] **Reserved Instances recommender** — EC2, RDS, ElastiCache coverage gap analysis
- [ ] New recommendation type: `commitment_purchase` with `risk = medium`, `effort = low`
- [ ] Approval workflow: `finops-analyst + finance` dual-approval (per approval matrix in `copilot-instructions.md`)
- [ ] Commitment purchase execution step in Step Functions: `purchase_savings_plan` Lambda adapter with idempotency key
- [ ] Realized savings tracker: compare committed vs actual spend week-over-week in `finops-kpi-metrics`
- [ ] Rollback handling: flag purchase as `policy_blocked` if environment check fails

### Approval Matrix Entry (new row)

| Environment | Action Type | Approvers | Mode |
|---|---|---|---|
| prod | commitment_purchase | finops-analyst + finance | dual |

### Exit Criteria

- [ ] Savings Plan recommendation card shows: coverage gap, projected savings, confidence score, 1yr vs 3yr comparison
- [ ] Purchase attempt without dual approval returns `policy_blocked`
- [ ] Realized savings appear in KPI dashboard within 7 days of commitment activation
- [ ] Idempotency verified: duplicate purchase request returns existing record, not new purchase

---

## Phase 12 — Shift-Left FinOps (IaC Cost Gates)

**Effort:** 2 weeks  
**Priority:** P2 — Prevention over remediation

### Objective

Intercept cost increases before they reach production by running cost estimation on every IaC pull request.

### Architecture

```
GitHub PR (CDK/Terraform/CloudFormation change)
    └── GitHub Actions: cost-gate.yml
          └── POST /api/cost-gate/estimate
                └── Pricing MCP Server
                      └── AWS Price List API
                            └── Cost delta comment posted on PR
                                  └── Block merge if delta > budget threshold
```

### Key Activities

- [ ] GitHub Actions workflow `cost-gate.yml`: triggers on `paths: ['src/infra/**', '**/*.tf', '**/*.cfn.yaml']`
- [ ] New FastAPI route `POST /api/cost-gate/estimate` — accepts diff of IaC changes, calls Pricing MCP tools
- [ ] Parse CDK/Terraform diff for new/modified resource types + configurations
- [ ] Call `estimate_ec2_cost`, `get_products`, `compare_instance_pricing` tools for each changed resource
- [ ] Post PR comment: table of resource changes, estimated monthly delta, flagged items > threshold
- [ ] Governance-agent new action group: `evaluate_pr_cost_impact` wrapping the estimate endpoint
- [ ] Team-level budget thresholds stored in `finops-kpi-metrics` table under `CONFIG#` prefix

### Exit Criteria

- [ ] PR adding a new `m5.4xlarge` instance triggers comment with estimated monthly cost
- [ ] PR exceeding team's monthly budget delta threshold sets PR check to failed state
- [ ] PR with no resource changes passes cost gate in < 10s

---

## Phase 13 — Knowledge Base / RAG for Policy Docs

**Effort:** 2–3 weeks  
**Priority:** P2 — Post-MVP Phase 7 backlog item now unblocked by AgentCore

### Objective

Ground recommendations in organization-specific FinOps policies, tagging standards, and cost allocation rules (not just AWS best practices).

### Architecture

```
Ingestion (weekly):
  S3 bucket (policy docs, tagging standards)
    └── Bedrock Knowledge Base (OpenSearch Serverless vector store)
          └── Chunking + embedding (Titan Text Embeddings v2)

Query path:
  Strands agent → RetrieveAndGenerate API
    └── Policy citations appended to recommendation rationale
```

### Key Activities

- [ ] Create `FinOpsKnowledgeBaseStack` CDK stack: S3 data source + OpenSearch Serverless collection + Bedrock Knowledge Base
- [ ] Ingestion pipeline: EventBridge weekly trigger → Lambda → `StartIngestionJob`
- [ ] Documents to ingest: tagging policy, cost allocation rules, FinOps team runbooks, approved instance families list
- [ ] Strands agent system prompt: instruct agent to always retrieve policy context before generating a recommendation
- [ ] Recommendation card: add `policy_citations[]` field with source doc + chunk reference
- [ ] `finops-recommendations` DynamoDB schema update: add `policy_citations` attribute

### Exit Criteria

- [ ] "Is this EC2 instance compliant with tagging policy?" returns a response citing the actual policy document
- [ ] Recommendation rationale includes `policy_citations` with doc name and relevant passage
- [ ] Ingestion job completes in < 5 minutes for a 50-document corpus

---

## Phase 14 — Multi-Cloud with FOCUS Alignment

**Effort:** 4–6 weeks  
**Priority:** P3 — Long-term platform play

### Objective

Make Optivue cloud-agnostic by adopting the [FOCUS specification](https://focus.finops.org/) (FinOps Open Cost and Usage Specification) as the canonical data model, enabling AWS, Azure, and GCP cost data in a single query surface.

### Architecture

```
Cloud Providers
  ├── AWS CUR 2.0 (native FOCUS export)
  ├── Azure Cost Management (FOCUS export)
  └── GCP Billing Export (FOCUS-aligned transform)
        ↓
  S3 landing zone
        ↓
  AWS Glue ETL (FOCUS normalization + validation)
        ↓
  Athena (single FOCUS-aligned table: finops_cost_focus)
        ↓
  Optivue query layer (unchanged — queries use FOCUS dimensions)
```

### FOCUS Canonical Dimensions

All queries standardized on:
- `BillingAccountId`, `SubAccountId`
- `Provider` (AWS / Azure / GCP)
- `ServiceName`, `ServiceCategory`
- `RegionName`, `AvailabilityZone`
- `ResourceId`, `ResourceType`, `ResourceTags`
- `BilledCost`, `EffectiveCost`, `ListCost`
- `ChargePeriodStart`, `ChargePeriodEnd`

### Key Activities

- [ ] Enable AWS CUR 2.0 FOCUS-format export in `FinOpsDataStack`
- [ ] Glue job: Azure Cost Management export → FOCUS normalization
- [ ] Glue job: GCP Billing export → FOCUS normalization
- [ ] Recreate Athena views using FOCUS column names
- [ ] Update all adapter query templates to use FOCUS dimensions
- [ ] Add `provider` filter to all recommendation cards and anomaly reports
- [ ] Update UI: provider selector in query bar, provider badge on cost cards

### Exit Criteria

- [ ] "Show me top 5 cost drivers across all clouds this month" returns a unified ranked list
- [ ] Anomaly detected on Azure appears in the same anomaly feed as AWS anomalies
- [ ] All existing AWS query tests pass against FOCUS-schema Athena tables

---

## KPI Targets by Phase

| Phase | Key Metric | Target |
|---|---|---|
| Phase 9 | Tool coverage (MCP vs custom adapters) | 24 tools vs 8 — 3× increase |
| Phase 9 | Conversation memory retention | Follow-up questions answered without re-asking context |
| Phase 10 | Multi-account query accuracy | 100% — no cross-account data leakage |
| Phase 11 | Annual commitment savings identified | >$10K/month per pilot account |
| Phase 11 | Dual-approval enforcement | 0 commitment purchases without both approvals |
| Phase 12 | PR cost gate latency | <10s P95 |
| Phase 12 | Cost increases caught pre-merge | Track % of cost-increasing PRs flagged |
| Phase 13 | Policy citation accuracy | >80% relevance score on manual eval |
| Phase 14 | Cross-cloud query coverage | AWS + Azure + GCP in single response |

---

## Dependencies

| Phase | Dependency |
|---|---|
| Phase 9 | AWS account with Bedrock AgentCore enabled (check regional availability: `us-east-1`) |
| Phase 9 | Docker available in CodeBuild for ARM64 Graviton image builds |
| Phase 10 | AWS Organizations access from management account; CUR consolidated billing enabled |
| Phase 11 | `ce:PurchaseSavingsPlans` and `ec2:PurchaseReservedInstancesOffering` IAM permissions |
| Phase 12 | GitHub Actions access to Optivue repo; `COST_GATE_API_KEY` secret in GitHub Secrets |
| Phase 13 | Amazon OpenSearch Serverless collection quota available in target region |
| Phase 14 | Azure Cost Management export configured; GCP Billing export to GCS bucket |

---

## Out of Scope (Unchanged from MVP)

- Autonomous production deletions — remains `policy_blocked` permanently
- Broad enterprise policy engine — Phase 12 RAG covers this sufficiently
- Statistical custom forecasting models — Cost Explorer Forecast API used throughout

---

## References

- [AWS Blog: Build a FinOps agent using Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/build-a-finops-agent-using-amazon-bedrock-agentcore/) — March 31, 2026
- [AWS Samples GitHub: sample-finops-agent-amazon-bedrock-agentcore](https://github.com/aws-samples/sample-finops-agent-amazon-bedrock-agentcore)
- [Amazon Bedrock AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Strands Agents SDK](https://strandsagents.com/)
- [AWS Labs Billing/Cost Management MCP Server](https://awslabs.github.io/mcp/servers/billing-cost-management-mcp-server/)
- [AWS Labs Pricing MCP Server](https://awslabs.github.io/mcp/servers/aws-pricing-mcp-server)
- [FOCUS Specification](https://focus.finops.org/)
- [Optivue Implementation Roadmap (MVP)](./01-implementation-roadmap-phases.md)
