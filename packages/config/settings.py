from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str
    port: int
    log_level: str
    ollama_base_url: str
    llm_model: str
    embedding_model: str
    secret_key :str
    database_url:str
    qdrant_url: str = "http://localhost:6333"
    access_token_expire_minutes: int
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()   