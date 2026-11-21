from src.adaptation.card_merger import load_merged_rules
from src.adaptation.conflict_resolver import resolve_conflicts
from src.models.session_state import SessionState
from src.models.student_profile import SupportCard


def test_wellbeing_and_accessibility_override_rigor():
    rules = load_merged_rules([
        SupportCard.LOW_CONFIDENCE,
        SupportCard.DYSLEXIA,
        SupportCard.TOUGH_COURSEWORK,
    ])
    state = SessionState(session_id="test", student_id="student", mood="stressed")
    resolved = resolve_conflicts(rules, state)
    assert resolved.index("Use a warm, encouraging tone") < resolved.index("Adjust pacing gradually")
    assert "Offer text-to-speech whenever helpful" in resolved
