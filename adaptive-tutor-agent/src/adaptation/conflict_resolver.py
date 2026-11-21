from pathlib import Path
import yaml

from src.models.session_state import SessionState


MATRIX_PATH = Path(__file__).resolve().parents[2] / "config" / "support_cards" / "priority_matrix.yaml"


def resolve_conflicts(rules: dict[str, list[str]], state: SessionState) -> list[str]:
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    priority_order = matrix["priority_order"]
    card_priorities = matrix["card_priorities"]

    ranked: list[tuple[int, str]] = []
    for card, card_rules in rules.items():
        category = card_priorities.get(card, "Rigor")
        rank = len(priority_order) - priority_order.index(category)
        if state.mood in {"tired", "stressed"} or state.stress >= 7:
            rank += len(priority_order)
        for rule in card_rules:
            ranked.append((rank, rule))

    unique = sorted(set(ranked), key=lambda item: (-item[0], item[1]))
    return [rule for _, rule in unique]
