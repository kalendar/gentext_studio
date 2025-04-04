from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="treebeard_")

    sqlite_database_path: Path = Field()

    root_path: Path = Path(__file__).parent.resolve()
    groq_api_key: str
    groq_model: str

    session_key: str | None = Field(min_length=20, default=None)

    google_oauth: bool = Field(default=False)
    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)

    github_oauth: bool = Field(default=False)
    github_client_id: str | None = Field(default=None)
    github_client_secret: str | None = Field(default=None)


SETTINGS = __Settings()  # type: ignore
