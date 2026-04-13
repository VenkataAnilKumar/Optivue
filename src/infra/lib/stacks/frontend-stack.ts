import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { ApiStack } from './api-stack';

export interface FrontendStackProps extends cdk.StackProps {
  api: ApiStack;
}

export class FrontendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    // Amplify hosting is managed via amplify.yml / console.
    // This stack captures configuration outputs for the frontend build.
    new cdk.CfnOutput(this, 'ApiUrl', { value: props.api.apiUrl });
    new cdk.CfnOutput(this, 'DeployNote', {
      value: 'Connect frontend repo to AWS Amplify Hosting via the console or amplify CLI',
    });
  }
}
