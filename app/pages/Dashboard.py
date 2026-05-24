import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.engine import init_db
from app.database.repository import EvaluationRepository, AgentRepository

st.set_page_config(page_title="Dashboard - AI Agent Security", page_icon="📊", layout="wide")
init_db()

st.markdown("## Security Dashboard")
st.markdown("---")

eval_repo = EvaluationRepository()
agent_repo = AgentRepository()

evaluations = eval_repo.list_all()
agents = agent_repo.list_all()

if not evaluations:
    st.info("No evaluations yet. Run your first evaluation to see the dashboard.")
    if st.button("Run Evaluation"):
        st.switch_page("app/pages/Run_Evaluation.py")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_score = sum(e["overall_score"] for e in evaluations) / len(evaluations)
    st.metric("Avg Security Score", f"{avg_score:.1f}/100")
with col2:
    total_attacks = sum(e["total_attacks"] for e in evaluations)
    st.metric("Total Attacks Run", f"{total_attacks:,}")
with col3:
    total_vulns = sum(e["successful_attacks"] for e in evaluations)
    st.metric("Total Vulnerabilities", total_vulns)
with col4:
    total_cost = sum(e["total_cost"] for e in evaluations)
    st.metric("Total Cost", f"${total_cost:.4f}")

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Score Trends", "Agent Comparison", "Attack Analysis"])

with tab1:
    if len(evaluations) > 1:
        df = pd.DataFrame(evaluations)
        df["started_at"] = pd.to_datetime(df["started_at"])
        fig = px.line(
            df, x="started_at", y="overall_score",
            color="agent_name", markers=True,
            title="Security Score Over Time",
            labels={"overall_score": "Score", "started_at": "Date"},
        )
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run multiple evaluations to see trends.")

with tab2:
    if agents:
        agent_scores = {}
        for e in evaluations:
            name = e["agent_name"]
            if name not in agent_scores:
                agent_scores[name] = []
            agent_scores[name].append(e["overall_score"])

        avg_by_agent = {k: sum(v) / len(v) for k, v in agent_scores.items()}
        if avg_by_agent:
            fig = go.Figure(go.Bar(
                x=list(avg_by_agent.keys()),
                y=list(avg_by_agent.values()),
                marker_color=["#EF4444" if s < 50 else "#EAB308" if s < 75 else "#22C55E" for s in avg_by_agent.values()],
            ))
            fig.update_layout(
                title="Average Score by Agent",
                template="plotly_dark",
                height=400,
                yaxis_range=[0, 100],
            )
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    if evaluations:
        latest = evaluations[0]
        report = eval_repo.get(latest["id"])
        if report and report.attack_results:
            attack_types = {}
            for r in report.attack_results:
                t = r.attack_type.value
                if t not in attack_types:
                    attack_types[t] = {"total": 0, "success": 0}
                attack_types[t]["total"] += 1
                if r.success:
                    attack_types[t]["success"] += 1

            categories = list(attack_types.keys())
            success_rates = [
                (attack_types[c]["success"] / attack_types[c]["total"]) * 100
                for c in categories
            ]

            fig = go.Figure(go.Bar(
                x=categories,
                y=success_rates,
                marker_color="#FF4B4B",
            ))
            fig.update_layout(
                title="Attack Success Rate by Type (Latest Evaluation)",
                template="plotly_dark",
                height=400,
                yaxis_title="Success Rate (%)",
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Recent Evaluations")
if evaluations:
    df = pd.DataFrame(evaluations[:10])
    display_cols = ["agent_name", "grade", "overall_score", "total_attacks", "successful_attacks", "started_at"]
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
