from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from app.core.models import AgentConfig, EvaluationReport
from app.database.engine import get_session
from app.database.models import AgentRecord, AuditLog, EvaluationRecord, VulnerabilityRecord


class AgentRepository:
    def save(self, config: AgentConfig) -> None:
        with get_session() as session:
            existing = session.get(AgentRecord, config.id)
            if existing:
                existing.name = config.name
                existing.description = config.description
                existing.team = config.team
                existing.owner = config.owner
                existing.provider = config.provider.value
                existing.config_json = config.model_dump()
                existing.updated_at = datetime.utcnow()
            else:
                record = AgentRecord(
                    id=config.id,
                    name=config.name,
                    description=config.description,
                    team=config.team,
                    owner=config.owner,
                    provider=config.provider.value,
                    config_json=config.model_dump(),
                )
                session.add(record)
            session.commit()

    def get(self, agent_id: str) -> Optional[AgentConfig]:
        with get_session() as session:
            record = session.get(AgentRecord, agent_id)
            if record:
                return AgentConfig(**record.config_json)
            return None

    def list_all(self) -> list[AgentConfig]:
        with get_session() as session:
            records = session.query(AgentRecord).order_by(AgentRecord.created_at.desc()).all()
            return [AgentConfig(**r.config_json) for r in records]

    def delete(self, agent_id: str) -> bool:
        with get_session() as session:
            record = session.get(AgentRecord, agent_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False


class EvaluationRepository:
    def save(self, report: EvaluationReport) -> None:
        with get_session() as session:
            existing = session.get(EvaluationRecord, report.id)
            if existing:
                existing.report_json = report.model_dump()
                existing.overall_score = report.score.overall
                existing.grade = report.score.grade
                existing.total_attacks = report.total_attacks
                existing.successful_attacks = report.successful_attacks
                existing.total_tokens = report.total_tokens
                existing.total_cost = report.total_cost
                existing.duration_seconds = report.duration_seconds
                existing.status = "completed"
                existing.completed_at = datetime.utcnow()
            else:
                record = EvaluationRecord(
                    id=report.id,
                    agent_id=report.agent_id,
                    agent_name=report.agent_name,
                    status="completed",
                    config_json={},
                    report_json=report.model_dump(),
                    overall_score=report.score.overall,
                    grade=report.score.grade,
                    total_attacks=report.total_attacks,
                    successful_attacks=report.successful_attacks,
                    total_tokens=report.total_tokens,
                    total_cost=report.total_cost,
                    duration_seconds=report.duration_seconds,
                    completed_at=datetime.utcnow(),
                )
                session.add(record)

            for vuln in report.vulnerabilities:
                vuln_record = VulnerabilityRecord(
                    id=vuln.id,
                    evaluation_id=report.evaluation_id,
                    agent_id=report.agent_id,
                    title=vuln.title,
                    description=vuln.description,
                    attack_type=vuln.attack_type.value,
                    risk_level=vuln.risk_level.value,
                    owasp_category=vuln.owasp_category.value,
                    evidence=vuln.evidence,
                    recommendation=vuln.recommendation,
                )
                session.merge(vuln_record)

            session.commit()

    def get(self, evaluation_id: str) -> Optional[EvaluationReport]:
        with get_session() as session:
            record = session.get(EvaluationRecord, evaluation_id)
            if record and record.report_json:
                return EvaluationReport(**record.report_json)
            return None

    def list_all(self) -> list[dict]:
        with get_session() as session:
            records = session.query(EvaluationRecord).order_by(EvaluationRecord.started_at.desc()).all()
            return [
                {
                    "id": r.id,
                    "agent_id": r.agent_id,
                    "agent_name": r.agent_name,
                    "status": r.status,
                    "overall_score": r.overall_score,
                    "grade": r.grade,
                    "total_attacks": r.total_attacks,
                    "successful_attacks": r.successful_attacks,
                    "duration_seconds": r.duration_seconds,
                    "total_cost": r.total_cost,
                    "started_at": r.started_at.isoformat() if r.started_at else "",
                }
                for r in records
            ]

    def list_by_agent(self, agent_id: str) -> list[dict]:
        with get_session() as session:
            records = (
                session.query(EvaluationRecord)
                .filter(EvaluationRecord.agent_id == agent_id)
                .order_by(EvaluationRecord.started_at.desc())
                .all()
            )
            return [
                {
                    "id": r.id,
                    "overall_score": r.overall_score,
                    "grade": r.grade,
                    "total_attacks": r.total_attacks,
                    "successful_attacks": r.successful_attacks,
                    "started_at": r.started_at.isoformat() if r.started_at else "",
                }
                for r in records
            ]


class AuditRepository:
    def log(self, action: str, entity_type: str = "", entity_id: str = "", details: dict = None) -> None:
        with get_session() as session:
            record = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details or {},
            )
            session.add(record)
            session.commit()

    def get_recent(self, limit: int = 50) -> list[dict]:
        with get_session() as session:
            records = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return [
                {
                    "action": r.action,
                    "entity_type": r.entity_type,
                    "entity_id": r.entity_id,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                }
                for r in records
            ]
