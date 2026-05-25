import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import init_db

st.set_page_config(page_title="Live Monitor - AI Agent Security", page_icon="📡", layout="wide")
init_db()

# Initialise session state keys so pages work when navigated to directly
for _key, _default in [("agents", {}), ("evaluations", []), ("current_report", None), ("attack_logs", [])]:
    if _key not in st.session_state:
        st.session_state[_key] = _default

st.markdown("## Live Execution Monitor")
st.markdown("Real-time view of attack execution, agent responses, and judge analysis.")
st.markdown("---")

if "attack_logs" not in st.session_state:
    st.session_state.attack_logs = []

if not st.session_state.attack_logs:
    st.info("No active evaluation. Start an evaluation to see live monitoring.")
    if st.button("Start Evaluation"):
        st.switch_page("pages/Run_Evaluation.py")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Attacks Executed", len(st.session_state.attack_logs))
with col2:
    successes = sum(1 for l in st.session_state.attack_logs if l.get("success"))
    st.metric("Successful Attacks", successes)
with col3:
    total_tokens = sum(l.get("tokens", 0) for l in st.session_state.attack_logs)
    st.metric("Tokens Used", f"{total_tokens:,}")

st.markdown("---")
st.markdown("### Attack Trace Log")

for i, log in enumerate(reversed(st.session_state.attack_logs[-20:])):
    status = "🔴 SUCCESS" if log.get("success") else "🟢 BLOCKED"
    with st.expander(f"{status} | {log.get('attack_type', 'unknown')} | {log.get('timestamp', '')}", expanded=(i == 0)):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Attack Prompt:**")
            st.code(log.get("prompt", "")[:300], language="text")
        with col2:
            st.markdown("**Agent Response:**")
            st.code(log.get("response", "")[:300], language="text")

        st.markdown(f"**Latency:** {log.get('latency_ms', 0):.0f}ms | "
                    f"**Tokens:** {log.get('tokens', 0)} | "
                    f"**Risk:** {log.get('risk_level', 'unknown')}")

if st.button("Clear Logs"):
    st.session_state.attack_logs = []
    st.rerun()
