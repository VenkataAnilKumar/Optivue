import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { FoundationStack } from '../lib/stacks/foundation-stack';

test('All 4 DynamoDB tables are created', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestDynamo');
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::DynamoDB::Table', 4);
});

test('Recommendations table has correct GSIs', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestDynamo2');
  const template = Template.fromStack(stack);
  template.hasResourceProperties('AWS::DynamoDB::Table', {
    TableName: 'finops-recommendations',
    GlobalSecondaryIndexes: [
      {
        IndexName: 'by-owner-status-index',
        KeySchema: [
          { AttributeName: 'owner', KeyType: 'HASH' },
          { AttributeName: 'status', KeyType: 'RANGE' },
        ],
      },
      {
        IndexName: 'by-priority-created-index',
        KeySchema: [
          { AttributeName: 'priority_tier', KeyType: 'HASH' },
          { AttributeName: 'created_at', KeyType: 'RANGE' },
        ],
      },
    ],
  });
});

test('Approvals table has correct GSIs', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestDynamo3');
  const template = Template.fromStack(stack);
  template.hasResourceProperties('AWS::DynamoDB::Table', {
    TableName: 'finops-approvals',
    GlobalSecondaryIndexes: [
      { IndexName: 'by-recommendation-index' },
      { IndexName: 'by-status-index' },
    ],
  });
});

test('Action history table has NO TTL (append-only audit trail)', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestDynamo4');
  const template = Template.fromStack(stack);
  const tables = template.findResources('AWS::DynamoDB::Table');
  const actionHistory = Object.values(tables).find(
    (t: any) => t.Properties.TableName === 'finops-action-history'
  ) as any;
  expect(actionHistory?.Properties?.TimeToLiveSpecification).toBeUndefined();
});

test('All tables use PAY_PER_REQUEST billing and PITR', () => {
  const app = new cdk.App();
  const stack = new FoundationStack(app, 'TestDynamo5');
  const template = Template.fromStack(stack);
  const tables = template.findResources('AWS::DynamoDB::Table');
  Object.values(tables).forEach((t: any) => {
    expect(t.Properties.BillingMode).toBe('PAY_PER_REQUEST');
    expect(t.Properties.PointInTimeRecoverySpecification?.PointInTimeRecoveryEnabled).toBe(true);
  });
});
