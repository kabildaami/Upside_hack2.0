"""Parse standardized Exellence Academy grade names without network/database imports."""
import re
GRADE_LABELS = {**{f'{n}{"st" if n==1 else "nd" if n==2 else "rd" if n==3 else "th"} primary':n for n in range(1,7)},
                **{f'{n}{"st" if n==1 else "nd" if n==2 else "rd" if n==3 else "th"} grade':n for n in range(7,13)}}

def parse_grade(label: str | None) -> int | None:
    if not label: return None
    s = label.strip().lower()
    if s in GRADE_LABELS: return GRADE_LABELS[s]
    match = re.fullmatch(r'(?:grade\s*)?(1[0-2]|[1-9])(?:\s*[a-z])?', s)
    return int(match.group(1)) if match else None
