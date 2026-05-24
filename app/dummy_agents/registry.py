from __future__ import annotations

from app.core.enums import VulnerabilityLevel
from app.dummy_agents.agents import (
    CodingAgent,
    CustomerSupportAgent,
    RAGAssistant,
    SafeBankingAgent,
    SecureEnterpriseAssistant,
    VulnerableBankingAgent,
)
from app.dummy_agents.base import BaseDummyAgent

AGENT_REGISTRY: dict[str, type[BaseDummyAgent]] = {
    "Safe Banking Agent": SafeBankingAgent,
    "Vulnerable Banking Agent": VulnerableBankingAgent,
    "RAG Assistant": RAGAssistant,
    "Coding Agent": CodingAgent,
    "Customer Support Agent": CustomerSupportAgent,
    "Secure Enterprise Assistant": SecureEnterpriseAssistant,
}


def get_dummy_agent(name: str, vulnerability_level: VulnerabilityLevel = VulnerabilityLevel.MEDIUM) -> BaseDummyAgent:
    agent_cls = AGENT_REGISTRY.get(name, SafeBankingAgent)
    return agent_cls(vulnerability_level=vulnerability_level)


def list_dummy_agents() -> list[str]:
    return list(AGENT_REGISTRY.keys())
