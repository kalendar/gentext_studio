from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="treebeard_")

    sqlite_database_path: Path = Field()

    root_path: Path = Path(__file__).parent.resolve()


SETTINGS = __Settings()  # type: ignore
