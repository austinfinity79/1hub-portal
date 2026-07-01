from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # NAPAS APG — sandbox endpoints
    NAPAS_BASE_URL: str = "https://apg-stg.napas.com.vn"
    NAPAS_SIMULATOR_URL: str = "https://apg-stg.napas.com.vn/bankdemo/app"
    NAPAS_CLIENT_TYPE: str = "mock"

    # NAPAS APG — security
    NAPAS_PRIVATE_KEY_PATH: str = ""        # PEM private key (.key) — sinh bằng OpenSSL, KHÔNG commit
    NAPAS_CERT_PATH: str = ""               # Cert (.cer/.pem) NAPAS ký trả về — dùng verify chữ ký NAPAS
    NAPAS_ALLOWED_IPS: str = "103.9.4.46"   # IP NAPAS push notify (comma-separated, thêm IP prod DC+DR)

    # NAPAS APG — credentials (chờ NAPAS cấp)
    # TODO[NAPAS-A2]: senderId / receiverId của 1Hub
    NAPAS_SENDER_ID: str = ""
    NAPAS_RECEIVER_ID: str = ""
    # TODO[NAPAS-A3]: OAuth2 client credentials
    NAPAS_CLIENT_ID: str = ""
    NAPAS_CLIENT_SECRET: str = ""
    NAPAS_TOKEN_URL: str = ""               # OAuth2 token endpoint

    # Legacy — giữ cho mock client tương thích
    NAPAS_API_URL: str = "http://mock-napas.local"
    NAPAS_KEY_PATH: str = "./keys/napas_mock.pem"

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
    def napas_allowed_ip_set(self) -> set[str]:
        return {ip.strip() for ip in self.NAPAS_ALLOWED_IPS.split(",") if ip.strip()}

    @property
    def napas_notification_url(self) -> str:
        return f"{self.NAPAS_BASE_URL}/apg/notification"

    @property
    def napas_investigation_url(self) -> str:
        return f"{self.NAPAS_BASE_URL}/apg/investigation"

    @property
    def napas_reconciliation_url(self) -> str:
        return f"{self.NAPAS_BASE_URL}/apg/reconciliation"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @classmethod
    def is_production(cls) -> bool:
        return Settings().ENV == "prod"


settings = Settings()
