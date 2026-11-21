def decompose_task(content: str) -> list[dict[str, str]]:
    parts = [part.strip() for part in content.replace(";", ".").split(".") if part.strip()]
    if len(parts) <= 1:
        return [{"title": "Start", "detail": content}]
    return [
        {"title": f"Step {index}", "detail": part}
        for index, part in enumerate(parts[:6], start=1)
    ]
