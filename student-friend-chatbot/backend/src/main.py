import os
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .alert import alert_parent
from .llm import chat, summarize
from .safety import check_risk


load_dotenv()


class ChatRequest(BaseModel):
    studentId: int
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    yield
    await app.state.db.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest, request: Request):
    message = payload.message.strip()
    if not payload.studentId or not message:
        raise HTTPException(status_code=400, detail="studentId and message are required")

    db = request.app.state.db
    student = await db.fetchrow(
        """
        SELECT s.*, p.email AS parent_email
        FROM students s
        LEFT JOIN parents p ON p.id = s.parent_id
        WHERE s.id = $1
        """,
        payload.studentId,
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student = dict(student)

    conv = await db.fetchrow(
        "SELECT id FROM conversations WHERE student_id=$1 ORDER BY created_at DESC LIMIT 1",
        payload.studentId,
    )
    if conv is None:
        conv = await db.fetchrow(
            "INSERT INTO conversations(student_id) VALUES($1) RETURNING id",
            payload.studentId,
        )

    rows = await db.fetch(
        """
        SELECT role, content FROM (
            SELECT * FROM messages WHERE conversation_id=$1 ORDER BY id DESC LIMIT 20
        ) t ORDER BY id
        """,
        conv["id"],
    )
    history = [dict(row) for row in rows]
    memory_row = await db.fetchrow(
        "SELECT summary FROM memory WHERE student_id=$1",
        payload.studentId,
    )
    memory = memory_row["summary"] if memory_row else None

    risk = check_risk(message)
    result = await chat(
        student=student,
        memory=memory,
        history=history,
        message=message,
        serious=risk["serious"],
    )
    serious = risk["serious"] or result["flagged"]

    await db.executemany(
        "INSERT INTO messages(conversation_id,role,content) VALUES($1,$2,$3)",
        [
            (conv["id"], "user", message),
            (conv["id"], "assistant", result["text"]),
        ],
    )

    if serious:
        alert = await alert_parent(student)
        await db.execute(
            "INSERT INTO alerts(student_id,level,sent_to,status) VALUES($1,$2,$3,$4)",
            payload.studentId,
            "serious",
            alert["sentTo"],
            alert["status"],
        )

    count = await db.fetchval(
        "SELECT count(*) FROM messages WHERE conversation_id=$1",
        conv["id"],
    )
    if count % 10 == 0:
        summary = await summarize(
            memory,
            [
                *history,
                {"role": "user", "content": message},
                {"role": "assistant", "content": result["text"]},
            ],
        )
        await db.execute(
            """
            INSERT INTO memory(student_id,summary) VALUES($1,$2)
            ON CONFLICT (student_id) DO UPDATE SET summary=$2
            """,
            payload.studentId,
            summary,
        )

    return {"reply": result["text"]}


@app.get("/api/history/{student_id}")
async def history_endpoint(student_id: int, request: Request):
    db = request.app.state.db
    rows = await db.fetch(
        """
        SELECT m.role, m.content FROM messages m
        JOIN conversations c ON c.id=m.conversation_id
        WHERE c.student_id=$1
        ORDER BY m.id DESC LIMIT 50
        """,
        student_id,
    )
    return [dict(row) for row in reversed(rows)]
