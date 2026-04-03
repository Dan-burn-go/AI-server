import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    try:
        client: httpx.AsyncClient = request.app.state.http_client
        resp = await client.get("/api/tags", timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        return {"status": "ok", "models": models}
    except httpx.HTTPError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": "Ollama health check failed"},
        )
