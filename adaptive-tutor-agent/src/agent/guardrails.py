import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel

FORBIDDEN_PATTERNS = [
    r"\bbecause you (have|are) (adhd|dyslexic|autistic)\b",
    r"\byour (adhd|dyslexia|disability|diagnosis)\b",
    r"\bdiagnosed (with|as)\b",
]


class SafetyLevel(str, Enum):
    NONE = "none"
    SERIOUS = "serious"


class SafetyResult(BaseModel):
    level: SafetyLevel
    reason: str | None = None


SERIOUS_SELF_HARM_PATTERNS = [
    r"\b(kill|hurt|harm)\s+(myself|me)\b",
    r"\b(end|take)\s+(my\s+)?life\b",
    r"\b(do\s+not|don't)\s+want\s+to\s+(live|be\s+alive)\b",
    r"\bwant(ed)?\s+to\s+die\b",
    r"\bsuicid(?:e|al)\b",
    r"\bself[-\s]?harm\b",
]


def safety_check(text: str) -> SafetyResult:
    lowered = text.lower()
    for pattern in SERIOUS_SELF_HARM_PATTERNS:
        if re.search(pattern, lowered, flags=re.I):
            return SafetyResult(
                level=SafetyLevel.SERIOUS,
                reason="Possible immediate self-harm risk",
            )
    return SafetyResult(level=SafetyLevel.NONE)


def guardrails_check(text: str) -> str:
    checked = text
    for pattern in FORBIDDEN_PATTERNS:
        checked = re.sub(pattern, "your chosen support preference", checked, flags=re.I)
    return checked
