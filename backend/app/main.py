import json
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .ai_engine import PentestAIAgent, dump_action_params
from .database import Base, engine, get_db
from .execution_engine import ExecutionError, execute_action, validate_action
from .models import Analysis, ExecutionLog, Proposal, Target, Vulnerability
from .scanner import run_light_scan
from .schemas import AnalysisOut, ExecuteRequest, ProposalDecision, TargetCreate
from .ai_engine import PentestAIAgent
from .database import Base, engine, get_db
from .models import Analysis, Proposal, Target, Vulnerability
from .scanner import run_light_scan
from .schemas import AnalysisOut, ProposalDecision, TargetCreate

Base.metadata.create_all(bind=engine)
ai_agent = PentestAIAgent()

app = FastAPI(title="Pentest AI Desktop API", version="0.2.0")
app = FastAPI(title="Pentest AI Desktop API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyses", response_model=AnalysisOut)
def create_analysis(payload: TargetCreate, db: Session = Depends(get_db)) -> AnalysisOut:
    target = Target(hostname=payload.target)
    db.add(target)
    db.flush()

    open_ports, fingerprint = run_light_scan(payload.target)
    risk_score, findings = ai_agent.analyze(open_ports, fingerprint)

    analysis = Analysis(
        target_id=target.id,
        status="completed",
        open_ports=",".join(str(port) for port in open_ports),
        service_fingerprint=fingerprint,
        risk_score=risk_score,
    )
    db.add(analysis)
    db.flush()

    for finding in findings:
        vulnerability = Vulnerability(
            analysis_id=analysis.id,
            name=finding.name,
            severity=finding.severity,
            confidence=finding.confidence,
            description=finding.description,
        )
        db.add(vulnerability)
        db.flush()

        proposal = Proposal(
            vulnerability_id=vulnerability.id,
            title=finding.proposal_title,
            action_plan=finding.proposal_plan,
            action_key=finding.action_key,
            action_params=dump_action_params(finding.action_params),
            approved=None,
        )
        db.add(proposal)

    db.commit()
    db.refresh(analysis)

    return _analysis_to_schema(analysis)


@app.get("/analyses", response_model=list[AnalysisOut])
def list_analyses(db: Session = Depends(get_db)) -> list[AnalysisOut]:
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(50).all()
    return [_analysis_to_schema(a) for a in analyses]


@app.patch("/proposals/{proposal_id}")
def decide_proposal(proposal_id: int, decision: ProposalDecision, db: Session = Depends(get_db)) -> dict[str, str]:
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal.approved = decision.approved
    proposal.approved_by = decision.approved_by
    proposal.approved_at = datetime.utcnow()
    db.commit()
    return {
        "status": "updated",
        "message": "Proposal decision stored. No exploitation is executed automatically.",
    }


@app.post("/execute")
def execute_proposal(payload: ExecuteRequest, db: Session = Depends(get_db)) -> dict:
    proposal = db.query(Proposal).filter(Proposal.id == payload.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.approved is not True:
        raise HTTPException(status_code=403, detail="Proposal must be human-approved before execution")

    params = json.loads(proposal.action_params or "{}")
    if payload.override_params:
        params.update(payload.override_params)

    vuln = proposal.vulnerability
    analysis = vuln.analysis
    target = analysis.target.hostname

    try:
        validate_action(proposal.action_key, params)
    except ExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = execute_action(proposal.action_key, target, params)
    proposal.execution_status = result["status"]
    proposal.execution_result = json.dumps(result.get("result")) if result.get("result") is not None else None
    proposal.execution_error = result.get("error")
    proposal.executed_by = payload.executed_by
    proposal.executed_at = datetime.utcnow()

    exec_log = ExecutionLog(
        proposal_id=proposal.id,
        action_key=proposal.action_key,
        parameters=json.dumps(params),
        status=result["status"],
        output=proposal.execution_result,
        error=proposal.execution_error,
    )
    db.add(exec_log)
    db.commit()

    return {
        "proposal_id": proposal.id,
        "execution_status": proposal.execution_status,
        "execution_result": result,
    }


def _analysis_to_schema(analysis: Analysis) -> AnalysisOut:
    open_ports = [int(p) for p in analysis.open_ports.split(",") if p]
    for vulnerability in analysis.vulnerabilities:
        for proposal in vulnerability.proposals:
            proposal.action_params = json.loads(proposal.action_params or "{}")
def _analysis_to_schema(analysis: Analysis) -> AnalysisOut:
    open_ports = [int(p) for p in analysis.open_ports.split(",") if p]
    return AnalysisOut(
        id=analysis.id,
        target=analysis.target.hostname,
        status=analysis.status,
        open_ports=open_ports,
        service_fingerprint=analysis.service_fingerprint,
        risk_score=analysis.risk_score,
        vulnerabilities=analysis.vulnerabilities,
        created_at=analysis.created_at,
    )
