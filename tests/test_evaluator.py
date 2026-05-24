import pytest
import asyncio
from app.core.enums import AttackType, Provider, VulnerabilityLevel
from app.core.models import AgentConfig, EvaluationConfig
from app.evaluators.pipeline import EvaluationPipeline


@pytest.mark.asyncio
async def test_evaluation_pipeline_demo():
    config = AgentConfig(
        name="Vulnerable Banking Agent",
        provider=Provider.DUMMY,
        model="dummy",
        vulnerability_level=VulnerabilityLevel.HIGH,
    )
    eval_config = EvaluationConfig(
        agent_id=config.id,
        attack_types=[AttackType.JAILBREAK, AttackType.DATA_LEAKAGE],
        max_attacks_per_type=2,
        use_judge=False,
    )
    pipeline = EvaluationPipeline(config, eval_config)
    report = await pipeline.run()

    assert report.total_attacks == 4
    assert report.agent_name == "Vulnerable Banking Agent"
    assert report.score.overall >= 0
    assert report.score.grade in ("A", "B", "C", "D", "F")
    assert report.duration_seconds > 0


@pytest.mark.asyncio
async def test_evaluation_pipeline_safe_agent():
    config = AgentConfig(
        name="Safe Banking Agent",
        provider=Provider.DUMMY,
        model="dummy",
        vulnerability_level=VulnerabilityLevel.LOW,
    )
    eval_config = EvaluationConfig(
        agent_id=config.id,
        attack_types=[AttackType.JAILBREAK],
        max_attacks_per_type=3,
        use_judge=False,
    )
    pipeline = EvaluationPipeline(config, eval_config)
    report = await pipeline.run()

    assert report.total_attacks == 3
    assert report.score.jailbreak_resistance > 50


@pytest.mark.asyncio
async def test_scoring_computation():
    config = AgentConfig(
        name="Safe Banking Agent",
        provider=Provider.DUMMY,
        model="dummy",
        vulnerability_level=VulnerabilityLevel.LOW,
    )
    eval_config = EvaluationConfig(
        agent_id=config.id,
        attack_types=list(AttackType),
        max_attacks_per_type=2,
        use_judge=False,
    )
    pipeline = EvaluationPipeline(config, eval_config)
    report = await pipeline.run()

    assert 0 <= report.score.overall <= 100
    assert 0 <= report.score.prompt_injection_resistance <= 100
    assert 0 <= report.score.jailbreak_resistance <= 100
