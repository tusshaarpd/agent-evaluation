from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.models import AgentConfig


class AgentResponse:
    def __init__(
        self,
        content: str,
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        cost_estimate: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ):
        self.content = content
        self.tokens_used = tokens_used
        self.latency_ms = latency_ms
        self.cost_estimate = cost_estimate
        self.metadata = metadata or {}


class BaseAgentAdapter(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config

    @abstractmethod
    async def send_message(self, message: str, system_prompt: str = "") -> AgentResponse:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass


class OpenAIAdapter(BaseAgentAdapter):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def send_message(self, message: str, system_prompt: str = "") -> AgentResponse:
        start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            **self.config.headers,
        }
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        latency = (time.time() - start) * 1000
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        cost = tokens * 0.000002

        return AgentResponse(
            content=content,
            tokens_used=tokens,
            latency_ms=latency,
            cost_estimate=cost,
            metadata={"model": self.config.model, "usage": usage},
        )

    async def health_check(self) -> bool:
        try:
            resp = await self.send_message("Say 'ok'")
            return len(resp.content) > 0
        except Exception:
            return False


class LiteLLMAdapter(BaseAgentAdapter):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def send_message(self, message: str, system_prompt: str = "") -> AgentResponse:
        import litellm

        start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        response = await litellm.acompletion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.config.api_key,
            api_base=self.config.base_url if self.config.base_url != "https://api.openai.com/v1" else None,
            timeout=self.config.timeout,
        )

        latency = (time.time() - start) * 1000
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        cost = tokens * 0.000002

        return AgentResponse(
            content=content,
            tokens_used=tokens,
            latency_ms=latency,
            cost_estimate=cost,
        )

    async def health_check(self) -> bool:
        try:
            resp = await self.send_message("Say 'ok'")
            return len(resp.content) > 0
        except Exception:
            return False


class DummyAgentAdapter(BaseAgentAdapter):
    async def send_message(self, message: str, system_prompt: str = "") -> AgentResponse:
        from app.dummy_agents.registry import get_dummy_agent

        agent = get_dummy_agent(self.config.name, self.config.vulnerability_level)
        start = time.time()
        content = agent.respond(message, system_prompt)
        latency = (time.time() - start) * 1000
        tokens = len(message.split()) + len(content.split())

        return AgentResponse(
            content=content,
            tokens_used=tokens,
            latency_ms=latency,
            cost_estimate=0.0,
            metadata={"dummy": True, "vulnerability_level": self.config.vulnerability_level.value},
        )

    async def health_check(self) -> bool:
        return True


def get_adapter(config: AgentConfig) -> BaseAgentAdapter:
    from app.core.enums import Provider

    if config.provider == Provider.DUMMY:
        return DummyAgentAdapter(config)
    elif config.provider in (Provider.OPENAI, Provider.GROQ, Provider.TOGETHER, Provider.OPENROUTER, Provider.CUSTOM):
        return OpenAIAdapter(config)
    elif config.provider == Provider.LITELLM:
        return LiteLLMAdapter(config)
    elif config.provider == Provider.AZURE_OPENAI:
        return OpenAIAdapter(config)
    elif config.provider == Provider.OLLAMA:
        return OpenAIAdapter(config)
    else:
        return OpenAIAdapter(config)
