from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AgentRecord(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    team = Column(String, default="")
    owner = Column(String, default="")
    provider = Column(String, nullable=False)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvaluationRecord(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False)
    agent_name = Column(String, default="")
    status = Column(String, default="pending")
    config_json = Column(JSON, nullable=False)
    report_json = Column(JSON, nullable=True)
    overall_score = Column(Float, default=0.0)
    grade = Column(String, default="F")
    total_attacks = Column(Integer, default=0)
    successful_attacks = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    duration_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class VulnerabilityRecord(Base):
    __tablename__ = "vulnerabilities"

    id = Column(String, primary_key=True)
    evaluation_id = Column(String, nullable=False)
    agent_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    attack_type = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    owasp_category = Column(String, default="")
    evidence = Column(Text, default="")
    recommendation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, default="")
    entity_id = Column(String, default="")
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
