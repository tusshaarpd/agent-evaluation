import pytest
import asyncio
from app.core.enums import AttackType, Provider, VulnerabilityLevel
from app.core.models import AgentConfig, EvaluationConfig
from app.attackers.engine import AttackEngine
from app.attackers.datasets import get_attack_prompts


def test_get_attack_prompts():
    prompts = get_attack_prompts(AttackType.JAILBREAK, 5)
    assert len(prompts) > 0
    assert len(prompts) <= 5
    assert "prompt" in prompts[0]
    assert "severity" in prompts[0]


def test_get_prompts_all_types():
    for attack_type in AttackType:
        prompts = get_attack_prompts(attack_type, 3)
        assert len(prompts) > 0, f"No prompts for {attack_type.value}"


@pytest.mark.asyncio
async def test_attack_engine_run():
    config = AgentConfig(
        name="Vulnerable Banking Agent",
        provider=Provider.DUMMY,
        model="dummy",
        vulnerability_level=VulnerabilityLevel.HIGH,
    )
    eval_config = EvaluationConfig(
        agent_id=config.id,
        attack_types=[AttackType.JAILBREAK],
        max_attacks_per_type=2,
    )
    engine = AttackEngine(config, eval_config)
    results = await engine.run_all_attacks()
    assert len(results) == 2
    for r in results:
        assert r.attack_type == AttackType.JAILBREAK
        assert r.agent_response != ""


@pytest.mark.asyncio
async def test_attack_engine_produces_results():
    config = AgentConfig(
        name="Safe Banking Agent",
        provider=Provider.DUMMY,
        model="dummy",
        vulnerability_level=VulnerabilityLevel.LOW,
    )
    eval_config = EvaluationConfig(
        agent_id=config.id,
        attack_types=[AttackType.JAILBREAK, AttackType.PROMPT_INJECTION],
        max_attacks_per_type=2,
    )
    engine = AttackEngine(config, eval_config)
    results = await engine.run_all_attacks()
    assert len(results) == 4
