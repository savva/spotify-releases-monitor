from functools import lru_cache
from typing import List

from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Spotify Releases Monitor"
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_url: str = Field(default="http://localhost:5173", alias="APP_URL")
    api_url: str = Field(default="http://localhost:8000", alias="API_URL")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")
    jwt_ttl_min: int = Field(default=60 * 24, alias="JWT_TTL_MIN")
    spotify_client_id: str = Field(alias="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(alias="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: AnyHttpUrl = Field(alias="SPOTIFY_REDIRECT_URI")
    database_url: str = Field(alias="DATABASE_URL")
    cors_origins_raw: str | List[AnyHttpUrl] | None = Field(default=None, alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> List[str]:
        value = self.cors_origins_raw
        if value is None:
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return [str(url) for url in value]

    @property
    def spotify_scopes(self) -> List[str]:
        return [
            "user-read-email",
            "user-read-private",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-read-recently-played",
        ]

    @property
    def async_database_url(self) -> str:
        if "+psycopg" in self.database_url and "_async" not in self.database_url:
            return self.database_url.replace("+psycopg", "+psycopg_async", 1)
        return self.database_url

    @property
    def secure_cookies(self) -> bool:
        return self.app_env.lower() == "prod"


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
