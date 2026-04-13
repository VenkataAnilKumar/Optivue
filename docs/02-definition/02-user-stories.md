# User Stories and Acceptance Criteria

## Story 1: Query spend by period
As a FinOps analyst, I want to ask for monthly spend so I can identify cost trends.

Acceptance criteria:
- Given a valid query, when user asks monthly spend, then response includes total spend and top 3 cost drivers.

## Story 2: Explain anomaly
As a FinOps analyst, I want anomaly explanation so I can investigate quickly.

Acceptance criteria:
- Given anomaly input, when user asks for explanation, then system returns impact amount, likely drivers, and owner candidate.

## Story 3: Show top recommendations
As an engineering manager, I want ranked savings recommendations so I can prioritize actions.

Acceptance criteria:
- Given usage/cost data, when recommendations are generated, then top 5 includes estimated savings and confidence.

## Story 4: Create Jira ticket
As an engineering manager, I want to create a ticket from recommendation so work is tracked.

Acceptance criteria:
- Given approved recommendation, when user confirms action, then Jira ticket is created and link is returned.

## Story 5: Send owner notification
As a FinOps analyst, I want owner notification in Slack/Teams so action is visible immediately.

Acceptance criteria:
- Given ticket created, when notify action is triggered, then message is sent with recommendation and ticket link.

## Story 6: Require approval gate
As a governance owner, I want mandatory approval before actions so risky changes are controlled.

Acceptance criteria:
- Given an action request, when approval is not provided, then action is blocked.

## Story 7: Track lifecycle status
As a FinOps analyst, I want to track recommendation status so I can measure follow-through.

Acceptance criteria:
- Given recommendation exists, when status changes, then history captures timestamp and actor.

## Story 8: Show realized savings
As leadership, I want identified vs realized savings so I can assess business impact.

Acceptance criteria:
- Given completed recommendation, when savings report runs, then realized values are visible by team and month.

## Priority Tags
- P1: Stories 1-6
- P2: Stories 7-8
