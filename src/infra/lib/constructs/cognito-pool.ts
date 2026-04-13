import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import { Construct } from 'constructs';

export class CognitoPool extends Construct {
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: 'finops-users',
      selfSignUpEnabled: false,
      signInAliases: { email: true },
      autoVerify: { email: true },
      passwordPolicy: {
        minLength: 12,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: true,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const groups: string[] = ['finops-analyst', 'engineering-manager', 'finance', 'leadership'];
    groups.forEach((groupName) => {
      new cognito.CfnUserPoolGroup(this, `Group-${groupName}`, {
        userPoolId: this.userPool.userPoolId,
        groupName,
      });
    });

    this.userPoolClient = this.userPool.addClient('WebClient', {
      userPoolClientName: 'finops-web-client',
      generateSecret: false,
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
    });

    new cdk.CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
      exportName: 'FinOpsUserPoolId',
    });
    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: this.userPoolClient.userPoolClientId,
      exportName: 'FinOpsUserPoolClientId',
    });
  }
}
