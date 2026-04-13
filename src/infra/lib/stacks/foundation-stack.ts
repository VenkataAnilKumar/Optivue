import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';
import { CognitoPool } from '../constructs/cognito-pool';
import { FinOpsTables } from '../constructs/dynamo-tables';

export class FoundationStack extends cdk.Stack {
  public readonly cognito: CognitoPool;
  public readonly tables: FinOpsTables;
  public readonly backendRole: iam.Role;
  public readonly jiraSecret: secretsmanager.Secret;
  public readonly slackSecret: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.cognito = new CognitoPool(this, 'CognitoPool');
    this.tables = new FinOpsTables(this, 'FinOpsTables');

    this.jiraSecret = new secretsmanager.Secret(this, 'JiraSecret', {
      secretName: 'finops/jira-api-token',
      description: 'Jira API token for FinOps ticket creation',
    });
    this.slackSecret = new secretsmanager.Secret(this, 'SlackSecret', {
      secretName: 'finops/slack-webhook-url',
      description: 'Slack webhook URL for FinOps notifications',
    });

    const baseLoggingPolicy = new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
      resources: ['arn:aws:logs:*:*:*'],
    });

    this.backendRole = new iam.Role(this, 'BackendRole', {
      roleName: 'finops-backend-role',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });
    this.backendRole.addToPolicy(baseLoggingPolicy);
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        'dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem',
        'dynamodb:Query', 'dynamodb:Scan',
      ],
      resources: [
        this.tables.recommendations.tableArn,
        `${this.tables.recommendations.tableArn}/index/*`,
        this.tables.approvals.tableArn,
        `${this.tables.approvals.tableArn}/index/*`,
        this.tables.actionHistory.tableArn,
        `${this.tables.actionHistory.tableArn}/index/*`,
        this.tables.kpiMetrics.tableArn,
      ],
    }));
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeAgent', 'bedrock-agent-runtime:InvokeAgent'],
      resources: ['*'],
    }));
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        'ce:GetCostAndUsage', 'ce:GetAnomalies', 'ce:GetCostForecast',
        'budgets:DescribeBudgets', 'budgets:DescribeBudgetPerformanceHistory',
        'athena:StartQueryExecution', 'athena:GetQueryExecution', 'athena:GetQueryResults',
        's3:GetObject', 's3:PutObject', 's3:ListBucket',
        'compute-optimizer:GetEC2InstanceRecommendations',
        'compute-optimizer:GetRecommendationSummaries',
        'support:DescribeTrustedAdvisorChecks',
        'support:DescribeTrustedAdvisorCheckResult',
      ],
      resources: ['*'],
    }));
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: ['states:StartExecution', 'states:DescribeExecution'],
      resources: ['*'],
    }));
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: ['secretsmanager:GetSecretValue'],
      resources: [this.jiraSecret.secretArn, this.slackSecret.secretArn],
    }));
    this.backendRole.addToPolicy(new iam.PolicyStatement({
      actions: ['cloudwatch:PutMetricData'],
      resources: ['*'],
    }));

    new cdk.CfnOutput(this, 'JiraSecretArn', { value: this.jiraSecret.secretArn });
    new cdk.CfnOutput(this, 'SlackSecretArn', { value: this.slackSecret.secretArn });
  }
}
