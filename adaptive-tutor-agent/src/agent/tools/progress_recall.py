def recall_progress(wins: list[str] | None = None) -> str | None:
    if not wins:
        return None
    return f"Earlier, you made progress with: {wins[-1]}"
