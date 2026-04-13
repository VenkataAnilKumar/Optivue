import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import { Construct } from 'constructs';

export interface BedrockAgentConstructProps {
	agentName: string;
	instruction: string;
	foundationModel: string;
	roleName?: string;
	idleSessionTtlInSeconds?: number;
	aliasName?: string;
	description?: string;
}

export class BedrockAgentConstruct extends Construct {
	public readonly role: iam.Role;
	public readonly agent: bedrock.CfnAgent;
	public readonly alias: bedrock.CfnAgentAlias;

	constructor(scope: Construct, id: string, props: BedrockAgentConstructProps) {
		super(scope, id);

		this.role = new iam.Role(this, 'Role', {
			roleName: props.roleName,
			assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
		});

		this.role.addToPolicy(
			new iam.PolicyStatement({
				actions: ['bedrock:InvokeModel'],
				resources: ['*'],
			}),
		);

		this.role.addToPolicy(
			new iam.PolicyStatement({
				actions: ['lambda:InvokeFunction'],
				resources: ['*'],
			}),
		);

		this.agent = new bedrock.CfnAgent(this, 'Agent', {
			agentName: props.agentName,
			instruction: props.instruction,
			foundationModel: props.foundationModel,
			agentResourceRoleArn: this.role.roleArn,
			idleSessionTtlInSeconds: props.idleSessionTtlInSeconds ?? 600,
			description: props.description,
			autoPrepare: true,
		});

		this.alias = new bedrock.CfnAgentAlias(this, 'Alias', {
			agentAliasName: props.aliasName ?? 'prod',
			agentId: this.agent.attrAgentId,
			description: `${props.agentName} alias`,
		});
	}
}

