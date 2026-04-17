from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    bedrock_agent_id: str = Field(default="", alias="BEDROCK_AGENT_ID")
    bedrock_agent_alias_id: str = Field(default="TSTALIASID", alias="BEDROCK_AGENT_ALIAS_ID")
    athena_database: str = Field(default="finops_cost_db", alias="ATHENA_DATABASE")
    athena_workgroup: str = Field(default="finops-primary", alias="ATHENA_WORKGROUP")
    cost_export_s3_bucket: str = Field(default="", alias="COST_EXPORT_S3_BUCKET")
    athena_results_s3_bucket: str = Field(default="", alias="ATHENA_RESULTS_S3_BUCKET")
    dynamodb_recommendations_table: str = Field(default="finops-recommendations", alias="DYNAMODB_RECOMMENDATIONS_TABLE")
    dynamodb_approvals_table: str = Field(default="finops-approvals", alias="DYNAMODB_APPROVALS_TABLE")
    dynamodb_action_history_table: str = Field(default="finops-action-history", alias="DYNAMODB_ACTION_HISTORY_TABLE")
    dynamodb_kpi_table: str = Field(default="finops-kpi-metrics", alias="DYNAMODB_KPI_TABLE")
    cognito_user_pool_id: str = Field(default="", alias="COGNITO_USER_POOL_ID")
    cognito_client_id: str = Field(default="", alias="COGNITO_CLIENT_ID")
    jira_base_url: str = Field(default="", alias="JIRA_BASE_URL")
    jira_secret_name: str = Field(default="finops/jira-api-token", alias="JIRA_SECRET_NAME")
    jira_project_key: str = Field(default="FINOPS", alias="JIRA_PROJECT_KEY")
    slack_secret_name: str = Field(default="finops/slack-webhook-url", alias="SLACK_SECRET_NAME")
    recommendation_confidence_threshold: float = Field(default=0.70, alias="RECOMMENDATION_CONFIDENCE_THRESHOLD")
    demo_mode: bool = Field(default=False, alias="DEMO_MODE")
    step_functions_arn: str = Field(default="", alias="STEP_FUNCTIONS_ARN")

    model_config = {"populate_by_name": True}

    @property
    def recommendations_table_name(self) -> str:
        """Return the DynamoDB table name for cost recommendations."""
        return self.dynamodb_recommendations_table

    @property
    def approvals_table_name(self) -> str:
        """Return the DynamoDB table name for approval token records."""
        return self.dynamodb_approvals_table

    @property
    def action_history_table_name(self) -> str:
        """Return the DynamoDB table name for completed/failed action audit trail."""
        return self.dynamodb_action_history_table

    @property
    def kpi_table_name(self) -> str:
        """Return the DynamoDB table name for weekly/monthly KPI snapshots."""
        return self.dynamodb_kpi_table

    @property
    def confidence_threshold(self) -> float:
        """Return the minimum confidence score required for auto-routing recommendations."""
        return self.recommendation_confidence_threshold


settings = Settings()
