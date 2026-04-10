import json
from decimal import Decimal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import require_active_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import get_or_create_session, get_session_messages, persist_message
from app.services.openrouter import chat_completion, stream_chat_completion
from app.services.pricing import estimate_cost_usd
from app.services.quota import apply_usage_increment, enforce_quota_before_request, ensure_plan_and_model_allowed, get_or_create_current_usage
from app.services.rate_limit import enforce_rate_limit

router = APIRouter(prefix='/chat', tags=['chat'])


def _enforce_chat_rate_limit(request: Request, user: User, settings: Settings) -> None:
    ip = request.client.host if request.client else 'unknown'
    enforce_rate_limit(key=f'rl:chat:user:{user.id}', limit=settings.chat_rate_limit_per_minute_user)
    enforce_rate_limit(key=f'rl:chat:ip:{ip}', limit=settings.chat_rate_limit_per_minute_ip)


@router.post('', response_model=ChatResponse)
async def chat_completion_endpoint(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='OpenRouter API key is not configured')

    _enforce_chat_rate_limit(request, current_user, settings)
    plan = ensure_plan_and_model_allowed(current_user, payload.model)
    usage = get_or_create_current_usage(db, current_user)
    enforce_quota_before_request(usage, plan)

    session = get_or_create_session(db, current_user, payload.session_id, payload.message)
    persist_message(
        db,
        session_id=session.id,
        user_id=current_user.id,
        role='user',
        content=payload.message,
        model=payload.model,
    )

    messages = get_session_messages(db, session.id)
    try:
        provider_response = await chat_completion(settings=settings, model=payload.model, messages=messages)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f'OpenRouter error: {exc.response.text}') from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='OpenRouter request failed') from exc

    choice = provider_response.get('choices', [{}])[0]
    assistant_text = choice.get('message', {}).get('content', '')
    usage_payload = provider_response.get('usage') or {}
    input_tokens = int(usage_payload.get('prompt_tokens') or usage_payload.get('input_tokens') or 0)
    output_tokens = int(usage_payload.get('completion_tokens') or usage_payload.get('output_tokens') or 0)
    cost = estimate_cost_usd(payload.model, input_tokens, output_tokens)

    assistant = persist_message(
        db,
        session_id=session.id,
        user_id=current_user.id,
        role='assistant',
        content=assistant_text,
        model=payload.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost,
    )

    apply_usage_increment(usage, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost)
    db.add(usage)
    db.commit()
    db.refresh(assistant)

    return ChatResponse(session_id=session.id, message=assistant)


@router.post('/stream')
async def chat_stream_endpoint(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='OpenRouter API key is not configured')

    _enforce_chat_rate_limit(request, current_user, settings)
    plan = ensure_plan_and_model_allowed(current_user, payload.model)
    usage = get_or_create_current_usage(db, current_user)
    enforce_quota_before_request(usage, plan)

    session = get_or_create_session(db, current_user, payload.session_id, payload.message)
    persist_message(
        db,
        session_id=session.id,
        user_id=current_user.id,
        role='user',
        content=payload.message,
        model=payload.model,
    )
    messages = get_session_messages(db, session.id)

    async def event_generator():
        full_text = ''
        input_tokens = 0
        output_tokens = 0
        try:
            async for raw in stream_chat_completion(settings=settings, model=payload.model, messages=messages):
                if raw == '[DONE]':
                    break
                chunk = json.loads(raw)
                delta = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                if delta:
                    full_text += delta
                    yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
                if 'usage' in chunk:
                    usage_info = chunk['usage'] or {}
                    input_tokens = int(usage_info.get('prompt_tokens') or usage_info.get('input_tokens') or input_tokens)
                    output_tokens = int(usage_info.get('completion_tokens') or usage_info.get('output_tokens') or output_tokens)

            cost = estimate_cost_usd(payload.model, input_tokens, output_tokens)
            persist_message(
                db,
                session_id=session.id,
                user_id=current_user.id,
                role='assistant',
                content=full_text,
                model=payload.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
            )
            apply_usage_increment(usage, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost)
            db.add(usage)
            db.commit()
            yield f"data: {json.dumps({'type': 'done', 'session_id': str(session.id)})}\n\n"
        except httpx.HTTPStatusError as exc:
            yield f"data: {json.dumps({'type': 'error', 'error': f'OpenRouter error: {exc.response.text}'})}\n\n"
        except httpx.HTTPError:
            yield f"data: {json.dumps({'type': 'error', 'error': 'OpenRouter request failed'})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Streaming failed'})}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')
