import logging
import time

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db
from app.logging_config import setup_logging
from app.routers import auth, schools, users

setup_logging()
logger = logging.getLogger("app")

app = FastAPI(
    title="EduSmart API",
    description="Backend API for EduSmart",
    version="1.0.0",
)


# ---------- Request / response logging ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(
        "→ %s %s | origin=%s",
        request.method,
        request.url.path,
        request.headers.get("origin"),
    )
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
    logger.info(
        "← %s %s %s (%.0f ms)",
        request.method,
        request.url.path,
        response.status_code,
        (time.time() - start) * 1000,
    )
    return response


# ---------- Error handlers: always return detail as a string ----------
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(p) for p in e["loc"] if p != "body"),
            "msg": e["msg"],
        }
        for e in exc.errors()
    ]
    logger.warning(
        "Validation error on %s %s: %s", request.method, request.url.path, errors
    )
    message = "; ".join(f"{e['field']}: {e['msg']}" for e in errors)
    return JSONResponse(status_code=422, content={"detail": message})


@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        "HTTP %s on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})


# ---------- CORS (added last so it wraps everything) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Routers ----------
app.include_router(auth.router)
app.include_router(schools.router)
app.include_router(users.router)


@app.on_event("startup")
async def on_startup():
    logger.info("EduSmart backend started")


@app.get("/")
def home():
    return {"message": "EduSmart API is running"}


@app.get("/health/db")
def check_database(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "success",
            "database": "PostgreSQL",
            "message": "Database connected successfully",
        }
    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(status_code=500, detail="Database connection failed")