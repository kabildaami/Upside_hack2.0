from pathlib import Path
import yaml

from src.models.student_profile import SupportCard


CARD_DIR = Path(__file__).resolve().parents[2] / "config" / "support_cards"


def load_merged_rules(cards: list[SupportCard]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for card in cards:
        path = CARD_DIR / f"{card.value}.yaml"
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        merged[card.value] = data["rules"]
    return merged
