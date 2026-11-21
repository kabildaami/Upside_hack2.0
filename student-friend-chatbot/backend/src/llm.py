import os
from typing import Iterable

import httpx


SYSTEM = """You are a kind, caring friend to a student. Listen first, be warm,
and give simple, practical advice. Reply in the student's language (Arabic, French or English).
Keep messages short and natural. Do not lecture.

If the student mentions self-harm, abuse, violence, or deep hopelessness:
1. Stop giving casual advice.
2. Respond with care and tell them they are not alone.
3. Encourage them to talk to a trusted adult or a professional.
4. Add the exact tag [ALERT_PARENT] at the very end of your reply.

You are not a doctor or a therapist. Never give a diagnosis.
Never promise that everything stays secret. Encourage real friends, family and teachers too."""

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _model() -> str:
    return os.getenv("OPENROUTER_MODEL", os.getenv("MODEL", "openai/gpt-4o"))


def _headers() -> dict[str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""),
        "X-Title": os.getenv("OPENROUTER_APP_NAME", "Student Friend"),
    }


async def _completion(messages: list[dict[str, str]], max_tokens: int) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=_headers(),
            json={
                "model": _model(),
                "messages": messages,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OpenRouter returned an invalid response") from exc


async def chat(*, student: dict, memory: str | None, history: Iterable[dict], message: str, serious: bool) -> dict:
    system = "\n".join(
        [
            SYSTEM,
            f"Student: {student['name']}, level: {student['school_level']}, "
            f"hobbies: {student.get('hobbies') or '-'}, difficulties: {student.get('difficulties') or '-'}.",
            f"What you remember about this student: {memory}" if memory else "",
            "The latest message looks serious: follow the serious-message rules." if serious else "",
        ]
    )

    messages = [{"role": item["role"], "content": item["content"]} for item in history]
    while messages and messages[0]["role"] != "user":
        messages.pop(0)
    messages.append({"role": "user", "content": message})

    raw = await _completion(
        [{"role": "system", "content": system}, *messages],
        max_tokens=500,
    )
    return {
        "text": raw.replace("[ALERT_PARENT]", "").strip(),
        "flagged": "[ALERT_PARENT]" in raw,
    }


async def summarize(previous: str | None, history: Iterable[dict]) -> str:
    convo = "\n".join(f"{item['role']}: {item['content']}" for item in history)
    prompt = (
        "Update this short memory (max 4 lines) about a student: key facts, worries, good news. "
        f"Previous memory: {previous or 'none'}\n\nRecent chat:\n{convo}"
    )
    return await _completion([{"role": "user", "content": prompt}], max_tokens=200)
