from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    anthropic_api_key: str
    anthropic_model: str
    database_url: str

settings = Settings()               # created once, when the module is imported