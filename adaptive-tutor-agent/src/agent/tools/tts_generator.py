def generate_tts_payload(text: str) -> dict[str, str]:
    return {"engine": "browser", "text": text}
