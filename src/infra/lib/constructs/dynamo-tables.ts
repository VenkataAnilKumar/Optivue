import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class FinOpsTables extends Construct {
  public readonly recommendations: dynamodb.Table;
  public readonly approvals: dynamodb.Table;
  public readonly actionHistory: dynamodb.Table;
  public readonly kpiMetrics: dynamodb.Table;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Table 1: finops-recommendations
    this.recommendations = new dynamodb.Table(this, 'Recommendations', {
      tableName: 'finops-recommendations',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true,
      },
      timeToLiveAttribute: 'ttl',
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.recommendations.addGlobalSecondaryIndex({
      indexName: 'by-owner-status-index',
      partitionKey: { name: 'owner', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'status', type: dynamodb.AttributeType.STRING },
    });
    this.recommendations.addGlobalSecondaryIndex({
      indexName: 'by-priority-created-index',
      partitionKey: { name: 'priority_tier', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
    });

    // Table 2: finops-approvals
    this.approvals = new dynamodb.Table(this, 'Approvals', {
      tableName: 'finops-approvals',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true,
      },
      timeToLiveAttribute: 'ttl',
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.approvals.addGlobalSecondaryIndex({
      indexName: 'by-recommendation-index',
      partitionKey: { name: 'recommendation_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
    });
    this.approvals.addGlobalSecondaryIndex({
      indexName: 'by-status-index',
      partitionKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
    });

    // Table 3: finops-action-history — append-only, NO TTL
    this.actionHistory = new dynamodb.Table(this, 'ActionHistory', {
      tableName: 'finops-action-history',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true,
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.actionHistory.addGlobalSecondaryIndex({
      indexName: 'by-recommendation-index',
      partitionKey: { name: 'recommendation_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'executed_at', type: dynamodb.AttributeType.STRING },
    });
    this.actionHistory.addGlobalSecondaryIndex({
      indexName: 'by-actor-date-index',
      partitionKey: { name: 'actor', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'executed_at', type: dynamodb.AttributeType.STRING },
    });

    // Table 4: finops-kpi-metrics
    this.kpiMetrics = new dynamodb.Table(this, 'KpiMetrics', {
      tableName: 'finops-kpi-metrics',
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true,
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
  }
}
