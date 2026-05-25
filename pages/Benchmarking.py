import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import init_db
from app.database.repository import EvaluationRepository

st.set_page_config(page_title="Benchmarking - AI Agent Security", page_icon="🏆", layout="wide")
init_db()

st.markdown("## Agent Benchmarking")
st.markdown("Compare security postures across multiple agents.")
st.markdown("---")

eval_repo = EvaluationRepository()
evaluations = eval_repo.list_all()

if not evaluations:
    st.info("Run evaluations on multiple agents to see benchmarks.")
    st.stop()

agent_names = list(set(e["agent_name"] for e in evaluations))

if len(agent_names) < 2:
    st.warning("Evaluate at least 2 different agents to use benchmarking.")
    if st.button("Run Evaluation"):
        st.switch_page("pages/Run_Evaluation.py")
    st.stop()

selected_agents = st.multiselect("Select Agents to Compare", agent_names, default=agent_names[:4])

if len(selected_agents) < 2:
    st.warning("Select at least 2 agents.")
    st.stop()

agent_reports = {}
for name in selected_agents:
    agent_evals = [e for e in evaluations if e["agent_name"] == name]
    if agent_evals:
        latest = agent_evals[0]
        report = eval_repo.get(latest["id"])
        if report:
            agent_reports[name] = report

if not agent_reports:
    st.error("No detailed reports available for selected agents.")
    st.stop()

st.markdown("### Comparison Radar")
fig = go.Figure()
for name, report in agent_reports.items():
    fig.add_trace(go.Scatterpolar(
        r=[
            report.score.prompt_injection_resistance,
            report.score.jailbreak_resistance,
            report.score.leakage_prevention,
            report.score.tool_safety,
            report.score.alignment_consistency,
            report.score.hallucination_resistance,
            report.score.robustness,
        ],
        theta=["Prompt Injection", "Jailbreak", "Leakage", "Tool Safety", "Alignment", "Hallucination", "Robustness"],
        fill="toself",
        name=name,
    ))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    template="plotly_dark",
    height=550,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Score Comparison Table")

rows = []
for name, report in agent_reports.items():
    rows.append({
        "Agent": name,
        "Grade": report.score.grade,
        "Overall": f"{report.score.overall:.1f}",
        "PI Resistance": f"{report.score.prompt_injection_resistance:.0f}%",
        "Jailbreak": f"{report.score.jailbreak_resistance:.0f}%",
        "Leakage": f"{report.score.leakage_prevention:.0f}%",
        "Tool Safety": f"{report.score.tool_safety:.0f}%",
        "Alignment": f"{report.score.alignment_consistency:.0f}%",
        "Vulnerabilities": len(report.vulnerabilities),
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### Overall Score Ranking")

fig = go.Figure(go.Bar(
    x=[name for name in agent_reports],
    y=[r.score.overall for r in agent_reports.values()],
    marker_color=[
        "#22C55E" if r.score.overall >= 80
        else "#EAB308" if r.score.overall >= 60
        else "#EF4444"
        for r in agent_reports.values()
    ],
    text=[r.score.grade for r in agent_reports.values()],
    textposition="outside",
))
fig.update_layout(
    title="Overall Security Score by Agent",
    template="plotly_dark",
    height=400,
    yaxis_range=[0, 110],
    yaxis_title="Score",
)
st.plotly_chart(fig, use_container_width=True)
