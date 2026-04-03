from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.middleware.auth import ApiKeyMiddleware
from app.middleware.rate_limit import limiter
from app.routes import chat, health

app = FastAPI(title="AI Inference Proxy", version="1.0.0")

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(ApiKeyMiddleware)

# Routes
app.include_router(health.router)
app.include_router(chat.router)
