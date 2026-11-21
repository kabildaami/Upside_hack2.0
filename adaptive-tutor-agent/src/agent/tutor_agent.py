import os
import httpx

from src.adaptation.prompt_assembler import assemble_prompt
from src.agent.guardrails import guardrails_check
from src.agent.tools.task_decomposer import decompose_task
from src.models.student_profile import StudentProfile
from src.models.session_state import SessionState


async def generate_tutor_response(
    profile: StudentProfile,
    state: SessionState,
    message: str,
) -> dict:
    system_prompt, response = assemble_prompt(profile, state, message)
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            result = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "temperature": 0.4,
                },
            )
            result.raise_for_status()
            text = result.json()["choices"][0]["message"]["content"]
    else:
        text = (
            "Let’s work through this in a small, manageable way. "
            f"First, tell me which part of “{message}” feels least clear."
        )

    text = guardrails_check(text)
    steps = decompose_task(text) if len(text) > 260 or len(message) > 80 else []
    response.text = text
    response.steps = steps
    response.encouragement = "You do not need to solve everything at once."
    return response.model_dump()
