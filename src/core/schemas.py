from pydantic import BaseModel, Field

class ProvisioningResult(BaseModel):
    resource_type: str = Field(description="The type of infrastructure resource requested (e.g., PostgreSQL Database, Cisco IOS Switch, EC2, S3).")
    requested_permissions: str = Field(description="The raw permissions or access level the user requested.")
    approved_permissions: str = Field(description="The explicitly approved permissions based on the Principle of Least Privilege and local standards.")
    suggested_config: str = Field(description="Syntactically correct code snippet for fulfillment (e.g., PostgreSQL GRANT statements or Cisco IOS commands). Must be only the code.")
    risk_level: int = Field(description="Risk assessment score from 1 to 10, where 10 is the highest risk (e.g., 0.0.0.0/0, wildcard ALL privileges).")
    confidence_score: int = Field(description="Self-assessed certainty of the response accuracy and security posture, scored from 1 to 100.")
    action_taken: str = Field(description="Action taken on the request. Examples: 'Approved', 'Downgraded', 'BLOCKED'.")
    reasoning: str = Field(description="Detailed explanation of the security assessment, citing policies, constraints, or misconfigurations.")
