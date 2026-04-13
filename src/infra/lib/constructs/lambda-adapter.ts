import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import { Construct } from 'constructs';

export interface LambdaAdapterProps {
	functionName: string;
	codePath: string;
	handler: string;
	role?: lambda.IRole;
	environment?: Record<string, string>;
	memorySizeMb?: number;
	timeoutSeconds?: number;
	architecture?: lambda.Architecture;
}

export interface LambdaRouteBindingProps {
	api: apigatewayv2.HttpApi;
	path: string;
	methods: apigatewayv2.HttpMethod[];
	authorizer?: apigatewayv2.IHttpRouteAuthorizer;
}

export class LambdaAdapter extends Construct {
	public readonly fn: lambda.Function;

	constructor(scope: Construct, id: string, props: LambdaAdapterProps) {
		super(scope, id);

		this.fn = new lambda.Function(this, 'Function', {
			functionName: props.functionName,
			runtime: lambda.Runtime.PYTHON_3_12,
			handler: props.handler,
			code: lambda.Code.fromAsset(props.codePath),
			role: props.role,
			memorySize: props.memorySizeMb ?? 512,
			timeout: cdk.Duration.seconds(props.timeoutSeconds ?? 30),
			architecture: props.architecture ?? lambda.Architecture.ARM_64,
			environment: props.environment,
		});
	}

	public bindHttpRoute(id: string, props: LambdaRouteBindingProps): void {
		const integration = new integrations.HttpLambdaIntegration(`${id}Integration`, this.fn);
		props.api.addRoutes({
			path: props.path,
			methods: props.methods,
			integration,
			authorizer: props.authorizer,
		});
	}
}

