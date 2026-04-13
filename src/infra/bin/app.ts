#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { FoundationStack } from '../lib/stacks/foundation-stack';
import { DataStack } from '../lib/stacks/data-stack';
import { AgentStack } from '../lib/stacks/agent-stack';
import { ApiStack } from '../lib/stacks/api-stack';
import { WorkflowStack } from '../lib/stacks/workflow-stack';
import { FrontendStack } from '../lib/stacks/frontend-stack';

const app = new cdk.App();
const env = {
  account: process.env.CDK_ACCOUNT ?? process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_REGION ?? process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
};

const foundation = new FoundationStack(app, 'FinOpsFoundation', { env });
const data = new DataStack(app, 'FinOpsData', { env, foundation });
const agent = new AgentStack(app, 'FinOpsAgent', { env, data });
const api = new ApiStack(app, 'FinOpsApi', { env, foundation, agent });
const workflow = new WorkflowStack(app, 'FinOpsWorkflow', { env, api });
new FrontendStack(app, 'FinOpsFrontend', { env, api });

// Add dependency metadata
data.addDependency(foundation);
agent.addDependency(data);
api.addDependency(agent);
workflow.addDependency(api);
