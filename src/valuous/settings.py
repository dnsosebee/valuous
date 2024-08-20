from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    github_token: str
    anthropic_api_key: str
    # telegram_bot_token: str
    # google_valuous_app_credentials: str
    # google_service_account_credentials: str

    model_config = ConfigDict(
        env_file=".env",
    )


settings = Settings()
