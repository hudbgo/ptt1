import json
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import Analysis, ExecutionLog, Proposal, Target, Vulnerability


client = TestClient(app)


def reset_db():
    db = SessionLocal()
    db.query(ExecutionLog).delete()
    db.query(Proposal).delete()
    db.query(Vulnerability).delete()
    db.query(Analysis).delete()
    db.query(Target).delete()
    db.commit()
    db.close()


def make_proposal(approved: bool | None, action_key: str = "dns_resolve", action_params: dict | None = None) -> int:
    db = SessionLocal()
    t = Target(hostname="localhost")
    db.add(t)
    db.flush()
    a = Analysis(target_id=t.id, status="completed", open_ports="80", service_fingerprint="HTTP:80", risk_score=10)
    db.add(a)
    db.flush()
    v = Vulnerability(analysis_id=a.id, name="x", severity="low", confidence=0.5, description="d")
    db.add(v)
    db.flush()
    p = Proposal(
        vulnerability_id=v.id,
        title="safe",
        action_plan="plan",
        action_key=action_key,
        action_params=json.dumps(action_params or {}),
        approved=approved,
        approved_by="tester" if approved else None,
    )
    db.add(p)
    db.commit()
    pid = p.id
    db.close()
    return pid


def test_unapproved_action_is_blocked():
    reset_db()
    proposal_id = make_proposal(approved=False)
    resp = client.post("/execute", json={"proposal_id": proposal_id, "executed_by": "tester"})
    assert resp.status_code == 403


def test_approved_action_executes_and_logs():
    reset_db()
    proposal_id = make_proposal(approved=True, action_key="dns_resolve", action_params={})
    resp = client.post("/execute", json={"proposal_id": proposal_id, "executed_by": "tester"})
    assert resp.status_code == 200
    assert resp.json()["execution_status"] in {"success", "error"}

    db = SessionLocal()
    logs = db.query(ExecutionLog).filter(ExecutionLog.proposal_id == proposal_id).all()
    assert len(logs) == 1
    db.close()


def test_invalid_parameters_fail_validation():
    reset_db()
    proposal_id = make_proposal(approved=True, action_key="tcp_connectivity_check", action_params={"ports": [99999]})
    resp = client.post("/execute", json={"proposal_id": proposal_id, "executed_by": "tester"})
    assert resp.status_code == 400
