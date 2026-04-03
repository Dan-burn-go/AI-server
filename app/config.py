from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    api_key: str  # 필수 — .env 없으면 기동 실패
    rate_limit: str = "30/minute"
    model_name: str = "qwen3.5:4b"

    model_config = {"env_file": ".env", "protected_namespaces": ()}


settings = Settings()
