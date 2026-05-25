import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import init_db
from app.database.repository import EvaluationRepository
from app.utils.observability import get_metrics

st.set_page_config(page_title="Analytics - AI Agent Security", page_icon="📈", layout="wide")
init_db()

st.markdown("## Analytics & Observability")
st.markdown("Track costs, performance, and attack trends.")
st.markdown("---")

eval_repo = EvaluationRepository()
evaluations = eval_repo.list_all()
metrics = get_metrics()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Evaluations", len(evaluations))
with col2:
    total_tokens = sum(e.get("total_tokens", 0) for e in evaluations) if evaluations else metrics.total_tokens
    st.metric("Total Tokens", f"{total_tokens:,}")
with col3:
    total_cost = sum(e.get("total_cost", 0) for e in evaluations) if evaluations else metrics.total_cost
    st.metric("Total Cost", f"${total_cost:.4f}")
with col4:
    avg_duration = (sum(e.get("duration_seconds", 0) for e in evaluations) / len(evaluations)) if evaluations else 0
    st.metric("Avg Duration", f"{avg_duration:.1f}s")

if not evaluations:
    st.info("Run evaluations to see analytics.")
    st.stop()

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Cost Analysis", "Performance", "Trends"])

with tab1:
    df = pd.DataFrame(evaluations)
    if "total_cost" in df.columns and "started_at" in df.columns:
        df["started_at"] = pd.to_datetime(df["started_at"])
        df["cumulative_cost"] = df["total_cost"].cumsum()

        fig = px.area(df, x="started_at", y="cumulative_cost",
                      title="Cumulative Cost Over Time",
                      labels={"cumulative_cost": "Cost ($)", "started_at": "Date"})
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(df, x="agent_name", y="total_cost", title="Cost by Agent",
                      color="agent_name")
        fig2.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    df = pd.DataFrame(evaluations)
    if "duration_seconds" in df.columns:
        fig = px.box(df, x="agent_name", y="duration_seconds",
                     title="Evaluation Duration by Agent",
                     labels={"duration_seconds": "Duration (s)"})
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    if "total_attacks" in df.columns and "successful_attacks" in df.columns:
        df["success_rate"] = df["successful_attacks"] / df["total_attacks"].replace(0, 1) * 100
        fig = px.bar(df, x="agent_name", y="success_rate",
                     title="Attack Success Rate by Agent (%)",
                     color="success_rate",
                     color_continuous_scale=["green", "yellow", "red"])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    df = pd.DataFrame(evaluations)
    if len(df) > 1 and "overall_score" in df.columns:
        df["started_at"] = pd.to_datetime(df["started_at"])
        fig = px.scatter(df, x="started_at", y="overall_score",
                         color="agent_name", size="total_attacks",
                         title="Score Trends Over Time",
                         labels={"overall_score": "Security Score"})
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
