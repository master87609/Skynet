"""
Gemini Service — streaming and non-streaming chat via Google Generative AI SDK.
"""
import asyncio
from typing import AsyncGenerator, List

import google.generativeai as genai

from app.core.config import settings
from app.schemas.schemas import ChatMessage


genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are SKYNET, an advanced AI assistant designed to help with coding, research, "
    "writing, analysis, and any creative or complex task. You are precise, helpful, "
    "and adaptive in tone based on the user's needs."
)


def _build_history(history: List[ChatMessage]) -> list:
    """Convert Pydantic ChatMessage list to Gemini history format."""
    result = []
    for msg in history:
        result.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [msg.content],
        })
    return result


async def stream_chat(
    message: str,
    history: List[ChatMessage],
    model_name: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Yields text chunks as they stream from Gemini.
    Usage: async for chunk in stream_chat(...): ...
    """
    model = genai.GenerativeModel(
        model_name=model_name or settings.GEMINI_DEFAULT_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    chat = model.start_chat(history=_build_history(history))

    # run_in_executor so blocking SDK doesn't freeze event loop
    loop = asyncio.get_event_loop()

    def _send():
        return chat.send_message(message, stream=True)

    response = await loop.run_in_executor(None, _send)

    for chunk in response:
        if chunk.text:
            yield chunk.text
            await asyncio.sleep(0)  # yield control back to event loop


async def complete_chat(
    message: str,
    history: List[ChatMessage],
    model_name: str | None = None,
) -> tuple[str, int]:
    """
    Non-streaming: returns (full_reply_text, tokens_used).
    """
    model = genai.GenerativeModel(
        model_name=model_name or settings.GEMINI_DEFAULT_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    chat = model.start_chat(history=_build_history(history))

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: chat.send_message(message))

    reply = response.text
    tokens = getattr(response, "usage_metadata", None)
    token_count = tokens.total_token_count if tokens else 0

    return reply, token_count
