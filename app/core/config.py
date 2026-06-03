from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "farfor-recommend"
    database_url: str = "sqlite:///./farfor.db"
    environment: str = "development"
    ml_model_dir: str = "app/ml/rag_order_model_custom"
    ml_enabled: bool = True

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
