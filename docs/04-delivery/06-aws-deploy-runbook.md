# AWS Deployment Runbook

## Purpose
This runbook describes the current AWS deployment flow for Optivue using the checked-in Phase 8 automation scripts and CDK stacks. It is aligned to the live repository state as of 2026-04-13.

Use this document when you need to:
- prepare an AWS account and region for the first deployment
- populate `.env.deploy` from CDK outputs
- deploy stacks in the correct dependency order
- run post-deploy smoke checks
- create Cognito test users for each role
- troubleshoot common deployment failures in the current Windows-based workflow

## Scope
This runbook covers:
- local prerequisite validation
- CDK bootstrap
- stack deployment
- post-deploy configuration
- smoke testing
- role test-user setup

This runbook does not cover:
- production data ingestion wiring beyond the stack outputs and env values
- live AWS cost export onboarding outside the current CDK/data stack assumptions
- CI/CD automation beyond the local PowerShell entrypoint

## Source of Truth
Deployment automation and environment mapping are defined in:
- `scripts/deploy/phase8-go-live.ps1`
- `scripts/deploy/phase8-go-live.cmd`
- `.env.deploy.example`
- `src/infra/lib/stacks/*.ts`
- `src/infra/lib/constructs/cognito-pool.ts`

## Architecture Targets
The deployment provisions these CDK stacks in order:
1. `FinOpsFoundation`
2. `FinOpsData`
3. `FinOpsAgent`
4. `FinOpsApi`
5. `FinOpsWorkflow`
6. `FinOpsFrontend`

## Local Prerequisites
Required tools:
- `node`
- `npm`
- `python`
- PowerShell 7 (`pwsh`) for the main runbook entrypoint

Required local files:
- `.env.deploy`
- backend `requirements.txt` and `requirements-dev.txt`
- `src/infra/node_modules` installed via `npm ci`
- `src/frontend/node_modules` installed via `npm ci`

Required AWS credentials:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

Optional but recommended:
- `CDK_DEFAULT_ACCOUNT`
- `CDK_DEFAULT_REGION`

Notes:
- The current PowerShell runbook does not require the AWS CLI binary to be installed.
- CDK still needs valid AWS SDK credentials in the shell environment.
- The local Lambda bundling path for `FinOpsApi` now works on Windows without Docker by copying backend sources with Node file-copy logic.

## Region Guidance
Default region in the current runbook is `us-east-1`.

If you deploy to a different region, keep these aligned:
- PowerShell `-Region` parameter
- `AWS_DEFAULT_REGION`
- `.env.deploy` value for `AWS_REGION`

## Files You Must Prepare
### 1. AWS credential environment variables
In PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "<secret>"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:CDK_DEFAULT_REGION = "us-east-1"
```

If `CDK_DEFAULT_ACCOUNT` is not already set in your environment, prefer setting it before bootstrap:

```powershell
$env:CDK_DEFAULT_ACCOUNT = "123456789012"
```

Without `CDK_DEFAULT_ACCOUNT`, the script currently falls back to `unknown` in the bootstrap command string, which is not suitable for a real deployment.

### 2. Deployment environment file
Create `.env.deploy` from `.env.deploy.example`.

```powershell
Copy-Item .env.deploy.example .env.deploy
```

Populate it after deployment outputs are available.

## `.env.deploy` Mapping
Use the stack output JSON files written by the runbook in `src/infra/`.

Current output files written by the PowerShell script:
- `cdk-outputs-foundation.json`
- `cdk-outputs-data.json`
- `cdk-outputs-agent.json`
- `cdk-outputs-api.json`
- `cdk-outputs-workflow-frontend.json`

### Values to copy
| `.env.deploy` key | Source stack | Output name | Notes |
|---|---|---|---|
| `AWS_REGION` | manual | n/a | Must match deployed region |
| `BEDROCK_AGENT_ID` | `FinOpsAgent` | `SupervisorAgentId` | Required for runtime agent invocation |
| `BEDROCK_AGENT_ALIAS_ID` | manual/Bedrock console | n/a | Create alias after agent deploy |
| `COGNITO_USER_POOL_ID` | `FinOpsFoundation` / Cognito construct | `UserPoolId` | Output emitted from `cognito-pool.ts` |
| `COGNITO_CLIENT_ID` | `FinOpsFoundation` / Cognito construct | `UserPoolClientId` | Output emitted from `cognito-pool.ts` |
| `ATHENA_DATABASE` | `FinOpsData` | `GlueDatabaseName` | Current value is `finops_cost_db` |
| `ATHENA_WORKGROUP` | `FinOpsData` | `AthenaWorkGroupName` | Current value is `finops-primary` |
| `COST_EXPORT_S3_BUCKET` | `FinOpsData` | `CostExportsBucketName` | Required for CUR/Data Export pipeline |
| `ATHENA_RESULTS_S3_BUCKET` | `FinOpsData` | `AthenaResultsBucketName` | Required for Athena query results |
| `JIRA_BASE_URL` | manual | n/a | Example: `https://yourcompany.atlassian.net` |
| `STEP_FUNCTIONS_ARN` | `FinOpsWorkflow` | `StateMachineArn` | Required for workflow invocations |
| `DEMO_MODE` | manual | n/a | Keep `false` in deployed environments |

### Additional useful outputs
These are not copied into `.env.deploy` but are important after deploy:
- `FinOpsApi` -> `ApiUrl`
- `FinOpsFoundation` -> `JiraSecretArn`
- `FinOpsFoundation` -> `SlackSecretArn`
- `FinOpsFrontend` -> `ApiUrl`
- `FinOpsFrontend` -> `DeployNote`

## Recommended Deployment Flow
## Step 1. Run zero-cost validation first
From repo root:

```powershell
pwsh -File scripts/deploy/phase8-go-live.ps1 -ZeroBudget -SkipSmokeTests -SkipCognitoUsers
```

Expected outcome:
- backend dependencies install
- frontend dependencies install
- backend unit tests pass
- CDK synth passes
- no AWS resources are created

Use this mode before every real deployment if local code changed.

## Step 2. Prepare `.env.deploy`
Create and fill `.env.deploy`.

At minimum, confirm these values before a live deploy:
- `AWS_REGION`
- `JIRA_BASE_URL`
- `DEMO_MODE=false`

Some values are only available after the first deploy pass. In practice:
1. deploy stacks
2. capture output JSON
3. update `.env.deploy`
4. re-run targeted deploys if needed

## Step 3. Run the live PowerShell deployment
From repo root:

```powershell
pwsh -File scripts/deploy/phase8-go-live.ps1 -Region us-east-1
```

Windows CMD wrapper:

```cmd
scripts\deploy\phase8-go-live.cmd -Region us-east-1
```

What the script does:
1. verifies `node`, `npm`, and `python`
2. verifies AWS credentials are present in env vars
3. loads `.env.deploy` into the current process
4. runs `npm ci` in `src/infra`
5. runs `npm ci` in `src/frontend`
6. runs backend pip install and unit tests
7. runs `npx cdk synth`
8. runs CDK bootstrap for the target account and region
9. deploys stacks in dependency order
10. writes output JSON files in `src/infra`
11. prints manual Secrets Manager and smoke-test reminders

## Step 4. Deploy stacks manually if you need tighter control
If you need to pause between stacks, run from `src/infra`:

```powershell
npx cdk bootstrap aws://123456789012/us-east-1
npx cdk deploy FinOpsFoundation --require-approval broadening --outputs-file cdk-outputs-foundation.json
npx cdk deploy FinOpsData --require-approval broadening --outputs-file cdk-outputs-data.json
npx cdk deploy FinOpsAgent --require-approval broadening --outputs-file cdk-outputs-agent.json
npx cdk deploy FinOpsApi --require-approval broadening --outputs-file cdk-outputs-api.json
npx cdk deploy FinOpsWorkflow FinOpsFrontend --require-approval broadening --outputs-file cdk-outputs-workflow-frontend.json
```

Use the manual flow when:
- you need to inspect stack outputs between stages
- you are troubleshooting a specific stack
- you want tighter change control around `FinOpsApi` or `FinOpsFrontend`

## Secrets Manager Post-Deploy Tasks
After foundation deploy, populate these secrets in AWS Secrets Manager:
- `finops/jira-api-token`
- `finops/slack-webhook-url`

The current script reminds you to do this but does not create secret values automatically.

Recommended contents:
- `finops/jira-api-token`: the raw Jira API token or JSON shape expected by the adapter implementation
- `finops/slack-webhook-url`: JSON containing `webhook_url` or the exact secret format expected by the action adapter

Before storing secrets, confirm the runtime adapter expectation in backend code.

## Bedrock Agent Alias Setup
`BEDROCK_AGENT_ALIAS_ID` is not emitted automatically by CDK in the current flow.

After `FinOpsAgent` deploy:
1. open Amazon Bedrock console
2. find the deployed supervisor agent
3. create an alias such as `prod`
4. copy the alias ID into `.env.deploy`

If you prefer CLI later, use the Bedrock agent alias command with the emitted `SupervisorAgentId`.

## Post-Deploy Smoke Tests
Run these after `FinOpsApi` is up and you have a valid Cognito JWT.

### Health check
```bash
curl https://<api-url>/health
```

Expected result:
- HTTP 200
- JSON with `status` and `version`

### Cost query route
```bash
curl -H "Authorization: Bearer <jwt>" -X POST https://<api-url>/cost/query -d '{"prompt":"What is my spend this month?"}'
```

### Recommendations route
```bash
curl -H "Authorization: Bearer <jwt>" https://<api-url>/recommendations/
```

### Negative approval-path test
```bash
curl -H "Authorization: Bearer <jwt>" -X POST https://<api-url>/actions/execute -d '{"recommendation_id":"REC#TEST","approval_token":"bad-token","action_type":"rightsizing"}'
```

Expected result:
- request should fail safely
- invalid approval token must not execute any action

## Cognito Test Users
The current deployment script prints a reminder only. User creation is manual.

Create one test user for each role group:
- `finops-analyst`
- `engineering-manager`
- `finance`
- `leadership`

Recommended user set:
- `analyst-test@example.com`
- `engmgr-test@example.com`
- `finance-test@example.com`
- `leadership-test@example.com`

If you use AWS CLI later, the flow is:
1. `admin-create-user`
2. `admin-set-user-password` or first-login reset flow
3. `admin-add-user-to-group`

Validation target:
- finance and leadership users must be read-only
- action execution must require approval-token flow
- production write actions must remain blocked or gated per policy

## Deployment Verification Checklist
Confirm all of the following:
- `FinOpsFoundation` deployed successfully
- `FinOpsData` deployed successfully
- `FinOpsAgent` deployed successfully
- `FinOpsApi` deployed successfully
- `FinOpsWorkflow` deployed successfully
- `FinOpsFrontend` deployed successfully
- `src/infra/cdk-outputs-*.json` files were written
- `.env.deploy` updated from actual outputs
- Secrets Manager values populated
- Bedrock alias created and copied into `.env.deploy`
- `/health` returns 200
- authenticated read routes succeed
- invalid approval action is blocked
- no unintended production mutation path is enabled

## Rollback and Containment
If a later stack fails:
- stop and inspect that stack before retrying downstream stacks
- do not continue to workflow or frontend if API deploy is unhealthy
- keep `DEMO_MODE=false` in live environments unless you are intentionally running a demo environment

If `FinOpsApi` packaging fails:
- rerun `npx cdk synth` in `src/infra`
- confirm Python is on PATH
- confirm local bundling succeeded without Docker fallback
- inspect `src/infra/lib/stacks/api-stack.ts`

If runtime auth fails:
- verify `COGNITO_USER_POOL_ID`
- verify `COGNITO_CLIENT_ID`
- verify the JWT issuer and audience match the deployed pool and app client

If Bedrock calls fail:
- verify `BEDROCK_AGENT_ID`
- verify `BEDROCK_AGENT_ALIAS_ID`
- verify region consistency across shell env, `.env.deploy`, and deployed resources

## Common Failure Modes
### 1. Missing AWS credentials
Symptom:
- script aborts before deployment

Fix:
- export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- set `AWS_DEFAULT_REGION`

### 2. Bootstrap account placeholder
Symptom:
- bootstrap command uses `unknown` account value

Fix:
- set `CDK_DEFAULT_ACCOUNT` explicitly before running the script
- alternatively run manual `npx cdk bootstrap aws://<ACCOUNT>/<REGION>`

### 3. Docker fallback during synth
Symptom:
- CDK tries Docker and fails with `spawnSync docker ENOENT`

Current status:
- local Windows bundling is fixed in the current repo state

Fix if this reappears:
- rerun synth from `src/infra`
- inspect the local bundling logic in `api-stack.ts`
- verify Python dependency install succeeds locally

### 4. Secret lookup failures at runtime
Symptom:
- Jira or Slack actions fail even though API is up

Fix:
- confirm secret values were created in Secrets Manager
- confirm secret names exactly match the code and stack env vars

### 5. `.env.deploy` drift
Symptom:
- runtime points at old resource IDs after redeploy

Fix:
- regenerate outputs with the latest deploy
- repopulate `.env.deploy`
- restart any local process that cached old environment variables

## Recommended Command Set
### Zero-cost preflight
```powershell
pwsh -File scripts/deploy/phase8-go-live.ps1 -ZeroBudget -SkipSmokeTests -SkipCognitoUsers
```

### Full deploy
```powershell
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "<secret>"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:CDK_DEFAULT_REGION = "us-east-1"
$env:CDK_DEFAULT_ACCOUNT = "123456789012"
pwsh -File scripts/deploy/phase8-go-live.ps1 -Region us-east-1
```

### Deploy without smoke tests
```powershell
pwsh -File scripts/deploy/phase8-go-live.ps1 -Region us-east-1 -SkipSmokeTests
```

### Deploy without Cognito test-user reminder
```powershell
pwsh -File scripts/deploy/phase8-go-live.ps1 -Region us-east-1 -SkipCognitoUsers
```

## Ownership and Next Action
Primary operator:
- engineer running deployment from the repo root on Windows PowerShell

Recommended next action when AWS credentials are ready:
1. run zero-budget preflight
2. set AWS credential env vars and `CDK_DEFAULT_ACCOUNT`
3. run the live PowerShell deploy
4. populate secrets and alias
5. run smoke tests
6. update release status after AWS verification
