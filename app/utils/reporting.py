from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.models import EvaluationReport


def generate_pdf_report(report: EvaluationReport) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=20, spaceAfter=20)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=14, spaceAfter=10)
    body_style = styles["Normal"]

    elements.append(Paragraph("AI Agent Security Evaluation Report", title_style))
    elements.append(Paragraph(f"Agent: {report.agent_name}", body_style))
    elements.append(Paragraph(f"Date: {report.started_at[:10]}", body_style))
    elements.append(Paragraph(f"Overall Grade: {report.score.grade} ({report.score.overall:.1f}/100)", body_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Executive Summary", heading_style))
    summary = (
        f"This evaluation tested {report.total_attacks} attack scenarios against the agent. "
        f"{report.successful_attacks} attacks were successful ({_pct(report.successful_attacks, report.total_attacks)}%). "
        f"Overall security score: {report.score.overall:.1f}/100 (Grade: {report.score.grade}). "
        f"Risk level: {report.score.risk_level.value.upper()}."
    )
    elements.append(Paragraph(summary, body_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Security Scores", heading_style))
    score_data = [
        ["Category", "Score"],
        ["Prompt Injection Resistance", f"{report.score.prompt_injection_resistance:.1f}%"],
        ["Jailbreak Resistance", f"{report.score.jailbreak_resistance:.1f}%"],
        ["Leakage Prevention", f"{report.score.leakage_prevention:.1f}%"],
        ["Tool Safety", f"{report.score.tool_safety:.1f}%"],
        ["Alignment Consistency", f"{report.score.alignment_consistency:.1f}%"],
        ["Hallucination Resistance", f"{report.score.hallucination_resistance:.1f}%"],
    ]
    table = Table(score_data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    if report.vulnerabilities:
        elements.append(Paragraph("Vulnerabilities Found", heading_style))
        for i, vuln in enumerate(report.vulnerabilities[:20], 1):
            elements.append(Paragraph(
                f"<b>{i}. [{vuln.risk_level.value.upper()}] {vuln.title}</b>",
                body_style,
            ))
            elements.append(Paragraph(f"   OWASP: {vuln.owasp_category.value}", body_style))
            elements.append(Paragraph(f"   {vuln.description[:200]}", body_style))
            elements.append(Paragraph(f"   Recommendation: {vuln.recommendation}", body_style))
            elements.append(Spacer(1, 8))

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Metadata", heading_style))
    elements.append(Paragraph(f"Total Tokens: {report.total_tokens:,}", body_style))
    elements.append(Paragraph(f"Estimated Cost: ${report.total_cost:.4f}", body_style))
    elements.append(Paragraph(f"Duration: {report.duration_seconds:.1f}s", body_style))

    doc.build(elements)
    return buffer.getvalue()


def generate_csv_report(report: EvaluationReport) -> str:
    rows = []
    for r in report.attack_results:
        rows.append({
            "attack_type": r.attack_type.value,
            "attack_prompt": r.attack_prompt[:200],
            "agent_response": r.agent_response[:200],
            "success": r.success,
            "risk_level": r.risk_level.value,
            "owasp_category": r.owasp_category.value,
            "latency_ms": r.latency_ms,
            "tokens_used": r.tokens_used,
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def generate_json_report(report: EvaluationReport) -> str:
    return report.model_dump_json(indent=2)


def _pct(part: int, total: int) -> str:
    if total == 0:
        return "0"
    return f"{(part / total) * 100:.1f}"
