import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as athena from 'aws-cdk-lib/aws-athena';
import { Construct } from 'constructs';
import { FoundationStack } from './foundation-stack';

export interface DataStackProps extends cdk.StackProps {
  foundation: FoundationStack;
}

export class DataStack extends cdk.Stack {
  public readonly costExportsBucket: s3.Bucket;
  public readonly athenaResultsBucket: s3.Bucket;
  public readonly glueDatabase: glue.CfnDatabase;
  public readonly athenaWorkGroup: athena.CfnWorkGroup;

  constructor(scope: Construct, id: string, props: DataStackProps) {
    super(scope, id, props);

    this.costExportsBucket = new s3.Bucket(this, 'CostExportsBucket', {
      bucketName: `finops-cost-exports-${this.account}`,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    this.athenaResultsBucket = new s3.Bucket(this, 'AthenaResultsBucket', {
      bucketName: `finops-athena-results-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [{
        id: 'delete-old-query-results',
        expiration: cdk.Duration.days(30),
        enabled: true,
      }],
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.glueDatabase = new glue.CfnDatabase(this, 'GlueDatabase', {
      catalogId: this.account,
      databaseInput: {
        name: 'finops_cost_db',
        description: 'FinOps cost data from AWS CUR/Data Exports',
      },
    });

    this.athenaWorkGroup = new athena.CfnWorkGroup(this, 'AthenaWorkGroup', {
      name: 'finops-primary',
      workGroupConfiguration: {
        resultConfiguration: {
          outputLocation: `s3://${this.athenaResultsBucket.bucketName}/query-results/`,
        },
        enforceWorkGroupConfiguration: true,
        publishCloudWatchMetricsEnabled: true,
      },
    });

    new cdk.CfnOutput(this, 'CostExportsBucketName', { value: this.costExportsBucket.bucketName });
    new cdk.CfnOutput(this, 'AthenaResultsBucketName', { value: this.athenaResultsBucket.bucketName });
    new cdk.CfnOutput(this, 'GlueDatabaseName', { value: 'finops_cost_db' });
    new cdk.CfnOutput(this, 'AthenaWorkGroupName', { value: 'finops-primary' });
  }
}
