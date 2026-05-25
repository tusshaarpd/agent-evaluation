import asyncio
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.enums import Provider, VulnerabilityLevel
from app.core.models import AgentConfig
from app.database.engine import init_db
from app.database.repository import AgentRepository, AuditRepository
from app.dummy_agents.registry import list_dummy_agents
from app.services.adapter import get_adapter

st.set_page_config(page_title="Register Agent - AI Agent Security", page_icon="🤖", layout="wide")
init_db()

agent_repo = AgentRepository()
audit_repo = AuditRepository()

st.markdown("## Register AI Agent")
st.markdown("Connect your AI agent or select a built-in dummy agent for testing.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Register New Agent", "Dummy Agents (Demo)", "Manage Agents"])

with tab1:
    with st.form("register_agent"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Agent Name*", placeholder="My Production Agent")
            description = st.text_area("Description", placeholder="What does this agent do?")
            team = st.text_input("Team", placeholder="Platform Engineering")
            owner = st.text_input("Owner", placeholder="team@company.com")

        with col2:
            provider = st.selectbox("Provider*", options=[p.value for p in Provider if p != Provider.DUMMY])
            base_url = st.text_input("Base URL", value="https://api.openai.com/v1")
            api_key = st.text_input("API Key", type="password")
            model = st.text_input("Model", value="gpt-4o-mini")

        st.markdown("#### Advanced Settings")
        col3, col4, col5 = st.columns(3)
        with col3:
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.number_input("Max Tokens", 64, 4096, 1024)
        with col4:
            timeout = st.number_input("Timeout (seconds)", 5, 120, 30)
            retry_count = st.number_input("Retry Count", 0, 5, 3)
        with col5:
            rag_enabled = st.checkbox("RAG Enabled")
            tool_usage = st.checkbox("Tool Usage Enabled")
            memory_enabled = st.checkbox("Memory Enabled")
            internet_enabled = st.checkbox("Internet Access")

        submitted = st.form_submit_button("Register Agent", type="primary", use_container_width=True)

        if submitted:
            if not name:
                st.error("Agent name is required.")
            else:
                config = AgentConfig(
                    name=name,
                    description=description,
                    team=team,
                    owner=owner,
                    provider=Provider(provider),
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    retry_count=retry_count,
                    rag_enabled=rag_enabled,
                    tool_usage_enabled=tool_usage,
                    memory_enabled=memory_enabled,
                    internet_enabled=internet_enabled,
                )
                agent_repo.save(config)
                st.session_state.agents[config.id] = config
                audit_repo.log("agent_registered", "agent", config.id, {"name": name, "provider": provider})
                st.success(f"Agent '{name}' registered successfully!")

with tab2:
    st.markdown("### Built-in Dummy Agents")
    st.info("These agents work offline with no API keys. Ideal for demos and testing.")

    dummy_names = list_dummy_agents()
    vuln_level = st.select_slider(
        "Vulnerability Level",
        options=[v.value for v in VulnerabilityLevel],
        value=VulnerabilityLevel.MEDIUM.value,
    )

    cols = st.columns(2)
    for i, agent_name in enumerate(dummy_names):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{agent_name}**")
                descriptions = {
                    "Safe Banking Agent": "Rejects jailbreaks, protects data, maintains compliance",
                    "Vulnerable Banking Agent": "Leaks data, hallucinates, easily manipulated",
                    "RAG Assistant": "Mock retrieval, vulnerable to context poisoning",
                    "Coding Agent": "Generates code, vulnerable to shell injection",
                    "Customer Support Agent": "Multi-turn memory, emotionally manipulatable",
                    "Secure Enterprise Assistant": "Strong alignment and policy enforcement",
                }
                st.caption(descriptions.get(agent_name, ""))
                if st.button(f"Register", key=f"reg_{agent_name}"):
                    config = AgentConfig(
                        name=agent_name,
                        description=descriptions.get(agent_name, ""),
                        provider=Provider.DUMMY,
                        model="dummy",
                        vulnerability_level=VulnerabilityLevel(vuln_level),
                    )
                    agent_repo.save(config)
                    st.session_state.agents[config.id] = config
                    audit_repo.log("dummy_agent_registered", "agent", config.id, {"name": agent_name})
                    st.success(f"'{agent_name}' registered!")
                    st.rerun()

with tab3:
    st.markdown("### Registered Agents")
    all_agents = agent_repo.list_all()

    if not all_agents:
        st.info("No agents registered. Register one above.")
    else:
        for agent in all_agents:
            with st.expander(f"{agent.name} ({agent.provider.value})", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**ID:** `{agent.id}`")
                    st.markdown(f"**Model:** {agent.model}")
                    st.markdown(f"**Team:** {agent.team or 'N/A'}")
                    st.markdown(f"**Owner:** {agent.owner or 'N/A'}")
                    if agent.provider != Provider.DUMMY:
                        st.markdown(f"**Base URL:** {agent.base_url}")
                        st.markdown(f"**API Key:** {'•' * 8 + agent.api_key[-4:] if agent.api_key else 'Not set'}")
                with col2:
                    if st.button("Test Connection", key=f"test_{agent.id}"):
                        with st.spinner("Testing..."):
                            adapter = get_adapter(agent)
                            try:
                                healthy = asyncio.run(adapter.health_check())
                                if healthy:
                                    st.success("Connected!")
                                else:
                                    st.error("Failed")
                            except Exception as e:
                                st.error(f"Error: {str(e)[:100]}")

                    if st.button("Delete", key=f"del_{agent.id}", type="secondary"):
                        agent_repo.delete(agent.id)
                        st.session_state.agents.pop(agent.id, None)
                        audit_repo.log("agent_deleted", "agent", agent.id)
                        st.rerun()
