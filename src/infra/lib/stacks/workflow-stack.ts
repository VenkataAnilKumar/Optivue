import * as cdk from 'aws-cdk-lib';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { ApiStack } from './api-stack';

export interface WorkflowStackProps extends cdk.StackProps {
  api: ApiStack;
}

export class WorkflowStack extends cdk.Stack {
  public readonly stateMachineArn: string;

  constructor(scope: Construct, id: string, props: WorkflowStackProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, 'WorkflowLogGroup', {
      logGroupName: '/aws/states/finops-action-workflow',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const approvalBlocked = new sfn.Fail(this, 'ApprovalBlocked', {
      error: 'ApprovalRequired',
      cause: 'Action requires a valid approval token',
    });

    const validateApproval = new tasks.LambdaInvoke(this, 'ValidateApproval', {
      lambdaFunction: props.api.apiHandler,
      payload: sfn.TaskInput.fromObject({
        action: 'validate_approval',
        'approval_token.$': '$.approval_token',
        'recommendation_id.$': '$.recommendation_id',
      }),
      resultSelector: { 'approved.$': '$.Payload.approved' },
      resultPath: '$.validation',
    });

    const createTicket = new tasks.LambdaInvoke(this, 'CreateTicket', {
      lambdaFunction: props.api.apiHandler,
      payload: sfn.TaskInput.fromObject({
        action: 'create_ticket',
        'recommendation_id.$': '$.recommendation_id',
        'approval_token.$': '$.approval_token',
      }),
      resultPath: '$.ticket',
    });

    const notifyOwner = new tasks.LambdaInvoke(this, 'NotifyOwner', {
      lambdaFunction: props.api.apiHandler,
      payload: sfn.TaskInput.fromObject({
        action: 'notify_owner',
        'recommendation_id.$': '$.recommendation_id',
        'ticket_url.$': '$.ticket.Payload.ticket_url',
      }),
      resultPath: '$.notification',
    });

    const approvalCheck = new sfn.Choice(this, 'ApprovalCheck')
      .when(
        sfn.Condition.booleanEquals('$.validation.approved', true),
        createTicket.next(notifyOwner)
      )
      .otherwise(approvalBlocked);

    const definition = validateApproval.next(approvalCheck);

    const role = new iam.Role(this, 'StateMachineRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com'),
    });
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['lambda:InvokeFunction'],
      resources: [props.api.apiHandler.functionArn],
    }));
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['logs:CreateLogDelivery', 'logs:PutLogEvents', 'logs:CreateLogGroup',
        'logs:GetLogDelivery', 'logs:UpdateLogDelivery', 'logs:DeleteLogDelivery',
        'logs:ListLogDeliveries', 'logs:PutResourcePolicy', 'logs:DescribeResourcePolicies',
        'logs:DescribeLogGroups'],
      resources: ['*'],
    }));
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['xray:PutTraceSegments', 'xray:PutTelemetryRecords', 'xray:GetSamplingRules',
        'xray:GetSamplingTargets'],
      resources: ['*'],
    }));

    const stateMachine = new sfn.StateMachine(this, 'ActionWorkflow', {
      stateMachineName: 'finops-action-workflow',
      definitionBody: sfn.DefinitionBody.fromChainable(definition),
      role,
      logs: {
        destination: logGroup,
        level: sfn.LogLevel.ALL,
        includeExecutionData: true,
      },
      tracingEnabled: true,
    });

    this.stateMachineArn = stateMachine.stateMachineArn;

    // EventBridge rule: trigger on ApprovalConfirmed
    const rule = new events.Rule(this, 'ApprovalConfirmedRule', {
      ruleName: 'finops-approval-confirmed',
      eventPattern: {
        source: ['finops.approval'],
        detailType: ['ApprovalConfirmed'],
      },
    });
    rule.addTarget(new targets.SfnStateMachine(stateMachine));

    // KPI weekly schedule - Monday 06:00 UTC
    new events.Rule(this, 'KpiWeeklyRule', {
      ruleName: 'finops-kpi-weekly',
      schedule: events.Schedule.cron({ minute: '0', hour: '6', weekDay: 'MON' }),
      targets: [new targets.LambdaFunction(props.api.apiHandler, {
        event: events.RuleTargetInput.fromObject({ action: 'compute_kpis' }),
      })],
    });

    new cdk.CfnOutput(this, 'StateMachineArn', {
      value: stateMachine.stateMachineArn,
      exportName: 'FinOpsStateMachineArn',
    });
  }
}
