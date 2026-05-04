from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # VK API
    vk_access_token: str = ""
    vk_api_version: str = "5.199"
    vk_group_screen_name: str = "er_ru"

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "vk_dashboard"
    db_user: str = "vk_dashboard"
    db_password: str = "vk_dashboard_pass"

    # Parser
    parser_lookback_days: int = 14
    parser_interval_minutes: int = 30

    # Dashboard
    dash_host: str = "0.0.0.0"
    dash_port: int = 8050
    dash_debug: bool = True

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def db_url_sync(self) -> str:
        return self.db_url


settings = Settings()
