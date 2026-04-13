import * as cdk from 'aws-cdk-lib';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as authorizers from 'aws-cdk-lib/aws-apigatewayv2-authorizers';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';
import { FoundationStack } from './foundation-stack';
import { AgentStack } from './agent-stack';
import * as path from 'path';

export interface ApiStackProps extends cdk.StackProps {
  foundation: FoundationStack;
  agent: AgentStack;
}

export class ApiStack extends cdk.Stack {
  public readonly apiUrl: string;
  public readonly apiHandler: lambda.Function;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, 'ApiHandlerLogGroup', {
      logGroupName: '/aws/lambda/finops-api-handler',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.apiHandler = new lambda.Function(this, 'ApiHandler', {
      functionName: 'finops-api-handler',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'app.main.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../backend'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            [
              'pip install -r requirements.txt -t /asset-output --quiet --no-cache-dir',
              'cp -r app adapters /asset-output/',
            ].join(' && '),
          ],
          // Fallback for machines without Docker: pre-install deps locally
          local: {
            tryBundle(outputDir: string): boolean {
              const { execSync } = require('child_process');
              const fs = require('fs');
              const src = path.join(__dirname, '../../../backend');
              const shouldCopy = (entry: string): boolean => {
                const base = path.basename(entry);
                if (base === '__pycache__' || base === '.pytest_cache' || base === 'tests') {
                  return false;
                }
                if (entry.endsWith('.pyc')) {
                  return false;
                }
                return true;
              };
              try {
                execSync(
                  `python -m pip install -r requirements.txt -t "${outputDir}" --quiet --no-cache-dir`,
                  { cwd: src, stdio: 'inherit' },
                );
                fs.cpSync(path.join(src, 'app'), path.join(outputDir, 'app'), {
                  recursive: true,
                  filter: shouldCopy,
                });
                fs.cpSync(path.join(src, 'adapters'), path.join(outputDir, 'adapters'), {
                  recursive: true,
                  filter: shouldCopy,
                });
                return true;
              } catch {
                return false;  // fall back to Docker
              }
            },
          },
        },
      }),
      role: props.foundation.backendRole,
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      environment: {
        AWS_REGION_NAME: this.region,
        COGNITO_USER_POOL_ID: props.foundation.cognito.userPool.userPoolId,
        COGNITO_CLIENT_ID: props.foundation.cognito.userPoolClient.userPoolClientId,
        DYNAMODB_RECOMMENDATIONS_TABLE: 'finops-recommendations',
        DYNAMODB_APPROVALS_TABLE: 'finops-approvals',
        DYNAMODB_ACTION_HISTORY_TABLE: 'finops-action-history',
        DYNAMODB_KPI_TABLE: 'finops-kpi-metrics',
        JIRA_SECRET_NAME: 'finops/jira-api-token',
        SLACK_SECRET_NAME: 'finops/slack-webhook-url',
        DEMO_MODE: 'false',
      },
      logGroup,
    });

    const authorizer = new authorizers.HttpJwtAuthorizer(
      'CognitoAuthorizer',
      `https://cognito-idp.${this.region}.amazonaws.com/${props.foundation.cognito.userPool.userPoolId}`,
      {
        jwtAudience: [props.foundation.cognito.userPoolClient.userPoolClientId],
      }
    );

    const httpApi = new apigatewayv2.HttpApi(this, 'HttpApi', {
      apiName: 'finops-api',
      corsPreflight: {
        allowHeaders: ['Content-Type', 'Authorization'],
        allowMethods: [apigatewayv2.CorsHttpMethod.ANY],
        allowOrigins: ['*'],
      },
    });

    const lambdaIntegration = new integrations.HttpLambdaIntegration(
      'LambdaIntegration',
      this.apiHandler
    );

    // Health — no auth
    httpApi.addRoutes({
      path: '/health',
      methods: [apigatewayv2.HttpMethod.GET],
      integration: lambdaIntegration,
    });

    // All other routes — Cognito JWT required
    httpApi.addRoutes({
      path: '/{proxy+}',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: lambdaIntegration,
      authorizer,
    });

    this.apiUrl = httpApi.apiEndpoint;

    // Observability
    const alertsTopic = new sns.Topic(this, 'AlertsTopic', { topicName: 'finops-alerts' });

    new cloudwatch.Dashboard(this, 'Dashboard', { dashboardName: 'finops-agent-dashboard' });

    const errAlarm = new cloudwatch.Alarm(this, 'LambdaErrorRate', {
      alarmName: 'finops-lambda-error-rate',
      metric: this.apiHandler.metricErrors({ period: cdk.Duration.minutes(1) }),
      threshold: 5,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
    });
    errAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(alertsTopic));

    const safetyAlarm = new cloudwatch.Alarm(this, 'SafetyViolationAlarm', {
      alarmName: 'finops-action-safety-violation',
      metric: new cloudwatch.Metric({
        namespace: 'finops',
        metricName: 'ActionSafetyViolations',
        statistic: 'Sum',
        period: cdk.Duration.minutes(1),
      }),
      threshold: 0,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    safetyAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(alertsTopic));

    new cdk.CfnOutput(this, 'ApiUrl', { value: this.apiUrl, exportName: 'FinOpsApiUrl' });
  }
}
