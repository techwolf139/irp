from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/irp"
    redis_url: str = "redis://localhost:6379/0"
    pms_api_url: str = "http://localhost:8001"
    oms_api_url: str = "http://localhost:8002"
    srm_api_url: str = "http://localhost:8003"
    sync_interval_seconds: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
