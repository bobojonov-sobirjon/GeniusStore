from __future__ import annotations

import httpx
from django.conf import settings


async def telegram_send_markdown(text: str) -> None:
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or ''
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '') or ''
    if not token or not chat_id:
        return
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text[:4096],
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(url, json=payload)
