import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { FoundationStack } from '../lib/stacks/foundation-stack';

test('Cognito User Pool exists', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestFoundation');
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::Cognito::UserPool', 1);
  template.resourceCountIs('AWS::Cognito::UserPoolClient', 1);
});

test('All 4 Cognito groups exist', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestFoundation2');
  const template = Template.fromStack(stack);
  const groups = ['finops-analyst', 'engineering-manager', 'finance', 'leadership'];
  groups.forEach((groupName) => {
    template.hasResourceProperties('AWS::Cognito::UserPoolGroup', { GroupName: groupName });
  });
});

test('Cognito self-signup is disabled', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestFoundation3');
  const template = Template.fromStack(stack);
  template.hasResourceProperties('AWS::Cognito::UserPool', {
    AdminCreateUserConfig: { AllowAdminCreateUserOnly: true },
  });
});

test('Secrets Manager placeholders exist', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestFoundation4');
  const template = Template.fromStack(stack);
  template.hasResourceProperties('AWS::SecretsManager::Secret', { Name: 'finops/jira-api-token' });
  template.hasResourceProperties('AWS::SecretsManager::Secret', { Name: 'finops/slack-webhook-url' });
});
