# Optivue — Code Reference

## Purpose
This document is the authoritative developer reference for the Optivue codebase.
It covers repo layout, stack versions, module responsibilities, code patterns, environment variables,
dependencies, and local development setup. Read this before writing any code.

---

## Table of Contents
1. [Repository Structure](#1-repository-structure)
2. [Tech Stack and Versions](#2-tech-stack-and-versions)
3. [Dependencies](#3-dependencies)
4. [Environment Variables](#4-environment-variables)
5. [CDK Infrastructure Stack](#5-cdk-infrastructure-stack)
6. [Backend — FastAPI on Lambda](#6-backend--fastapi-on-lambda)
7. [Bedrock Agent Integration](#7-bedrock-agent-integration)
8. [Lambda Action Group Adapters](#8-lambda-action-group-adapters)
9. [Step Functions Action Workflow](#9-step-functions-action-workflow)
10. [DynamoDB Access Layer](#10-dynamodb-access-layer)
11. [Frontend — Next.js App](#11-frontend--nextjs-app)
12. [Testing Patterns](#12-testing-patterns)
13. [CI/CD Pipeline](#13-cicd-pipeline)
14. [Local Development Setup](#14-local-development-setup)

---

## 1. Repository Structure

```
finops-agent/
├── infra/                          # AWS CDK infrastructure (TypeScript)
│   ├── bin/
│   │   └── app.ts                  # CDK app entry point
│   ├── lib/
│   │   ├── stacks/
│   │   │   ├── foundation-stack.ts # Cognito, IAM, Secrets Manager
│   │   │   ├── data-stack.ts       # S3, Glue, Athena
│   │   │   ├── agent-stack.ts      # Bedrock Agents + action groups
│   │   │   ├── api-stack.ts        # API Gateway + Lambda FastAPI
│   │   │   ├── workflow-stack.ts   # Step Functions + EventBridge
│   │   │   └── frontend-stack.ts   # Amplify Hosting
│   │   └── constructs/
│   │       ├── bedrock-agent.ts
│   │       ├── lambda-adapter.ts
│   │       └── dynamo-tables.ts
│   ├── package.json
│   └── cdk.json
│
├── backend/                        # Python FastAPI application
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry + Mangum handler
│   │   ├── routers/
│   │   │   ├── cost.py             # /cost/* endpoints
│   │   │   ├── anomalies.py        # /anomalies/* endpoints
│   │   │   ├── recommendations.py  # /recommendations/* endpoints
│   │   │   ├── actions.py          # /actions/* endpoints
│   │   │   └── kpi.py              # /kpi/* endpoints
│   │   ├── services/
│   │   │   ├── bedrock_service.py  # Bedrock agent invoke
│   │   │   ├── dynamo_service.py   # DynamoDB read/write
│   │   │   └── auth_service.py     # Cognito JWT validation
│   │   ├── models/
│   │   │   ├── cost.py             # Pydantic models for cost records
│   │   │   ├── anomaly.py          # Pydantic models for anomalies
│   │   │   ├── recommendation.py   # Pydantic models for recommendations
│   │   │   └── action.py           # Pydantic models for actions/approvals
│   │   └── config.py               # Settings from env vars
│   ├── adapters/                   # Lambda action group handlers
│   │   ├── cost_query.py           # get_cost_by_period
│   │   ├── anomaly_explain.py      # get_anomaly_explanation
│   │   ├── budget_variance.py      # get_budget_variance
│   │   ├── forecast.py             # get_forecast
│   │   ├── recommendations.py      # get_recommendations
│   │   ├── commitments.py          # get_commitment_opportunities
│   │   ├── create_ticket.py        # create_ticket (Jira)
│   │   ├── notify_owner.py         # notify_owner (Slack/Teams)
│   │   ├── risk_eval.py            # evaluate_action_risk
│   │   └── approval.py             # request_approval
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/                       # Next.js 15 application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Role-aware home redirect
│   │   ├── (analyst)/
│   │   │   ├── dashboard/page.tsx  # FinOps analyst queue
│   │   │   ├── anomalies/page.tsx
│   │   │   └── recommendations/page.tsx
│   │   ├── (engineering)/
│   │   │   └── inbox/page.tsx      # Engineering action inbox
│   │   ├── (leadership)/
│   │   │   └── snapshot/page.tsx   # Leadership KPI snapshot
│   │   └── chat/page.tsx           # Natural language query interface
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx
│   │   │   └── MessageBubble.tsx
│   │   ├── recommendations/
│   │   │   ├── RecommendationCard.tsx
│   │   │   └── ApprovalModal.tsx
│   │   ├── anomalies/
│   │   │   └── AnomalyCard.tsx
│   │   └── kpi/
│   │       └── KPIDashboard.tsx
│   ├── lib/
│   │   ├── api.ts                  # API client (typed fetch wrappers)
│   │   ├── auth.ts                 # Cognito Amplify auth helpers
│   │   └── types.ts                # Shared TypeScript types
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── fixtures/                       # Sample data for demo fallback
│   ├── sample-cost-data.json
│   ├── sample-anomaly.json
│   └── sample-recommendations.json
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # PR checks: lint, test, type-check
│       └── deploy.yml              # Deploy to AWS on merge to main
│
└── docs/                           # Project documentation (this repo)
```

---

## 2. Tech Stack and Versions

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend framework | Next.js | 15.x |
| Frontend language | TypeScript | 5.x |
| Frontend styling | Tailwind CSS | 3.x |
| Frontend auth | AWS Amplify JS | 6.x |
| Frontend hosting | AWS Amplify Hosting | — |
| Backend language | Python | 3.12 |
| Backend framework | FastAPI | 0.115.x |
| Lambda adapter | Mangum | 0.19.x |
| Agent orchestration | Amazon Bedrock Agents Runtime | boto3 1.34.x |
| Data query | Amazon Athena | boto3 1.34.x |
| Workflow | AWS Step Functions | boto3 1.34.x |
| State store | Amazon DynamoDB | boto3 1.34.x |
| Auth | Amazon Cognito | boto3 1.34.x |
| IaC | AWS CDK | 2.x (TypeScript) |
| CI/CD | GitHub Actions | — |
| Node.js (CDK + frontend) | Node.js | 20.x LTS |
| Package manager (frontend) | npm | 10.x |
| Package manager (Python) | pip + venv | — |

---

## 3. Dependencies

### backend/requirements.txt
```
fastapi==0.115.0
mangum==0.19.0
boto3==1.34.0
pydantic==2.7.0
pydantic-settings==2.3.0
python-jose[cryptography]==3.3.0
httpx==0.27.0
```

### backend/requirements-dev.txt
```
pytest==8.2.0
pytest-asyncio==0.23.0
moto[all]==5.0.0
httpx==0.27.0
ruff==0.4.0
mypy==1.10.0
```

### frontend/package.json (key dependencies)
```json
{
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "aws-amplify": "6.3.0",
    "@aws-amplify/ui-react": "6.2.0",
    "recharts": "2.12.0",
    "lucide-react": "0.395.0",
    "clsx": "2.1.1",
    "tailwind-merge": "2.3.0"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "tailwindcss": "3.4.4",
    "@types/react": "19.0.0",
    "eslint": "9.4.0",
    "vitest": "1.6.0"
  }
}
```

### infra/package.json (key dependencies)
```json
{
  "dependencies": {
    "aws-cdk-lib": "2.145.0",
    "constructs": "10.3.0"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "aws-cdk": "2.145.0",
    "@types/node": "20.14.0"
  }
}
```

---

## 4. Environment Variables

### Backend Lambda (set via CDK → Secrets Manager or SSM)

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | Deployment region | `us-east-1` |
| `BEDROCK_AGENT_ID` | Bedrock supervisor agent ID | `ABCD1234EF` |
| `BEDROCK_AGENT_ALIAS_ID` | Bedrock agent alias | `TSTALIASID` |
| `ATHENA_DATABASE` | Glue/Athena database name | `finops_cost_db` |
| `ATHENA_WORKGROUP` | Athena workgroup | `primary` |
| `COST_EXPORT_S3_BUCKET` | S3 bucket for CUR/Data Exports | `my-cost-exports-bucket` |
| `ATHENA_RESULTS_S3_BUCKET` | S3 bucket for Athena query results | `my-athena-results-bucket` |
| `DYNAMODB_RECOMMENDATIONS_TABLE` | DynamoDB table name | `finops-recommendations` |
| `DYNAMODB_APPROVALS_TABLE` | DynamoDB table name | `finops-approvals` |
| `DYNAMODB_ACTION_HISTORY_TABLE` | DynamoDB table name | `finops-action-history` |
| `DYNAMODB_KPI_TABLE` | DynamoDB table name | `finops-kpi-metrics` |
| `COGNITO_USER_POOL_ID` | Cognito user pool ID | `us-east-1_XXXXXXXXX` |
| `COGNITO_CLIENT_ID` | Cognito app client ID | `xxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `JIRA_BASE_URL` | Jira instance URL | `https://your-org.atlassian.net` |
| `JIRA_SECRET_NAME` | Secrets Manager key for Jira token | `finops/jira-api-token` |
| `JIRA_PROJECT_KEY` | Jira project key | `FINOPS` |
| `SLACK_SECRET_NAME` | Secrets Manager key for Slack webhook | `finops/slack-webhook-url` |
| `RECOMMENDATION_CONFIDENCE_THRESHOLD` | Min confidence for auto-routing | `0.70` |
| `DEMO_MODE` | Use fixture data instead of live APIs | `false` |

### Frontend (.env.local)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL |
| `NEXT_PUBLIC_COGNITO_REGION` | AWS region for Cognito |
| `NEXT_PUBLIC_COGNITO_USER_POOL_ID` | Cognito user pool ID |
| `NEXT_PUBLIC_COGNITO_CLIENT_ID` | Cognito app client ID |

---

## 5. CDK Infrastructure Stack

### Stack Order and Dependencies
```
foundation-stack  (no deps)
    └── data-stack         (depends on foundation-stack)
    └── agent-stack        (depends on data-stack)
    └── api-stack          (depends on agent-stack)
    └── workflow-stack     (depends on api-stack)
    └── frontend-stack     (depends on api-stack)
```

### infra/bin/app.ts
```typescript
import * as cdk from 'aws-cdk-lib';
import { FoundationStack } from '../lib/stacks/foundation-stack';
import { DataStack } from '../lib/stacks/data-stack';
import { AgentStack } from '../lib/stacks/agent-stack';
import { ApiStack } from '../lib/stacks/api-stack';
import { WorkflowStack } from '../lib/stacks/workflow-stack';
import { FrontendStack } from '../lib/stacks/frontend-stack';

const app = new cdk.App();
const env = { account: process.env.CDK_ACCOUNT, region: process.env.CDK_REGION ?? 'us-east-1' };

const foundation = new FoundationStack(app, 'FinOpsFoundation', { env });
const data = new DataStack(app, 'FinOpsData', { env, foundation });
const agent = new AgentStack(app, 'FinOpsAgent', { env, data });
const api = new ApiStack(app, 'FinOpsApi', { env, foundation, agent });
const workflow = new WorkflowStack(app, 'FinOpsWorkflow', { env, api });
new FrontendStack(app, 'FinOpsFrontend', { env, api });
```

### infra/lib/constructs/dynamo-tables.ts (pattern)
```typescript
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class FinOpsTables extends Construct {
  public readonly recommendations: dynamodb.Table;
  public readonly approvals: dynamodb.Table;
  public readonly actionHistory: dynamodb.Table;
  public readonly kpiMetrics: dynamodb.Table;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.recommendations = new dynamodb.Table(this, 'Recommendations', {
      tableName: 'finops-recommendations',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl',
    });

    this.recommendations.addGlobalSecondaryIndex({
      indexName: 'by-owner-status-index',
      partitionKey: { name: 'owner', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    this.recommendations.addGlobalSecondaryIndex({
      indexName: 'by-priority-created-index',
      partitionKey: { name: 'priority_tier', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    this.approvals = new dynamodb.Table(this, 'Approvals', {
      tableName: 'finops-approvals',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      timeToLiveAttribute: 'ttl',
    });

    this.actionHistory = new dynamodb.Table(this, 'ActionHistory', {
      tableName: 'finops-action-history',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      // No TTL — immutable audit log
    });

    this.kpiMetrics = new dynamodb.Table(this, 'KpiMetrics', {
      tableName: 'finops-kpi-metrics',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
    });
  }
}
```

---

## 6. Backend — FastAPI on Lambda

### backend/app/main.py
```python
from fastapi import FastAPI
from mangum import Mangum
from app.routers import cost, anomalies, recommendations, actions, kpi
from app.config import settings

app = FastAPI(title="Optivue API", version="0.1.0")

app.include_router(cost.router, prefix="/cost", tags=["cost"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["anomalies"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(actions.router, prefix="/actions", tags=["actions"])
app.include_router(kpi.router, prefix="/kpi", tags=["kpi"])

@app.get("/health")
def health():
    return {"status": "ok"}

# Lambda handler
handler = Mangum(app, lifespan="off")
```

### backend/app/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    bedrock_agent_id: str
    bedrock_agent_alias_id: str
    athena_database: str
    athena_workgroup: str = "primary"
    cost_export_s3_bucket: str
    athena_results_s3_bucket: str
    dynamodb_recommendations_table: str = "finops-recommendations"
    dynamodb_approvals_table: str = "finops-approvals"
    dynamodb_action_history_table: str = "finops-action-history"
    dynamodb_kpi_table: str = "finops-kpi-metrics"
    cognito_user_pool_id: str
    cognito_client_id: str
    jira_base_url: str
    jira_secret_name: str
    jira_project_key: str = "FINOPS"
    slack_secret_name: str
    recommendation_confidence_threshold: float = 0.70
    demo_mode: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### backend/app/routers/recommendations.py (pattern)
```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.recommendation import RecommendationResponse, RecommendationListResponse
from app.services.bedrock_service import invoke_agent
from app.services.dynamo_service import get_recommendations_for_owner
from app.services.auth_service import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=RecommendationListResponse)
async def list_recommendations(
    top_n: int = 5,
    priority_tier: str | None = None,
    current_user=Depends(get_current_user),
):
    """Return ranked recommendations. Engineering managers see only their team's recs."""
    if current_user.role == "engineering-manager":
        items = await get_recommendations_for_owner(current_user.team)
    else:
        items = await get_recommendations_for_owner(owner=None, top_n=top_n, priority_tier=priority_tier)
    return RecommendationListResponse(recommendations=items)

@router.post("/{recommendation_id}/approve")
async def approve_recommendation(
    recommendation_id: str,
    current_user=Depends(require_role(["finops-analyst", "engineering-manager"])),
):
    """Initiate approval workflow for a recommendation."""
    # Calls governance agent to evaluate risk, then stores approval request
    response = await invoke_agent(
        session_id=current_user.session_id,
        prompt=f"Evaluate and initiate approval for recommendation {recommendation_id}",
        context={"recommendation_id": recommendation_id, "approver": current_user.username, "role": current_user.role},
    )
    return response
```

### backend/app/models/recommendation.py
```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class Recommendation(BaseModel):
    recommendation_id: str
    type: Literal["rightsizing", "idle", "commitment", "tagging"]
    estimated_monthly_savings: float
    confidence_score: float = Field(ge=0.0, le=1.0)
    effort_level: Literal["low", "medium", "high"]
    risk_level: Literal["low", "medium", "high"]
    priority_score: float = Field(ge=0.0, le=1.0)
    priority_tier: Literal["P1", "P2", "P3"]
    suggested_owner: str
    recommended_due_date: date
    needs_review: bool
    rationale: str
    evidence_refs: list[str]
    status: str = "open"

class RecommendationListResponse(BaseModel):
    recommendations: list[Recommendation]
    total_estimated_monthly_savings: float = 0.0
```

---

## 7. Bedrock Agent Integration

### backend/app/services/bedrock_service.py
```python
import boto3
import json
from app.config import settings

client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)

async def invoke_agent(session_id: str, prompt: str, context: dict | None = None) -> dict:
    """Invoke the Bedrock supervisor agent and stream the response."""
    input_text = prompt
    if context:
        input_text = f"{prompt}\n\nContext: {json.dumps(context)}"

    response = client.invoke_agent(
        agentId=settings.bedrock_agent_id,
        agentAliasId=settings.bedrock_agent_alias_id,
        sessionId=session_id,
        inputText=input_text,
        enableTrace=True,
    )

    completion = ""
    traces = []

    for event in response.get("completion", []):
        if "chunk" in event:
            completion += event["chunk"]["bytes"].decode("utf-8")
        if "trace" in event:
            traces.append(event["trace"])

    return {
        "response": completion,
        "session_id": session_id,
        "traces": traces,
    }
```

### Demo mode fallback pattern
```python
# backend/app/services/bedrock_service.py (demo mode)
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "fixtures"

async def invoke_agent(session_id: str, prompt: str, context: dict | None = None) -> dict:
    if settings.demo_mode:
        return _load_fixture_response(prompt)
    # ... real implementation above

def _load_fixture_response(prompt: str) -> dict:
    prompt_lower = prompt.lower()
    if "anomaly" in prompt_lower:
        data = json.loads((FIXTURES_DIR / "sample-anomaly.json").read_text())
        return {"response": f"Anomaly detected: {data['root_cause_summary']}", "session_id": "demo"}
    if "recommendation" in prompt_lower:
        data = json.loads((FIXTURES_DIR / "sample-recommendations.json").read_text())
        return {"response": json.dumps(data["recommendations"][:5]), "session_id": "demo"}
    data = json.loads((FIXTURES_DIR / "sample-cost-data.json").read_text())
    return {"response": f"Total cost: ${data['result']['total_cost']:,.2f}", "session_id": "demo"}
```

---

## 8. Lambda Action Group Adapters

All adapters follow the same Bedrock action group event contract:

### Adapter pattern (backend/adapters/cost_query.py)
```python
import boto3
import json
from datetime import datetime

athena = boto3.client("athena")

def handler(event: dict, context) -> dict:
    """Bedrock action group handler for get_cost_by_period."""
    # Parse parameters from Bedrock action group event
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}

    start_date = params.get("start_date")
    end_date = params.get("end_date")
    granularity = params.get("granularity", "MONTHLY")
    service = params.get("service")
    environment = params.get("environment", "all")

    query = _build_athena_query(start_date, end_date, granularity, service, environment)
    result = _run_athena_query(query)

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "function": event["function"],
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": json.dumps(result)
                    }
                }
            }
        }
    }

def _build_athena_query(start_date, end_date, granularity, service, environment) -> str:
    filters = f"usage_start_time >= DATE '{start_date}' AND usage_end_time <= DATE '{end_date}'"
    if service:
        filters += f" AND service = '{service}'"
    if environment != "all":
        filters += f" AND tags['environment'] = '{environment}'"

    return f"""
        SELECT
            service,
            SUM(blended_cost) AS total_cost,
            SUM(blended_cost) * 100.0 / SUM(SUM(blended_cost)) OVER () AS percentage
        FROM cost_usage
        WHERE {filters}
        GROUP BY service
        ORDER BY total_cost DESC
        LIMIT 10
    """

def _run_athena_query(query: str) -> dict:
    import os
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": os.environ["ATHENA_DATABASE"]},
        WorkGroup=os.environ.get("ATHENA_WORKGROUP", "primary"),
        ResultConfiguration={
            "OutputLocation": f"s3://{os.environ['ATHENA_RESULTS_S3_BUCKET']}/query-results/"
        },
    )
    # Poll for completion (with timeout) then fetch results
    execution_id = response["QueryExecutionId"]
    return _poll_and_fetch(execution_id)
```

### Approval adapter pattern (backend/adapters/approval.py)
```python
import boto3, json, os, uuid
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")

def handler(event: dict, context) -> dict:
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}

    action_type = params["action_type"]
    action_payload = json.loads(params["action_payload"])
    approver_role = params["approver_role"]
    risk_level = params["risk_level"]
    dual_approval = params.get("dual_approval_required", "false").lower() == "true"
    expiry_hours = int(params.get("expiry_hours", 4))

    # Block production deletion in MVP
    if action_type == "deletion" and action_payload.get("environment") == "prod":
        return _build_response(event, {
            "status": "blocked",
            "block_reason": "Production resource deletion is blocked in MVP phase.",
            "approval_token": None,
        })

    approval_id = f"apr-{uuid.uuid4().hex[:8]}"
    expires_at = (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat() + "Z"

    table = dynamodb.Table(os.environ["DYNAMODB_APPROVALS_TABLE"])
    table.put_item(Item={
        "pk": f"APPROVAL#{approval_id}",
        "sk": "METADATA",
        "approval_request_id": approval_id,
        "action_type": action_type,
        "action_payload": action_payload,
        "approver_role": approver_role,
        "risk_level": risk_level,
        "dual_approval_required": dual_approval,
        "status": "pending",
        "approval_token": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": expires_at,
    })

    return _build_response(event, {
        "approval_request_id": approval_id,
        "status": "pending",
        "approval_token": None,
        "expires_at": expires_at,
    })
```

---

## 9. Step Functions Action Workflow

### State Machine Definition (infra/lib/stacks/workflow-stack.ts)
```typescript
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';

const validateApproval = new tasks.LambdaInvoke(this, 'ValidateApproval', {
  lambdaFunction: approvalValidatorFn,
  outputPath: '$.Payload',
});

const createTicket = new tasks.LambdaInvoke(this, 'CreateTicket', {
  lambdaFunction: jiraAdapterFn,
  outputPath: '$.Payload',
});

const notifyOwner = new tasks.LambdaInvoke(this, 'NotifyOwner', {
  lambdaFunction: notifyAdapterFn,
  outputPath: '$.Payload',
});

const updateState = new tasks.DynamoPutItem(this, 'UpdateActionState', {
  table: actionHistoryTable,
  item: {
    pk: tasks.DynamoAttributeValue.fromString(sfn.JsonPath.stringAt('$.action_id')),
    sk: tasks.DynamoAttributeValue.fromString('METADATA'),
    status: tasks.DynamoAttributeValue.fromString('completed'),
    executed_at: tasks.DynamoAttributeValue.fromString(sfn.JsonPath.stringAt('$$.Execution.StartTime')),
  },
});

const approvalBlocked = new sfn.Fail(this, 'ApprovalBlocked', {
  error: 'ApprovalRequired',
  cause: 'Action blocked — valid approval token not present.',
});

const definition = validateApproval
  .next(new sfn.Choice(this, 'ApprovalValid?')
    .when(sfn.Condition.booleanEquals('$.approved', true),
      createTicket.next(notifyOwner).next(updateState))
    .otherwise(approvalBlocked));

this.stateMachine = new sfn.StateMachine(this, 'ActionWorkflow', {
  definition,
  stateMachineName: 'finops-action-workflow',
  tracingEnabled: true,
  logs: {
    destination: logGroup,
    level: sfn.LogLevel.ALL,
  },
});
```

---

## 10. DynamoDB Access Layer

### backend/app/services/dynamo_service.py
```python
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from app.models.recommendation import Recommendation

dynamodb = boto3.resource("dynamodb")

def get_recommendations_table():
    return dynamodb.Table(os.environ["DYNAMODB_RECOMMENDATIONS_TABLE"])

async def get_recommendations_for_owner(
    owner: str | None = None,
    top_n: int = 5,
    priority_tier: str | None = None,
) -> list[Recommendation]:
    table = get_recommendations_table()

    if owner:
        # GSI1: by-owner-status-index
        response = table.query(
            IndexName="by-owner-status-index",
            KeyConditionExpression=Key("owner").eq(owner) & Key("status").eq("open"),
            Limit=top_n,
        )
    elif priority_tier:
        # GSI2: by-priority-created-index
        response = table.query(
            IndexName="by-priority-created-index",
            KeyConditionExpression=Key("priority_tier").eq(priority_tier),
            ScanIndexForward=False,
            Limit=top_n,
        )
    else:
        # Default: top P1 recommendations
        response = table.query(
            IndexName="by-priority-created-index",
            KeyConditionExpression=Key("priority_tier").eq("P1"),
            ScanIndexForward=False,
            Limit=top_n,
        )

    return [Recommendation(**{k: v for k, v in item.items() if k not in ("pk", "sk")})
            for item in response.get("Items", [])]

async def update_recommendation_status(
    recommendation_id: str,
    new_status: str,
    actor: str,
    actor_role: str,
    comment: str = "",
) -> None:
    table = get_recommendations_table()
    from datetime import datetime
    now = datetime.utcnow().isoformat() + "Z"

    # Update current status
    table.update_item(
        Key={"pk": f"REC#{recommendation_id}", "sk": "METADATA"},
        UpdateExpression="SET #s = :s, updated_at = :t",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": new_status, ":t": now},
    )

    # Append history record
    table.put_item(Item={
        "pk": f"REC#{recommendation_id}",
        "sk": f"HISTORY#{now}",
        "new_status": new_status,
        "actor": actor,
        "actor_role": actor_role,
        "comment": comment,
        "timestamp": now,
    })
```

---

## 11. Frontend — Next.js App

### Cognito Auth setup (frontend/lib/auth.ts)
```typescript
import { Amplify } from 'aws-amplify';
import { fetchAuthSession, getCurrentUser, signIn, signOut } from 'aws-amplify/auth';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
      userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
      loginWith: { username: true, email: true },
    },
  },
});

export async function getAuthToken(): Promise<string> {
  const session = await fetchAuthSession();
  return session.tokens?.idToken?.toString() ?? '';
}

export async function getUserRole(): Promise<string> {
  const session = await fetchAuthSession();
  const groups = (session.tokens?.idToken?.payload['cognito:groups'] as string[]) ?? [];
  // Role priority: finops-analyst > engineering-manager > finance > leadership
  for (const role of ['finops-analyst', 'engineering-manager', 'finance', 'leadership']) {
    if (groups.includes(role)) return role;
  }
  return 'readonly';
}

export { getCurrentUser, signIn, signOut };
```

### API client (frontend/lib/api.ts)
```typescript
import { getAuthToken } from './auth';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  cost: {
    query: (prompt: string) =>
      request('/cost/query', { method: 'POST', body: JSON.stringify({ prompt }) }),
  },
  anomalies: {
    explain: (anomalyId?: string) =>
      request('/anomalies/explain', { method: 'POST', body: JSON.stringify({ anomaly_id: anomalyId }) }),
  },
  recommendations: {
    list: (topN = 5, priorityTier?: string) =>
      request(`/recommendations/?top_n=${topN}${priorityTier ? `&priority_tier=${priorityTier}` : ''}`),
    approve: (id: string) =>
      request(`/recommendations/${id}/approve`, { method: 'POST' }),
  },
  actions: {
    createTicket: (recommendationId: string) =>
      request('/actions/ticket', { method: 'POST', body: JSON.stringify({ recommendation_id: recommendationId }) }),
    notify: (recommendationId: string) =>
      request('/actions/notify', { method: 'POST', body: JSON.stringify({ recommendation_id: recommendationId }) }),
  },
  kpi: {
    snapshot: () => request('/kpi/snapshot'),
  },
};
```

### Role-aware home redirect (frontend/app/page.tsx)
```typescript
import { redirect } from 'next/navigation';
import { getUserRole } from '@/lib/auth';

export default async function Home() {
  const role = await getUserRole();
  const roleRoutes: Record<string, string> = {
    'finops-analyst': '/analyst/dashboard',
    'engineering-manager': '/engineering/inbox',
    'finance': '/analyst/dashboard',
    'leadership': '/leadership/snapshot',
  };
  redirect(roleRoutes[role] ?? '/chat');
}
```

### ApprovalModal component (frontend/components/recommendations/ApprovalModal.tsx)
```typescript
'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import type { Recommendation } from '@/lib/types';

interface Props {
  recommendation: Recommendation;
  onClose: () => void;
  onApproved: () => void;
}

export function ApprovalModal({ recommendation, onClose, onApproved }: Props) {
  const [loading, setLoading] = useState(false);

  const handleApprove = async () => {
    setLoading(true);
    try {
      await api.recommendations.approve(recommendation.recommendation_id);
      await api.actions.createTicket(recommendation.recommendation_id);
      await api.actions.notify(recommendation.recommendation_id);
      onApproved();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full shadow-xl">
        <h2 className="text-lg font-semibold mb-2">Confirm Action</h2>
        <p className="text-sm text-gray-600 mb-4">{recommendation.rationale}</p>
        <div className="flex gap-2 justify-between text-sm mb-6">
          <span>Savings: <strong>${recommendation.estimated_monthly_savings.toLocaleString()}/mo</strong></span>
          <span>Risk: <strong className="capitalize">{recommendation.risk_level}</strong></span>
          <span>Owner: <strong>{recommendation.suggested_owner}</strong></span>
        </div>
        <p className="text-xs text-amber-600 mb-4">
          This will create a Jira ticket and notify the owner. This action is logged.
        </p>
        <div className="flex gap-3 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm border rounded-lg">Cancel</button>
          <button
            onClick={handleApprove}
            disabled={loading}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg disabled:opacity-50"
          >
            {loading ? 'Processing…' : 'Approve & Create Ticket'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 12. Testing Patterns

### Backend unit test (backend/tests/test_recommendations.py)
```python
import pytest
from moto import mock_aws
import boto3, os, json
from app.services.dynamo_service import get_recommendations_for_owner, update_recommendation_status

@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_RECOMMENDATIONS_TABLE", "finops-recommendations")

@mock_aws
def test_get_recommendations_for_owner():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName="finops-recommendations",
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "owner", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[{
            "IndexName": "by-owner-status-index",
            "KeySchema": [
                {"AttributeName": "owner", "KeyType": "HASH"},
                {"AttributeName": "status", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(Item={
        "pk": "REC#rec-001", "sk": "METADATA",
        "recommendation_id": "rec-001",
        "type": "rightsizing",
        "owner": "team-payments",
        "status": "open",
        "priority_tier": "P1",
        "priority_score": 0.74,
        "estimated_monthly_savings": 842.15,
        "confidence_score": 0.83,
        "effort_level": "medium",
        "risk_level": "low",
        "rationale": "CPU low",
        "evidence_refs": [],
        "suggested_owner": "team-payments",
        "recommended_due_date": "2026-05-01",
        "needs_review": False,
    })

    import asyncio
    results = asyncio.run(get_recommendations_for_owner(owner="team-payments"))
    assert len(results) == 1
    assert results[0].recommendation_id == "rec-001"
```

### Safety test — approval gate
```python
@mock_aws
def test_action_blocked_without_approval_token(client):
    """No action executes without a valid approval token."""
    response = client.post("/actions/ticket", json={"recommendation_id": "rec-001"})
    # Must return 403 if no approval token in session
    assert response.status_code == 403
    assert "approval" in response.json()["detail"].lower()
```

### Frontend component test (frontend/components/recommendations/ApprovalModal.test.tsx)
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ApprovalModal } from './ApprovalModal';
import { api } from '@/lib/api';
import { vi } from 'vitest';

vi.mock('@/lib/api');

const mockRec = {
  recommendation_id: 'rec-001',
  rationale: 'CPU below 18% for 14 days',
  estimated_monthly_savings: 842.15,
  risk_level: 'low',
  suggested_owner: 'team-payments',
};

test('shows confirmation details before approving', () => {
  render(<ApprovalModal recommendation={mockRec as any} onClose={vi.fn()} onApproved={vi.fn()} />);
  expect(screen.getByText(/CPU below 18%/)).toBeInTheDocument();
  expect(screen.getByText(/\$842/)).toBeInTheDocument();
});

test('calls approve, createTicket, and notify on confirm', async () => {
  vi.mocked(api.recommendations.approve).mockResolvedValue({});
  vi.mocked(api.actions.createTicket).mockResolvedValue({});
  vi.mocked(api.actions.notify).mockResolvedValue({});

  const onApproved = vi.fn();
  render(<ApprovalModal recommendation={mockRec as any} onClose={vi.fn()} onApproved={onApproved} />);
  fireEvent.click(screen.getByText('Approve & Create Ticket'));

  await waitFor(() => expect(onApproved).toHaveBeenCalled());
  expect(api.actions.createTicket).toHaveBeenCalledWith('rec-001');
});
```

---

## 13. CI/CD Pipeline

### .github/workflows/ci.yml
```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r backend/requirements.txt -r backend/requirements-dev.txt
      - run: ruff check backend/
      - run: mypy backend/app
      - run: pytest backend/tests/ --tb=short

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci --prefix frontend
      - run: npm run type-check --prefix frontend
      - run: npm run lint --prefix frontend
      - run: npm run test --prefix frontend

  infra:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci --prefix infra
      - run: npm run build --prefix infra
      - run: npx cdk synth --app "npx ts-node infra/bin/app.ts"
        env:
          CDK_ACCOUNT: ${{ secrets.AWS_ACCOUNT_ID }}
          CDK_REGION: us-east-1
```

### .github/workflows/deploy.yml
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: npm ci --prefix infra
      - run: npx cdk deploy --all --require-approval never --app "npx ts-node infra/bin/app.ts"
        working-directory: infra
```

---

## 14. Local Development Setup

```bash
# 1. Clone and navigate
git clone https://github.com/your-org/finops-agent.git
cd finops-agent

# 2. Bootstrap AWS environment (one-time)
aws configure                          # or use SSO
aws sts get-caller-identity            # verify credentials
npm install -g aws-cdk
npm ci --prefix infra
cdk bootstrap --app "npx ts-node infra/bin/app.ts"

# 3. Backend local dev
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                   # fill in values
uvicorn app.main:app --reload --port 8000

# 4. Frontend local dev
cd ../frontend
npm ci
cp .env.local.example .env.local       # fill in values
npm run dev                            # starts on http://localhost:3000

# 5. Run all tests
cd ../backend && pytest tests/ -v
cd ../frontend && npm run test

# 6. Enable demo mode (no AWS APIs needed)
# In backend/.env set: DEMO_MODE=true
# Fixtures in fixtures/ will be used as response data
```

---

## References
- AWS CDK v2: https://docs.aws.amazon.com/cdk/v2/guide/home.html
- Amazon Bedrock Agents: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- FastAPI: https://fastapi.tiangolo.com
- Mangum: https://mangum.faas.lol
- Next.js 15: https://nextjs.org/docs
- AWS Amplify JS v6: https://docs.amplify.aws/javascript/
- Bedrock samples: https://github.com/aws-samples/amazon-bedrock-samples
- AgentCore samples: https://github.com/awslabs/agentcore-samples
- Agent Evaluation: https://github.com/awslabs/agent-evaluation

