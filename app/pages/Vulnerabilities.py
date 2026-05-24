import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.engine import init_db
from app.database.repository import EvaluationRepository

st.set_page_config(page_title="Vulnerabilities - AI Agent Security", page_icon="🔓", layout="wide")
init_db()

st.markdown("## Vulnerability Database")
st.markdown("All identified vulnerabilities across evaluations.")
st.markdown("---")

eval_repo = EvaluationRepository()
evaluations = eval_repo.list_all()

all_vulns = []
for e in evaluations:
    report = eval_repo.get(e["id"])
    if report:
        for v in report.vulnerabilities:
            all_vulns.append({
                "agent": report.agent_name,
                "title": v.title,
                "risk_level": v.risk_level.value,
                "attack_type": v.attack_type.value,
                "owasp": v.owasp_category.value,
                "description": v.description[:100],
                "recommendation": v.recommendation,
            })

if not all_vulns:
    st.info("No vulnerabilities found yet. Run an evaluation to detect vulnerabilities.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    critical = sum(1 for v in all_vulns if v["risk_level"] == "critical")
    st.metric("Critical", critical)
with col2:
    high = sum(1 for v in all_vulns if v["risk_level"] == "high")
    st.metric("High", high)
with col3:
    medium = sum(1 for v in all_vulns if v["risk_level"] == "medium")
    st.metric("Medium", medium)
with col4:
    low = sum(1 for v in all_vulns if v["risk_level"] == "low")
    st.metric("Low", low)

st.markdown("---")

tab1, tab2 = st.tabs(["Table View", "Analytics"])

with tab1:
    risk_filter = st.multiselect("Filter by Risk Level", ["critical", "high", "medium", "low"], default=["critical", "high", "medium", "low"])
    df = pd.DataFrame(all_vulns)
    filtered = df[df["risk_level"].isin(risk_filter)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab2:
    df = pd.DataFrame(all_vulns)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names="risk_level", title="Vulnerabilities by Risk Level",
                     color="risk_level",
                     color_discrete_map={"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#22C55E"})
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="attack_type", title="Vulnerabilities by Attack Type",
                           color="risk_level",
                           color_discrete_map={"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#22C55E"})
        fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(df, x="owasp", title="OWASP LLM Top 10 Mapping",
                       color="risk_level",
                       color_discrete_map={"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#22C55E"})
    fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
