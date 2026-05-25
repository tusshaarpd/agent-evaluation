import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.models import EvaluationReport
from app.database.engine import init_db
from app.database.repository import EvaluationRepository
from app.utils.reporting import generate_csv_report, generate_json_report, generate_pdf_report

st.set_page_config(page_title="Reports - AI Agent Security", page_icon="📄", layout="wide")
init_db()

# Initialise session state keys so pages work when navigated to directly
for _key, _default in [("agents", {}), ("evaluations", []), ("current_report", None), ("attack_logs", [])]:
    if _key not in st.session_state:
        st.session_state[_key] = _default

st.markdown("## Evaluation Reports")
st.markdown("Download and review detailed security evaluation reports.")
st.markdown("---")

eval_repo = EvaluationRepository()
evaluations = eval_repo.list_all()

if not evaluations:
    st.info("No evaluations available. Run an evaluation first.")
    if st.button("Run Evaluation"):
        st.switch_page("pages/Run_Evaluation.py")
    st.stop()

selected_eval = st.selectbox(
    "Select Evaluation",
    range(len(evaluations)),
    format_func=lambda i: f"{evaluations[i]['agent_name']} | Grade: {evaluations[i]['grade']} | Score: {evaluations[i]['overall_score']:.1f} | {evaluations[i]['started_at'][:16]}",
)

report = eval_repo.get(evaluations[selected_eval]["id"])

if not report:
    st.error("Report data not found.")
    st.stop()

st.markdown("---")
st.markdown(f"### Report: {report.agent_name}")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Grade", report.score.grade)
with col2:
    st.metric("Score", f"{report.score.overall:.1f}")
with col3:
    st.metric("Risk Level", report.score.risk_level.value.upper())
with col4:
    st.metric("Attacks", f"{report.successful_attacks}/{report.total_attacks}")
with col5:
    st.metric("Duration", f"{report.duration_seconds:.1f}s")

st.markdown("---")

fig = go.Figure(data=go.Scatterpolar(
    r=[
        report.score.prompt_injection_resistance,
        report.score.jailbreak_resistance,
        report.score.leakage_prevention,
        report.score.tool_safety,
        report.score.alignment_consistency,
        report.score.hallucination_resistance,
        report.score.robustness,
    ],
    theta=[
        "Prompt Injection",
        "Jailbreak",
        "Leakage Prevention",
        "Tool Safety",
        "Alignment",
        "Hallucination",
        "Robustness",
    ],
    fill="toself",
    line_color="#FF4B4B",
    fillcolor="rgba(255, 75, 75, 0.2)",
))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    title="Security Score Radar",
    template="plotly_dark",
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Download Reports")

col1, col2, col3 = st.columns(3)
with col1:
    try:
        pdf_data = generate_pdf_report(report)
        st.download_button(
            "Download PDF Report",
            data=pdf_data,
            file_name=f"security_report_{report.agent_name}_{report.started_at[:10]}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"PDF generation error: {str(e)[:100]}")

with col2:
    csv_data = generate_csv_report(report)
    st.download_button(
        "Download CSV Report",
        data=csv_data,
        file_name=f"security_report_{report.agent_name}_{report.started_at[:10]}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col3:
    json_data = generate_json_report(report)
    st.download_button(
        "Download JSON Report",
        data=json_data,
        file_name=f"security_report_{report.agent_name}_{report.started_at[:10]}.json",
        mime="application/json",
        use_container_width=True,
    )

st.markdown("---")
st.markdown("### Attack Results Detail")

if report.attack_results:
    for i, result in enumerate(report.attack_results):
        status = "🔴" if result.success else "🟢"
        with st.expander(f"{status} {result.attack_type.value} | Risk: {result.risk_level.value}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Attack Prompt:**")
                st.code(result.attack_prompt[:500], language="text")
            with col2:
                st.markdown("**Agent Response:**")
                st.code(result.agent_response[:500], language="text")
            st.caption(f"Latency: {result.latency_ms:.0f}ms | Tokens: {result.tokens_used} | OWASP: {result.owasp_category.value}")
