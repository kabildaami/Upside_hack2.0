"""Strict answer normalization, answer-key stays server side."""
import re
from decimal import Decimal, InvalidOperation

def normalize_answer(value: str) -> str:
    val=' '.join(value.strip().casefold().split())
    # Accept 2,104 as a thousands-grouped integer; 2,5 as decimal 2.5.
    number=val.replace(',','') if re.fullmatch(r'[-+]?\d{1,3}(?:,\d{3})+',val) else val.replace(',','.')
    try:
        return str(Decimal(number).normalize()) if re.fullmatch(r'[-+]?\d+(?:[.,]\d+)?',val) else val
    except InvalidOperation:
        return val

def grade_answer(submitted: str, answer_key: str, template: str, options: list[str]) -> bool:
    if template in ('multiple_choice','true_false'):
        return normalize_answer(submitted) in {normalize_answer(answer_key)}
    return normalize_answer(submitted)==normalize_answer(answer_key)

def valid_quiz_item(item: dict) -> bool:
    template=item.get('template'); opts=item.get('options',[])
    if template not in ('multiple_choice','number_input','true_false') or not isinstance(opts,list): return False
    if template=='number_input' and opts: return False
    if template=='multiple_choice' and not 2<=len(opts)<=6: return False
    if template=='true_false' and opts!=['True','False']: return False
    return bool(str(item.get('prompt','')).strip()) and bool(str(item.get('answer_text','')).strip()) and (template=='number_input' or str(item['answer_text']) in opts)
