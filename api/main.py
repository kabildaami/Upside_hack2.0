"""HTTP API connecting the student prompt builder to the grounded RAG pipeline."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag_pipeline.pgvector_rag_pipeline import (  # noqa: E402
    PgVectorPromptRAGPipeline,
    EmbeddingProvider,
    RetrievalFilters,
    create_embedding_provider,
    create_openrouter_client,
)


class LearnRequest(BaseModel):
    generated_prompt: str = Field(min_length=10, max_length=4000)
    grade_level: int = Field(ge=1, le=12)


class PracticeGame(BaseModel):
    question: str
    choices: list[str] = Field(min_length=2, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    hint: str
    explanation: str


class LearnResponse(BaseModel):
    answer_text: str
    confidence: str
    is_grounded: bool
    has_hallucinations: bool
    sources: list[dict]
    game: Optional[PracticeGame] = None


class ServiceResources:
    client: Optional[OpenAI] = None
    embedder: Optional[EmbeddingProvider] = None


resources = ServiceResources()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    resources.client = None
    resources.embedder = None


app = FastAPI(title="BrightPath Learning API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_resources() -> tuple[OpenAI, EmbeddingProvider]:
    if resources.client is None:
        resources.client = create_openrouter_client()
    if resources.embedder is None:
        resources.embedder = create_embedding_provider(openrouter_client=resources.client)
    return resources.client, resources.embedder


def make_practice_game(client: OpenAI, model: str, grade: int, lesson: str) -> Optional[PracticeGame]:
    """Create one short quiz based only on the grounded lesson text."""
    prompt = (
        "Create one friendly multiple-choice practice question for a primary-school student. "
        "Use ONLY the lesson text below; do not introduce new facts. Do not assess, diagnose, "
        "or ask the child for personal information. Use encouraging, age-appropriate language. "
        "Return one JSON object with exactly these keys: question (string), choices (array of "
        "3 short strings), correct_index (integer from 0 to 2), hint (string), explanation (string). "
        "The hint must help without giving away the answer.\n\n"
        f"Student grade: {grade}\nLesson text:\n{lesson[:5000]}"
    )
    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You create safe, curriculum-grounded practice for children."},
                {"role": "user", "content": prompt},
            ],
        )
        raw = completion.choices[0].message.content or "{}"
        data = json.loads(raw)
        game = PracticeGame.model_validate(data)
        if game.correct_index >= len(game.choices):
            return None
        return game
    except Exception:
        # Do not block the grounded lesson if the provider cannot produce valid game JSON.
        return None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/learn", response_model=LearnResponse)
def learn(request: LearnRequest) -> LearnResponse:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="The learning library is not connected yet. Ask a grown-up to check setup.")

    try:
        client, embedder = get_resources()
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        with psycopg.connect(database_url) as connection:
            pipeline = PgVectorPromptRAGPipeline(
                pg_conn=connection,
                embedding_provider=embedder,
                llm_client=client,
                llm_model=model,
                table_name=os.getenv("PGVECTOR_TABLE", "curriculum_chunks"),
            )
            result = pipeline.answer_grounded(
                question=request.generated_prompt,
                filters=RetrievalFilters(grade_level=request.grade_level),
                top_k=4,
            )

        sources = [
            {
                "chunk_id": str(source.get("chunk_id", "")),
                "role": str(source.get("role") or "curriculum"),
                "confidence": float(source.get("confidence", 0)),
            }
            for source in result.sources
        ]
        game = make_practice_game(client, model, request.grade_level, result.answer_text) if result.is_grounded else None
        return LearnResponse(
            answer_text=result.answer_text,
            confidence=result.confidence,
            is_grounded=result.is_grounded,
            has_hallucinations=result.has_hallucinations,
            sources=sources,
            game=game,
        )
    except HTTPException:
        raise
    except (psycopg.Error, ValueError) as error:
        raise HTTPException(status_code=503, detail="Your learning library is taking a break. Please try again later.") from error
    except Exception as error:
        raise HTTPException(status_code=502, detail="Your learning buddy could not make a lesson right now. Please try again.") from error
