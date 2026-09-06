from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CommercePilot"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    # Postgres (Neon)
    DATABASE_URL: str = ""

    # Auth
    JWT_SECRET: str = ""
    JWT_EXPIRE_DAYS: int = 7
    GOOGLE_CLIENT_ID: str = ""

    # Shopify (client-credentials grant; access token is minted on demand)
    SHOPIFY_SHOP_DOMAIN: str = ""
    SHOPIFY_CLIENT_ID: str = ""
    SHOPIFY_CLIENT_SECRET: str = ""

    # CALL-E
    CALLE_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()