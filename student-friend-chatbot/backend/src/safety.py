import re


PATTERNS = [
    re.compile(r"suicid|kill myself|want to die|end my life|hurt myself|self[- ]?harm|cut myself", re.I),
    re.compile(r"me tuer|veux mourir|en finir avec|me faire du mal|automutil|plus envie de vivre", re.I),
    re.compile(r"انتحر|أقتل نفسي|أريد أن أموت|نفسي أموت"),
    re.compile(r"(hits|beats|abuses|touches) me|il me frappe|elle me frappe|abus(e|é)|يضربني|يعتدي عليّ", re.I),
    re.compile(r"no reason to live|hopeless|rien n'a de sens|لا أمل", re.I),
]


def check_risk(text: str) -> dict[str, bool]:
    return {"serious": any(pattern.search(text) for pattern in PATTERNS)}
