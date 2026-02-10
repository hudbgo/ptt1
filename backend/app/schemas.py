from datetime import datetime
from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    target: str = Field(min_length=1, max_length=255)


class ProposalDecision(BaseModel):
    approved: bool


class ProposalOut(BaseModel):
    id: int
    title: str
    action_plan: str
    approved: bool | None

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
