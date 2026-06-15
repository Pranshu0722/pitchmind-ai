from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "local"
    app_secret_key: SecretStr = Field(default="change-me-32-chars-min!!!!!!!!")
    app_debug: bool = False
    app_log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["http://localhost:5173"]

    # Database
    database_url: str = "postgresql+asyncpg://pitchmind:pitchmind_dev_pw@localhost:5432/pitchmind"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Object Storage
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: SecretStr = Field(default="minioadmin")
    s3_bucket_name: str = "pitchmind"
    s3_region: str = "us-east-1"

    # Auth
    jwt_secret_key: SecretStr = Field(default="change-me-jwt-secret")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # LLM
    gemini_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    ollama_base_url: str = "http://localhost:11434"
    llm_routing_provider: str = "gemini"
    llm_routing_model: str = "gemini-2.0-flash"
    llm_synthesis_provider: str = "anthropic"
    llm_synthesis_model: str = "claude-sonnet-4-6"
    llm_budget_cents_per_run: int = 50

    # CV
    cv_device: str = "cpu"
    cv_yolo_model: str = "yolov11n.pt"
    cv_detection_fps: int = 5
    cv_batch_size: int = 16

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "pitchmind"

    # Model server
    model_server_url: str = "http://localhost:8001"

    # Observability
    sentry_dsn: str | None = None
    otel_exporter_otlp_endpoint: str | None = None

    # Rate limiting
    rate_limit_default: str = "60/minute"
    rate_limit_upload: str = "10/hour"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"


settings = Settings()
