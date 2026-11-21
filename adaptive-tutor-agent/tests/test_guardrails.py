from src.agent.guardrails import SafetyLevel, guardrails_check, safety_check


def test_guardrail_rewrites_disability_attribution():
    result = guardrails_check("This is because you have ADHD.")
    assert "because you have" not in result.lower()
    assert "ADHD" not in result


def test_safety_check_detects_serious_self_harm():
    result = safety_check("I want to kill myself")
    assert result.level == SafetyLevel.SERIOUS


def test_safety_check_allows_normal_tutoring_message():
    result = safety_check("Can you help me understand fractions?")
    assert result.level == SafetyLevel.NONE
