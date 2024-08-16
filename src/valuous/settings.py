from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    github_token: str
    google_credentials_base64: str = None

    class Config:
        env_file = ".env"


settings = Settings()
