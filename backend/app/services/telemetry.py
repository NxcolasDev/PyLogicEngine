"""Persistência OO/SQLAlchemy e publicação AWS com async/await sem bloquear o loop."""

import asyncio
import json
from datetime import datetime, timezone

import boto3
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.domain import Event


def record_event(db: Session, *, user_id: int, severity: str, message: str) -> Event:
    """Cria entidade ORM com argumentos tipados e confirma a transação de analytics."""

    event = Event(
        user_id=user_id,
        severity=severity,
        message=message,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


async def publish_event(event: Event) -> bool:
    """Usa async/await e thread de trabalho para publicar sem bloquear o event loop."""

    settings = get_settings()
    if not settings.sqs_queue_url:
        return False

    payload = {
        "event_id": event.id,
        "user_id": event.user_id,
        "severity": event.severity,
        "message": event.message,
        "created_at": event.created_at.isoformat(),
    }

    def send_message() -> None:
        client = boto3.client("sqs", region_name=settings.aws_region)
        client.send_message(
            QueueUrl=settings.sqs_queue_url,
            MessageBody=json.dumps(payload),
        )

    await asyncio.to_thread(send_message)
    return True
