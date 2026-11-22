"""Deterministic verification for teacher-approved intermediate math steps.

This intentionally avoids LLM judgment. 'exact' compares normalized literal expressions,
not arbitrary semantic proofs; open-ended proofs require human teacher review.
"""
import re
from decimal import Decimal, InvalidOperation


def canonical(value: str) -> str:
    return re.sub(r'\s+', '', str(value).strip().lower().replace('×', '*').replace('−', '-').replace('²', '^2'))


def verify_step(answer: str, expected: str, kind: str) -> bool:
    if kind == 'numeric':
        try:
            value = Decimal(canonical(answer).replace(',', '.'))
            target = Decimal(canonical(expected).replace(',', '.'))
            return value.is_finite() and target.is_finite() and abs(value-target) <= Decimal('0.000001')
        except InvalidOperation:
            return False
    if kind == 'exact':
        return bool(canonical(answer)) and canonical(answer) == canonical(expected)
    return False


def source_match(chunk_text: str, lesson_key: str, source_terms: list[str]) -> bool:
    normalized = ' '.join(chunk_text.lower().split())
    if lesson_key.lower() in normalized:
        return True
    terms = [x.lower().strip() for x in source_terms if len(str(x).strip()) >= 4]
    return bool(terms) and sum(word in normalized for word in terms) >= min(2,len(terms))


def quiz_safe_summary(quiz: dict, steps: list[dict], completed_positions: set[int]) -> dict:
    """Never expose expected_answer, teacher_explanation or future hints."""
    next_step = next((s for s in steps if s['position'] not in completed_positions), None)
    return {'id':quiz['id'],'title':quiz['title'],'statement':quiz['statement'],'lesson_key':quiz['lesson_key'],
        'total_steps':len(steps),'completed_steps':len(completed_positions),
        'next_step':{'id':next_step['id'],'position':next_step['position'],'prompt':next_step['prompt'],'xp':next_step['xp']} if next_step else None,
        'completed':next_step is None}
