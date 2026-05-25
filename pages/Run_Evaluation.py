import asyncio
import streamlit as st
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.enums import AttackType, Provider, VulnerabilityLevel
from app.core.models import AgentConfig, AttackResult, EvaluationConfig, JudgeVerdict
from app.database.engine import init_db
from app.database.repository import AgentRepository, AuditRepository, EvaluationRepository
from app.dummy_agents.registry import list_dummy_agents
from app.evaluators.pipeline import EvaluationPipeline
from app.utils.observability import get_metrics

st.set_page_config(page_title="Run Evaluation - AI Agent Security", page_icon="⚔️", layout="wide")
init_db()

# Initialise session state keys so pages work when navigated to directly
for _key, _default in [("agents", {}), ("evaluations", []), ("current_report", None), ("attack_logs", [])]:
    if _key not in st.session_state:
        st.session_state[_key] = _default

agent_repo = AgentRepository()
eval_repo = EvaluationRepository()
audit_repo = AuditRepository()

st.markdown("## Run Security Evaluation")
st.markdown("Execute adversarial attacks against registered agents.")
st.markdown("---")

all_agents = agent_repo.list_all()
demo_mode = len(all_agents) == 0

if demo_mode:
    st.warning("No agents registered. Using demo mode with built-in agents.")
    agent_options = list_dummy_agents()
else:
    agent_options = [f"{a.name} ({a.id[:8]})" for a in all_agents]

col1, col2 = st.columns([2, 1])

with col1:
    if demo_mode:
        selected_agent_name = st.selectbox("Select Dummy Agent", agent_options)
        vuln_level = st.select_slider(
            "Vulnerability Level",
            options=[v.value for v in VulnerabilityLevel],
            value="medium",
        )
    else:
        selected_idx = st.selectbox("Select Agent", range(len(agent_options)), format_func=lambda i: agent_options[i])

with col2:
    st.markdown("#### Attack Configuration")
    max_attacks = st.slider("Attacks per Category", 1, 10, 3)
    use_judge = st.checkbox("Use LLM Judge", value=False, help="Requires API key for enhanced evaluation")

st.markdown("#### Select Attack Types")
attack_cols = st.columns(3)
selected_attacks = []
for i, attack_type in enumerate(AttackType):
    with attack_cols[i % 3]:
        if st.checkbox(attack_type.value.replace("_", " ").title(), value=True, key=f"atk_{attack_type.value}"):
            selected_attacks.append(attack_type)

st.markdown("---")

if st.button("Start Evaluation", type="primary", use_container_width=True):
    if not selected_attacks:
        st.error("Select at least one attack type.")
        st.stop()

    if demo_mode:
        agent_config = AgentConfig(
            name=selected_agent_name,
            provider=Provider.DUMMY,
            model="dummy",
            vulnerability_level=VulnerabilityLevel(vuln_level),
        )
    else:
        agent_config = all_agents[selected_idx]

    eval_config = EvaluationConfig(
        agent_id=agent_config.id,
        attack_types=selected_attacks,
        max_attacks_per_type=max_attacks,
        use_judge=use_judge,
    )

    pipeline = EvaluationPipeline(agent_config, eval_config)
    metrics = get_metrics()

    st.markdown("### Evaluation Progress")
    progress_bar = st.progress(0)

    total_expected = len(selected_attacks) * max_attacks
    progress_state = {"completed": 0}
    results_list: list = []

    async def run_evaluation():
        def on_progress(result: AttackResult, verdict: JudgeVerdict):
            progress_state["completed"] += 1
            results_list.append(result)
            metrics.record_request(
                tokens=result.tokens_used,
                cost=result.cost_estimate,
                latency_ms=result.latency_ms,
                success=result.success,
            )

        return await pipeline.run(progress_callback=on_progress)

    with st.spinner("Running adversarial evaluation..."):
        start_time = time.time()

        report = asyncio.run(run_evaluation())

        elapsed = time.time() - start_time
        progress_bar.progress(1.0)

    st.success(f"Evaluation completed in {elapsed:.1f}s!")

    eval_repo.save(report)
    st.session_state.evaluations.append(report.model_dump())
    st.session_state.current_report = report
    audit_repo.log("evaluation_completed", "evaluation", report.id, {
        "agent": agent_config.name,
        "score": report.score.overall,
        "grade": report.score.grade,
    })

    st.markdown("---")
    st.markdown("### Results Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Security Grade", report.score.grade)
    with col2:
        st.metric("Overall Score", f"{report.score.overall:.1f}/100")
    with col3:
        st.metric("Attacks Successful", f"{report.successful_attacks}/{report.total_attacks}")
    with col4:
        st.metric("Duration", f"{report.duration_seconds:.1f}s")

    st.markdown("---")
    st.markdown("### Score Breakdown")
    score_cols = st.columns(3)
    with score_cols[0]:
        st.metric("Prompt Injection Resistance", f"{report.score.prompt_injection_resistance:.0f}%")
        st.metric("Jailbreak Resistance", f"{report.score.jailbreak_resistance:.0f}%")
    with score_cols[1]:
        st.metric("Leakage Prevention", f"{report.score.leakage_prevention:.0f}%")
        st.metric("Tool Safety", f"{report.score.tool_safety:.0f}%")
    with score_cols[2]:
        st.metric("Alignment", f"{report.score.alignment_consistency:.0f}%")
        st.metric("Hallucination Resistance", f"{report.score.hallucination_resistance:.0f}%")

    if report.vulnerabilities:
        st.markdown("---")
        st.markdown(f"### Vulnerabilities ({len(report.vulnerabilities)})")
        for vuln in report.vulnerabilities[:10]:
            risk_colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "informational": "⚪"}
            icon = risk_colors.get(vuln.risk_level.value, "⚪")
            with st.expander(f"{icon} [{vuln.risk_level.value.upper()}] {vuln.title}"):
                st.markdown(f"**OWASP:** {vuln.owasp_category.value}")
                st.markdown(f"**Description:** {vuln.description}")
                st.markdown(f"**Recommendation:** {vuln.recommendation}")
                st.markdown("**Attack Prompt:**")
                st.code(vuln.attack_prompt[:500], language="text")
                st.markdown("**Agent Response:**")
                st.code(vuln.agent_response[:500], language="text")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Full Report"):
            st.switch_page("pages/Reports.py")
    with col2:
        if st.button("Run Another Evaluation"):
            st.rerun()
