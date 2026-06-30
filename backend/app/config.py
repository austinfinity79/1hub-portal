from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    NAPAS_API_URL: str = "http://mock-napas.local"
    NAPAS_KEY_PATH: str = "./keys/napas_mock.pem"
    NAPAS_CLIENT_TYPE: str = "mock"

    DB_URL: str = "sqlite:///./1hub.db"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    ENV: str = "dev"

    # Auth / JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Key encryption
    API_KEY_MASTER_SECRET: str = "change-me-api-key-secret"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @classmethod
    def is_production(cls) -> bool:
        return Settings().ENV == "prod"


settings = Settings()
