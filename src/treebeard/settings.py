from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="treebeard_")

    sqlite_database_path: Path = Field()

    root_path: Path = Path(__file__).parent.resolve()
    session_key: str | None = Field(min_length=20, default=None)

    development_mode: bool = Field(default=False)

    groq_api_key: str
    groq_model: str
    groq_max_tokens_per_user: int = Field(default=50_000)

    google_oauth: bool = Field(default=False)
    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)

    github_oauth: bool = Field(default=False)
    github_client_id: str | None = Field(default=None)
    github_client_secret: str | None = Field(default=None)

    authorization: bool = Field(default=False)


SETTINGS = __Settings()  # type: ignore

if SETTINGS.google_oauth:
    if not (SETTINGS.google_client_id and SETTINGS.google_client_secret):
        raise ValueError("Missing Google OAuth environment variables!")

if SETTINGS.github_oauth:
    if not (SETTINGS.github_client_id and SETTINGS.github_client_secret):
        raise ValueError("Missing Github OAuth environment variables!")

if SETTINGS.github_oauth or SETTINGS.google_oauth:
    SETTINGS.authorization = True

if SETTINGS.authorization and not SETTINGS.session_key:
    raise ValueError("Missing session key environment variable!")
