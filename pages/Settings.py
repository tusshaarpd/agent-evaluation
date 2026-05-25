import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.configs.settings import get_settings, is_demo_mode
from app.database.engine import init_db
from app.database.repository import AuditRepository

st.set_page_config(page_title="Settings - AI Agent Security", page_icon="⚙️", layout="wide")
init_db()

st.markdown("## Platform Settings")
st.markdown("Configure API connections, preferences, and platform options.")
st.markdown("---")

settings = get_settings()
audit_repo = AuditRepository()

tab1, tab2, tab3 = st.tabs(["API Configuration", "Platform", "Audit Log"])

with tab1:
    st.markdown("### API Keys")
    st.caption("API keys are loaded from Streamlit secrets or environment variables. Configure them in your deployment settings.")

    with st.form("api_settings"):
        openai_key = st.text_input(
            "OpenAI API Key",
            value="•" * 8 + settings["openai_api_key"][-4:] if settings["openai_api_key"] else "",
            type="password",
            help="Used for LLM Judge and OpenAI agents",
        )
        openai_base = st.text_input("OpenAI Base URL", value=settings["openai_base_url"])

        st.markdown("#### Additional Providers")
        col1, col2 = st.columns(2)
        with col1:
            groq_key = st.text_input("Groq API Key", type="password",
                                     value="•" * 8 if settings["groq_api_key"] else "")
            together_key = st.text_input("Together AI Key", type="password",
                                        value="•" * 8 if settings["together_api_key"] else "")
        with col2:
            azure_key = st.text_input("Azure OpenAI Key", type="password",
                                      value="•" * 8 if settings["azure_api_key"] else "")
            openrouter_key = st.text_input("OpenRouter Key", type="password",
                                          value="•" * 8 if settings["openrouter_api_key"] else "")

        submitted = st.form_submit_button("Save Configuration", use_container_width=True)
        if submitted:
            st.info("API keys should be configured via Streamlit secrets (`.streamlit/secrets.toml`) or environment variables for security.")

with tab2:
    st.markdown("### Platform Configuration")

    demo_mode = st.toggle("Demo Mode", value=is_demo_mode(), help="Use dummy agents without API keys")
    st.caption("Demo mode allows full platform testing without external API dependencies.")

    st.markdown("### Database")
    st.code(settings["database_url"], language="text")
    st.caption("Default: SQLite stored in /tmp. Configure DATABASE_URL for PostgreSQL in production.")

    st.markdown("### System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Platform:** AI Agent Security Platform v1.0")
        st.markdown("**Python:** 3.11+")
        st.markdown("**Framework:** Streamlit")
    with col2:
        st.markdown("**Database:** SQLite / PostgreSQL")
        st.markdown("**Deployment:** Streamlit Cloud")
        st.markdown("**License:** Enterprise")

with tab3:
    st.markdown("### Audit Log")
    logs = audit_repo.get_recent(limit=50)
    if logs:
        for log in logs:
            st.markdown(f"**{log['timestamp']}** | `{log['action']}` | {log['entity_type']} | {log.get('entity_id', '')[:8]}")
    else:
        st.info("No audit events recorded yet.")
