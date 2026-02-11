from datetime import datetime
from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    target: str = Field(min_length=1, max_length=255)


class ProposalDecision(BaseModel):
    approved: bool
    approved_by: str = Field(min_length=1, max_length=120)


class ExecuteRequest(BaseModel):
    proposal_id: int
    executed_by: str = Field(min_length=1, max_length=120)
    override_params: dict | None = None


class ProposalOut(BaseModel):
    id: int
    title: str
    action_plan: str
    action_key: str
    action_params: dict
    approved: bool | None
    approved_by: str | None
    approved_at: datetime | None
    execution_status: str
    execution_result: str | None
    execution_error: str | None
    executed_by: str | None
    executed_at: datetime | None

    class Config:
        from_attributes = True


class VulnerabilityOut(BaseModel):
    id: int
    name: str
    severity: str
    confidence: float
    description: str
    proposals: list[ProposalOut]

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    id: int
    target: str
    status: str
    open_ports: list[int]
    service_fingerprint: str
    risk_score: float
    vulnerabilities: list[VulnerabilityOut]
    created_at: datetime
