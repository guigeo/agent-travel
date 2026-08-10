from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    max_tool_iters: int = 6
    session_ttl_seconds: int = 3600


settings = Settings()
