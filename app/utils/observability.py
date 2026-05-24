from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent_eval")


@dataclass
class MetricsCollector:
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    total_latency_ms: float = 0.0
    errors: int = 0
    attack_successes: int = 0
    attack_failures: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def record_request(self, tokens: int = 0, cost: float = 0.0, latency_ms: float = 0.0, success: bool = False) -> None:
        self.total_requests += 1
        self.total_tokens += tokens
        self.total_cost += cost
        self.total_latency_ms += latency_ms
        if success:
            self.attack_successes += 1
        else:
            self.attack_failures += 1
        self.history.append({
            "timestamp": time.time(),
            "tokens": tokens,
            "cost": cost,
            "latency_ms": latency_ms,
            "success": success,
        })

    def record_error(self) -> None:
        self.errors += 1

    @property
    def avg_latency(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_latency_ms / self.total_requests

    @property
    def success_rate(self) -> float:
        total = self.attack_successes + self.attack_failures
        if total == 0:
            return 0.0
        return self.attack_successes / total

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_latency_ms": self.avg_latency,
            "errors": self.errors,
            "attack_success_rate": self.success_rate,
        }


_global_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    return _global_metrics


def reset_metrics() -> None:
    global _global_metrics
    _global_metrics = MetricsCollector()
