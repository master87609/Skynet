"""
Website Builder Agents API — Multi-Agent Team Orchestration.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional

from app.api.deps import get_current_user
from app.models.pg_models import User
from app.services.website_agent_team import stream_website_builder, _call_gemini, CODER_PROMPT, _clean_code_block

router = APIRouter(prefix="/agents", tags=["Website Builder Agents"])


class WebsiteBuildRequest(BaseModel):
    prompt: str
    category: Optional[str] = "General"


class WebsiteRefineRequest(BaseModel):
    current_html: str
    instruction: str


@router.post("/website/build", summary="Stream Multi-Agent Website Generation (SSE)")
async def build_website_stream(
    payload: WebsiteBuildRequest,
    # Allow both authenticated and trial/guest users
):
    """
    Orchestrates the 5 specialized agents:
    - Architect Agent
    - Copywriter Agent
    - Designer Agent
    - Coder Agent
    - QA Reviewer Agent
    Streams progress events and returns complete standalone HTML code.
    """
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    return StreamingResponse(
        stream_website_builder(payload.prompt, "guest"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/website/refine", summary="Refine Website with Agent Feedback")
async def refine_website(payload: WebsiteRefineRequest):
    """
    Allows the user to tell the agents:
    'Change the color palette to emerald green',
    'Add a contact form modal', etc.
    """
    instruction_prompt = (
        f"You are the Lead Developer Agent. Given this existing HTML website:\n"
        f"```html\n{payload.current_html[:4000]}\n```\n"
        f"Apply this specific refinement: '{payload.instruction}'.\n"
        f"Keep the entire HTML valid, responsive, and working. Return ONLY the complete updated HTML."
    )
    new_html = await _call_gemini(CODER_PROMPT, instruction_prompt)
    cleaned = _clean_code_block(new_html)
    if not cleaned or "<html" not in cleaned.lower():
        cleaned = payload.current_html  # Fallback to current if refinement failed

    return {"html": cleaned, "instruction": payload.instruction, "status": "refined"}


@router.post("/website/download", summary="Download Website as index.html")
async def download_website(html: str):
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=index.html"},
    )
