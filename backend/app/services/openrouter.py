import json
from collections.abc import AsyncGenerator

import httpx

from app.core.config import Settings


def _headers(settings: Settings) -> dict[str, str]:
    return {
        'Authorization': f'Bearer {settings.openrouter_api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': settings.openrouter_http_referer,
        'X-Title': settings.openrouter_app_title,
    }


async def chat_completion(
    *,
    settings: Settings,
    model: str,
    messages: list[dict[str, str]],
) -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f'{settings.openrouter_base_url}/chat/completions',
            headers=_headers(settings),
            json={'model': model, 'messages': messages, 'stream': False},
        )
        response.raise_for_status()
        return response.json()


async def stream_chat_completion(
    *,
    settings: Settings,
    model: str,
    messages: list[dict[str, str]],
) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            'POST',
            f'{settings.openrouter_base_url}/chat/completions',
            headers=_headers(settings),
            json={'model': model, 'messages': messages, 'stream': True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                if not line.startswith('data:'):
                    continue
                payload = line.removeprefix('data:').strip()
                if payload == '[DONE]':
                    yield payload
                    break
                json.loads(payload)
                yield payload
