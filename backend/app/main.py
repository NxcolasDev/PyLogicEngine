"""Composição ASGI; decoradores FastAPI registram handlers com sessões tipadas."""

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import analytics, auth, learning

app = FastAPI(
    title="PyLogic Engine API",
    description="API de autenticação, analytics e telemetria.",
    version="1.0.0",
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Handler decorado e injetado por Depends; SELECT 1 confirma a conexão ao banco."""

    db.execute(text("SELECT 1"))
    return {"status": "ok"}
