import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import { Construct } from 'constructs';
import { DataStack } from './data-stack';

export interface AgentStackProps extends cdk.StackProps {
  data: DataStack;
}

const SUPERVISOR_INSTRUCTION = `You are the FinOps Supervisor Agent for a cloud cost management platform. Your role is to understand the user's intent and route their request to the most appropriate specialist agent.

You have access to three specialist agents:
- cost-analysis-agent: handles spend queries, trend analysis, anomaly explanation, budget variance, and forecast.
- optimization-agent: handles savings opportunity discovery, rightsizing, idle resource identification, commitment recommendations, and ranked prioritization.
- governance-agent: handles tag policy compliance, budget policy enforcement, approval gating, and risk classification.

Rules:
1. Always clarify ambiguous scope before routing (e.g., "Which time period?" or "Which account or environment?").
2. Route to exactly one specialist unless the request explicitly spans multiple domains.
3. Never execute a write action (ticket creation, notification, resource mutation) without confirmed user approval.
4. Always include data freshness timestamp and source reference in responses.
5. If a specialist agent returns low-confidence results, surface the confidence score and recommend a follow-up action.
6. Responses must be factual and grounded in tool-returned data. Do not infer or hallucinate cost figures.
7. Account numbers must be redacted for roles below finops-analyst.`;

export class AgentStack extends cdk.Stack {
  public readonly supervisorAgentId: cdk.CfnOutput;

  constructor(scope: Construct, id: string, props: AgentStackProps) {
    super(scope, id, props);

    const agentRole = new iam.Role(this, 'BedrockAgentRole', {
      roleName: 'finops-bedrock-agent-role',
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
    });
    agentRole.addToPolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: ['*'],
    }));
    agentRole.addToPolicy(new iam.PolicyStatement({
      actions: ['lambda:InvokeFunction'],
      resources: ['*'],
    }));

    const supervisorAgent = new bedrock.CfnAgent(this, 'SupervisorAgent', {
      agentName: 'finops-supervisor',
      instruction: SUPERVISOR_INSTRUCTION,
      foundationModel: 'anthropic.claude-sonnet-4-5',
      agentResourceRoleArn: agentRole.roleArn,
      idleSessionTtlInSeconds: 600,
    });

    this.supervisorAgentId = new cdk.CfnOutput(this, 'SupervisorAgentId', {
      value: supervisorAgent.attrAgentId,
      exportName: 'FinOpsSupervisorAgentId',
    });
  }
}
