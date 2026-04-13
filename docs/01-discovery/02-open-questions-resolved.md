# Open Questions — Resolved

Source: PRD Section 21 (5 open questions identified during product definition).
Status: All 5 resolved. Decisions recorded here as authoritative answers for implementation.

---

## Q1: Minimum confidence threshold for auto-routing recommendations

**Question:** What minimum confidence threshold is required before a recommendation can be auto-routed to an owner?

**Decision:** `0.70` (70%)

**Rationale:**
- Below 0.70, the risk of noisy or irrelevant recommendations causing alert fatigue is high.
- At 0.70+, Compute Optimizer and Trusted Advisor signal quality is typically sufficient for low-risk actions (rightsizing, idle detection).
- This threshold is configurable via a policy parameter stored in DynamoDB — it can be raised per environment (e.g., 0.85 for prod) without code changes.
- Recommendations below 0.70 are labeled `needs_review: true` and surfaced to the FinOps analyst queue for manual triage rather than auto-routed.

**Implementation note:** The threshold is read from a DynamoDB config item at runtime:
```
pk = CONFIG#recommendation_threshold
sk = GLOBAL
value = 0.70
```
Environment-specific overrides:
```
pk = CONFIG#recommendation_threshold
sk = ENV#prod
value = 0.85
```

---

## Q2: Which teams own final approval for production-impacting changes?

**Question:** Which teams own final approval for production-impacting changes?

**Decision:** Dual-approval required for all production mutations — Engineering Manager (resource owner) + FinOps Analyst (cost owner).

**Approval matrix by action type:**

| Action Type | Environment | Required Approvers | Mode |
|-------------|-------------|-------------------|------|
| Rightsizing | prod | Engineering Manager + FinOps Analyst | Dual |
| Idle shutdown | prod | Engineering Manager | Single |
| Commitment purchase (Savings Plans/RIs) | any | FinOps Analyst + Finance | Dual |
| Tag update | prod | FinOps Analyst | Single |
| Any action | staging | FinOps Analyst | Single |
| Low-risk action | dev | Auto-approved | None |
| High-risk action | dev | FinOps Analyst | Single |

**Escalation path:** If the designated approver does not respond within 24 hours, the approval request escalates to their manager. If no response within 48 hours, the request expires and must be re-submitted.

**Implementation note:** Approver roles are sourced from the Cognito user pool groups. The governance agent checks group membership via the JWT token before issuing an approval request.

---

## Q3: Mandatory unit economics metrics for executive reporting

**Question:** What unit economics metrics are mandatory for executive reporting?

**Decision:** Three mandatory unit economics metrics for the MVP executive dashboard:

| Metric | Definition | Reporting Cadence |
|--------|-----------|-------------------|
| Cost per active user (CPAU) | Total cloud cost / Monthly active users | Monthly |
| Cost per transaction (CPT) | Total cloud cost / Total transactions processed | Monthly |
| Cost per service (CPS) | Cloud cost allocated to each product/service by tag | Weekly |

**Additional metrics (Phase 2 / Post-MVP):**
- Cost per API call
- Unit cost trend (month-over-month change in CPAU and CPT)
- Cost efficiency score (actual unit cost vs. benchmark)

**Data requirements:**
- CPAU requires MAU metric fed from application analytics (e.g., CloudWatch custom metric or external analytics tool).
- CPT requires transaction count fed from application metrics.
- CPS is derived from existing CUR data using `product` tag.

**Implementation note:** For MVP, CPAU and CPT are optional if the application metrics data source is not yet integrated. CPS is mandatory and derivable from existing CUR tags.

---

## Q4: Internal deployment vs. customer-facing SaaS

**Question:** Is the first deployment internal-only or customer-facing SaaS?

**Decision:** Internal-first for MVP (single AWS account, single organization). SaaS architecture is deferred to Post-MVP Phase 7.

**MVP deployment model:**
- Single AWS account deployment.
- Cognito user pool scoped to internal users (corporate SSO via SAML federation if available).
- No multi-tenancy, no tenant isolation, no per-customer billing.
- Data is single-organization only.

**Implications for implementation:**
- No tenant ID needed in DynamoDB schema for MVP.
- No per-customer Bedrock agent isolation needed for MVP.
- No Stripe/billing integration needed for MVP.
- The SaaS pricing tiers in PRD Section 18 are deferred — do not implement in MVP.

**SaaS readiness notes (for Phase 7):**
- Add `tenant_id` to all DynamoDB partition keys when multi-tenancy is needed.
- Add Cognito user pool per tenant or use a shared pool with custom attributes.
- Add cost allocation tags for per-tenant cost tracking.

---

## Q5: Acceptable forecast error band by business unit

**Question:** What is the acceptable forecast error band by business unit?

**Decision:**

| Forecast Horizon | Acceptable Error Band | Rationale |
|-----------------|-----------------------|-----------|
| Monthly (current month) | ± 15% | Sufficient for budget tracking and variance alerting |
| Quarterly (next quarter) | ± 25% | Reflects inherent uncertainty in cloud usage 60-90 days out |
| Annual | ± 35% | Directional only — not used for budget commitments |

**Per-business-unit override:**
- Business units with highly stable, predictable workloads (e.g., batch processing) may tighten the band to ± 10% monthly.
- Business units with variable workloads (e.g., ML training, event-driven) should expect ± 20-25% monthly and this should be communicated to stakeholders.

**Forecast quality gate:**
- If the model's predicted error band exceeds the acceptable threshold, the forecast response includes a `forecast_reliability: low` flag.
- The agent must communicate this flag to the user and recommend reviewing the forecast manually before budget decisions are made.

**Implementation note:** AWS Cost Explorer's GetCostForecast API returns a prediction interval at 80% confidence. Use this as the primary error band source. Compare the returned `lower_bound` and `upper_bound` against the `mean_forecast` to compute the effective error band percentage.

---

## Decision Log

| Question | Decision Owner | Decision Date | Next Review |
|----------|---------------|---------------|-------------|
| Q1: Confidence threshold | FinOps Lead | 2026-04-13 | After pilot (Week 12) |
| Q2: Approval owners | Engineering Lead + FinOps Lead | 2026-04-13 | After Phase 4 |
| Q3: Unit economics metrics | CFO / Finance BP | 2026-04-13 | Monthly |
| Q4: Internal vs SaaS | Product Owner | 2026-04-13 | Post-MVP review |
| Q5: Forecast error band | Finance BP | 2026-04-13 | Quarterly |
