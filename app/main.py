from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware.rate_limit import limiter
from app.routes import chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 공유 httpx 클라이언트 (커넥션 풀링)
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.ollama_base_url,
        timeout=120.0,
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(title="AI Inference Proxy", version="1.0.0", lifespan=lifespan)

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routes
app.include_router(health.router)
app.include_router(chat.router)
