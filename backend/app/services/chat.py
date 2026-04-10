from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User


def get_or_create_session(db: Session, user: User, session_id: UUID | None, initial_title: str) -> ChatSession:
    if session_id:
        session = db.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id))
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
        return session

    title = initial_title[:80] if initial_title else 'New Chat'
    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_messages(db: Session, session_id: UUID) -> list[dict[str, str]]:
    rows = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return [{'role': m.role, 'content': m.content} for m in rows]


def persist_message(
    db: Session,
    *,
    session_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: Decimal = Decimal('0'),
) -> ChatMessage:
    msg = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
