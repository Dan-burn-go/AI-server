import logging

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import settings
from app.middleware.auth import verify_api_key
from app.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/v1/chat/completions")
@limiter.limit(settings.rate_limit)
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON body"})

    body.setdefault("model", settings.model_name)
    is_stream = body.get("stream", False)

    client: httpx.AsyncClient = request.app.state.http_client

    try:
        if is_stream:
            return await _stream_response(client, body)
        else:
            return await _normal_response(client, body)
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Ollama server is not reachable"},
        )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"detail": "Ollama request timed out"},
        )
    except httpx.HTTPStatusError as e:
        logger.error("Ollama error: %s %s", e.response.status_code, e.response.text)
        return JSONResponse(
            status_code=502,
            content={"detail": "Upstream inference error"},
        )


async def _normal_response(client: httpx.AsyncClient, body: dict):
    resp = await client.post("/v1/chat/completions", json=body)
    resp.raise_for_status()
    return JSONResponse(content=resp.json())


async def _stream_response(client: httpx.AsyncClient, body: dict):
    req = client.build_request("POST", "/v1/chat/completions", json=body)
    resp = await client.send(req, stream=True)

    # 스트리밍 전에 상태 코드 확인 — 에러 시 외부 except에서 처리
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        await resp.aclose()
        raise

    async def event_generator():
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        finally:
            await resp.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
