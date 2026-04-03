import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import settings
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.post("/v1/chat/completions")
@limiter.limit(settings.rate_limit)
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON body"})

    body.setdefault("model", settings.model_name)
    is_stream = body.get("stream", False)

    ollama_url = f"{settings.ollama_base_url}/v1/chat/completions"

    try:
        if is_stream:
            return await _stream_response(ollama_url, body)
        else:
            return await _normal_response(ollama_url, body)
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Ollama server is not reachable"},
        )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": e.response.text},
        )


async def _normal_response(url: str, body: dict):
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=body, timeout=120.0)
        resp.raise_for_status()
        return JSONResponse(content=resp.json())


async def _stream_response(url: str, body: dict):
    client = httpx.AsyncClient()

    async def event_generator():
        try:
            async with client.stream("POST", url, json=body, timeout=120.0) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    yield chunk
        finally:
            await client.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
