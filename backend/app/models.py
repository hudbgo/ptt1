from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analyses: Mapped[list["Analysis"]] = relationship("Analysis", back_populates="target", cascade="all, delete")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    open_ports: Mapped[str] = mapped_column(String(512), default="")
    service_fingerprint: Mapped[str] = mapped_column(Text, default="")
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    target: Mapped[Target] = relationship("Target", back_populates="analyses")
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        "Vulnerability", back_populates="analysis", cascade="all, delete"
    )


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="vulnerabilities")
    proposals: Mapped[list["Proposal"]] = relationship("Proposal", back_populates="vulnerability", cascade="all, delete")


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vulnerability_id: Mapped[int] = mapped_column(ForeignKey("vulnerabilities.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    action_plan: Mapped[str] = mapped_column(Text)
    action_key: Mapped[str] = mapped_column(String(120), default="dns_resolve")
    action_params: Mapped[str] = mapped_column(Text, default="{}")
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    execution_status: Mapped[str] = mapped_column(String(30), default="not_executed")
    execution_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vulnerability: Mapped[Vulnerability] = relationship("Vulnerability", back_populates="proposals")
    execution_logs: Mapped[list["ExecutionLog"]] = relationship("ExecutionLog", back_populates="proposal", cascade="all, delete")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposals.id"), index=True)
    action_key: Mapped[str] = mapped_column(String(120))
    parameters: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    proposal: Mapped[Proposal] = relationship("Proposal", back_populates="execution_logs")
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vulnerability: Mapped[Vulnerability] = relationship("Vulnerability", back_populates="proposals")
