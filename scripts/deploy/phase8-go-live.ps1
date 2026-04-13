param(
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-east-1",

    [Parameter(Mandatory = $false)]
    [switch]$SkipSmokeTests,

    [Parameter(Mandatory = $false)]
    [switch]$SkipCognitoUsers

    ,
    [Parameter(Mandatory = $false)]
    [switch]$ZeroBudget
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Run {
    param([string]$Command)
    Write-Host "[run] $Command" -ForegroundColor DarkGray
    Invoke-Expression $Command
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$infraDir = Join-Path $repoRoot "src/infra"
$backendDir = Join-Path $repoRoot "src/backend"
$deployEnvPath = Join-Path $repoRoot ".env.deploy"

Write-Step "Phase 8 prereq checks"
Require-Command "node"
Require-Command "npm"
Require-Command "python"

Push-Location $infraDir
try {
    Run "npx cdk --version"
}
finally {
    Pop-Location
}

if (-not $ZeroBudget) {
    # Verify AWS credentials are available as env vars (no CLI required)
    if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
        throw @"
AWS credentials not found. Set these environment variables before running:
  `$env:AWS_ACCESS_KEY_ID     = 'AKIA...'
  `$env:AWS_SECRET_ACCESS_KEY = 'your-secret'
  `$env:AWS_DEFAULT_REGION    = '$Region'
Obtain keys from: AWS Console > IAM > Users > Security credentials > Create access key
"@
    }

    # Propagate region so CDK SDK picks it up
    $env:AWS_DEFAULT_REGION = $Region
    $env:CDK_DEFAULT_REGION = $Region
    Write-Host "  Credentials detected for key: $($env:AWS_ACCESS_KEY_ID.Substring(0,8))..." -ForegroundColor Green

    if (-not (Test-Path $deployEnvPath)) {
        throw "Missing .env.deploy at $deployEnvPath. Create it from .env.deploy.example before continuing."
    }

    Write-Step "Loading deployment environment from .env.deploy"
    Get-Content $deployEnvPath |
        Where-Object { $_ -and -not $_.StartsWith("#") } |
        ForEach-Object {
            $parts = $_ -split "=", 2
            if ($parts.Length -eq 2) {
                [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
            }
        }
}

Write-Step "Bootstrap dependencies"
Push-Location $infraDir
try {
    Run "npm ci"
}
finally {
    Pop-Location
}

Push-Location (Join-Path $repoRoot "src/frontend")
try {
    Run "npm ci"
}
finally {
    Pop-Location
}

Push-Location $backendDir
try {
    Run "python -m pip install -r requirements.txt -r requirements-dev.txt"
    Run "python -m pytest tests/unit/ -q"
}
finally {
    Pop-Location
}

Write-Step "Synthesizing CDK"
Push-Location $infraDir
try {
    Run "npx cdk synth"
}
finally {
    Pop-Location
}

Write-Step "Deploy stacks in dependency order"
if (-not $ZeroBudget) {
    Push-Location $infraDir
    try {
        Write-Step "CDK Bootstrap (one-time per account/region)"
        Run "npx cdk bootstrap aws://$($env:CDK_DEFAULT_ACCOUNT ?? 'unknown')/$Region"

        Run "npx cdk deploy FinOpsFoundation --require-approval broadening --outputs-file cdk-outputs-foundation.json"
        Run "npx cdk deploy FinOpsData --require-approval broadening --outputs-file cdk-outputs-data.json"
        Run "npx cdk deploy FinOpsAgent --require-approval broadening --outputs-file cdk-outputs-agent.json"
        Run "npx cdk deploy FinOpsApi --require-approval broadening --outputs-file cdk-outputs-api.json"
        Run "npx cdk deploy FinOpsWorkflow FinOpsFrontend --require-approval broadening --outputs-file cdk-outputs-workflow-frontend.json"

        Write-Host "`nStack outputs saved to src/infra/cdk-outputs-*.json" -ForegroundColor Green
        Write-Host "Use these to populate .env.deploy (see .env.deploy.example for field mapping)." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

if (-not $ZeroBudget) {
    Write-Step "Manual secret population reminder"
    Write-Host "Set Jira and Slack secrets in Secrets Manager:" -ForegroundColor Yellow
    Write-Host "  finops/jira-api-token" -ForegroundColor Yellow
    Write-Host "  finops/slack-webhook-url" -ForegroundColor Yellow
}

if (-not $SkipSmokeTests -and -not $ZeroBudget) {
    Write-Step "Post-deploy smoke test commands"
    Write-Host "Run these once you have API URL + JWT:" -ForegroundColor Yellow
    Write-Host "  curl https://<api-url>/health" -ForegroundColor Yellow
    Write-Host "  curl -H 'Authorization: Bearer <jwt>' -X POST https://<api-url>/cost/query -d '{\"prompt\":\"What is my spend this month?\"}'" -ForegroundColor Yellow
    Write-Host "  curl -H 'Authorization: Bearer <jwt>' https://<api-url>/recommendations/" -ForegroundColor Yellow
    Write-Host "  curl -H 'Authorization: Bearer <jwt>' -X POST https://<api-url>/actions/execute -d '{\"recommendation_id\":\"REC#TEST\",\"approval_token\":\"bad-token\",\"action_type\":\"rightsizing\"}'" -ForegroundColor Yellow
}

if (-not $SkipCognitoUsers -and -not $ZeroBudget) {
    Write-Step "Cognito user creation templates"
    Write-Host "Create test users for each role group with aws cognito-idp admin-create-user/admin-add-user-to-group." -ForegroundColor Yellow
}

if ($ZeroBudget) {
    Write-Step "Zero-budget mode complete"
    Write-Host "Cloud deployment was skipped. Local validation gates are complete with no AWS spend." -ForegroundColor Green
    Write-Host "Use DEMO_MODE=true for product walkthroughs and evaluation artifacts." -ForegroundColor Green
}
else {
    Write-Step "Phase 8 automation complete"
    Write-Host "If all smoke checks pass in AWS, update CHANGELOG and mark Phase 8 checklist complete." -ForegroundColor Green
}
