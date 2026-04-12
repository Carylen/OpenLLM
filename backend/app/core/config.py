from functools import lru_cache

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore')

    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/openllm'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = 'OpenLLM MVP'
    environment: str = 'development'
    debug: bool = True
    backend_cors_origins: list[AnyHttpUrl] = []

    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/openllm'
    redis_url: str = 'redis://localhost:6379/0'

    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 60 * 24 * 7
    auth_cookie_name: str = 'openllm_session'
    auth_cookie_secure: bool = False
    auth_cookie_domain: str | None = None

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = 'http://localhost:8000/auth/google/callback'
    frontend_url: str = 'http://localhost:3000'

    admin_email: str | None = None
    default_plan_code: str = 'starter'

    auth_rate_limit_per_minute: int = 10

    chat_rate_limit_per_minute_user: int = 20
    chat_rate_limit_per_minute_ip: int = 60

    openrouter_api_key: str = ''
    openrouter_base_url: str = 'https://openrouter.ai/api/v1'
    openrouter_http_referer: str = 'http://localhost'
    openrouter_app_title: str = 'OpenLLM MVP'

    @field_validator('backend_cors_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v:
            return [origin.strip() for origin in v.split(',')]
        return []

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == 'production'


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_database_url() -> str:
    return DatabaseSettings().database_url
