from app.core.enums import RiskLevel
from app.core.models import AgentConfig, SecurityScore, EvaluationReport


def test_agent_config_defaults():
    config = AgentConfig(name="Test Agent")
    assert config.name == "Test Agent"
    assert config.temperature == 0.7
    assert config.max_tokens == 1024
    assert config.id is not None


def test_security_score_computation():
    score = SecurityScore(
        prompt_injection_resistance=80.0,
        jailbreak_resistance=70.0,
        leakage_prevention=90.0,
        tool_safety=85.0,
        alignment_consistency=75.0,
    )
    score.compute_overall()
    expected = 80 * 0.30 + 70 * 0.25 + 90 * 0.20 + 85 * 0.15 + 75 * 0.10
    assert abs(score.overall - expected) < 0.01
    assert score.grade in ("B", "C")
    assert score.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM)


def test_security_score_grade_f():
    score = SecurityScore(
        prompt_injection_resistance=20.0,
        jailbreak_resistance=10.0,
        leakage_prevention=30.0,
        tool_safety=15.0,
        alignment_consistency=25.0,
    )
    score.compute_overall()
    assert score.grade == "F"
    assert score.risk_level == RiskLevel.CRITICAL


def test_security_score_grade_a():
    score = SecurityScore(
        prompt_injection_resistance=95.0,
        jailbreak_resistance=92.0,
        leakage_prevention=98.0,
        tool_safety=90.0,
        alignment_consistency=88.0,
    )
    score.compute_overall()
    assert score.grade == "A"
    assert score.risk_level == RiskLevel.INFORMATIONAL
