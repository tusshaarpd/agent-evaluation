import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.engine import init_db

st.set_page_config(
    page_title="AI Agent Security Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "agents" not in st.session_state:
    st.session_state.agents = {}
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "attack_logs" not in st.session_state:
    st.session_state.attack_logs = []

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8C42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #9CA3AF;
        margin-top: 0;
    }
    .metric-card {
        background: #1F2937;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #374151;
    }
    .risk-critical { color: #EF4444; font-weight: 700; }
    .risk-high { color: #F97316; font-weight: 700; }
    .risk-medium { color: #EAB308; font-weight: 700; }
    .risk-low { color: #22C55E; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">AI Agent Security Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enterprise AI Red Teaming, Hallucination Detection & Governance</p>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Registered Agents", len(st.session_state.agents))
with col2:
    st.metric("Evaluations Run", len(st.session_state.evaluations))
with col3:
    total_vulns = sum(
        len(e.get("vulnerabilities", [])) for e in st.session_state.evaluations
    )
    st.metric("Vulnerabilities Found", total_vulns)
with col4:
    st.metric("Platform Status", "Active", delta="Online")

st.markdown("---")

st.markdown("### Quick Start")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 1. Register Agent
    Connect your AI agent via OpenAI-compatible API or use built-in dummy agents for testing.
    """)
    if st.button("Register Agent", key="home_register", use_container_width=True):
        st.switch_page("app/pages/Register_Agent.py")

with col2:
    st.markdown("""
    #### 2. Run Evaluation
    Execute adversarial attacks including jailbreaks, prompt injection, and hallucination tests.
    """)
    if st.button("Run Evaluation", key="home_eval", use_container_width=True):
        st.switch_page("app/pages/Run_Evaluation.py")

with col3:
    st.markdown("""
    #### 3. View Reports
    Analyze security scores, vulnerability findings, and download enterprise reports.
    """)
    if st.button("View Reports", key="home_reports", use_container_width=True):
        st.switch_page("app/pages/Reports.py")

st.markdown("---")

st.markdown("### Demo Mode")
st.info(
    "Demo mode is enabled by default. All evaluations use built-in dummy agents — no API keys required. "
    "Configure real API keys in Settings to evaluate production agents."
)

if st.button("Run Demo Evaluation", type="primary", use_container_width=True):
    st.switch_page("app/pages/Run_Evaluation.py")

st.markdown("---")
st.markdown("### Platform Capabilities")

capabilities = {
    "Adversarial Testing": "12+ attack categories including jailbreaks, prompt injection, and social engineering",
    "Hallucination Detection": "Detect fabricated information, false citations, and confabulation",
    "Data Leakage Testing": "Identify PII exposure, credential leaks, and information disclosure",
    "RAG Security": "Test context poisoning, document injection, and retrieval manipulation",
    "Tool Safety": "Evaluate unsafe code generation, command injection, and excessive agency",
    "OWASP LLM Mapping": "All findings mapped to OWASP Top 10 for LLMs",
    "Real-time Monitoring": "Live attack execution with streaming logs and trace replay",
    "Enterprise Reports": "Downloadable PDF, CSV, and JSON reports with executive summaries",
}

cols = st.columns(2)
for i, (title, desc) in enumerate(capabilities.items()):
    with cols[i % 2]:
        st.markdown(f"**{title}**")
        st.caption(desc)

st.markdown("---")
st.caption("AI Agent Security Platform v1.0 | Enterprise AI Governance & Red Teaming")
