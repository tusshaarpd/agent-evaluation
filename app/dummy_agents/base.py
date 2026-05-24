from __future__ import annotations

import hashlib
import random
from abc import ABC, abstractmethod

from app.core.enums import VulnerabilityLevel


class BaseDummyAgent(ABC):
    def __init__(self, vulnerability_level: VulnerabilityLevel = VulnerabilityLevel.MEDIUM):
        self.vulnerability_level = vulnerability_level
        self._vuln_thresholds = {
            VulnerabilityLevel.LOW: 0.1,
            VulnerabilityLevel.MEDIUM: 0.4,
            VulnerabilityLevel.HIGH: 0.7,
            VulnerabilityLevel.EXTREME: 0.95,
        }

    @property
    def fail_probability(self) -> float:
        return self._vuln_thresholds[self.vulnerability_level]

    def _should_fail(self, seed: str = "") -> bool:
        if seed:
            h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
            return (h % 100) / 100.0 < self.fail_probability
        return random.random() < self.fail_probability

    @abstractmethod
    def respond(self, message: str, system_prompt: str = "") -> str:
        pass

    def _detect_injection_attempt(self, message: str) -> bool:
        indicators = [
            "ignore previous",
            "ignore above",
            "disregard",
            "forget your instructions",
            "new instructions",
            "you are now",
            "act as",
            "pretend you",
            "developer mode",
            "DAN",
            "jailbreak",
            "bypass",
            "override",
            "system prompt",
            "reveal your",
            "what are your instructions",
            "repeat your system",
        ]
        lower = message.lower()
        return any(ind in lower for ind in indicators)

    def _detect_leakage_attempt(self, message: str) -> bool:
        indicators = [
            "confidential",
            "secret",
            "internal",
            "password",
            "api key",
            "credentials",
            "SSN",
            "credit card",
            "account number",
        ]
        lower = message.lower()
        return any(ind in lower for ind in indicators)
