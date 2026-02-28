from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    llama_cloud_api_key: str

    model_config = SettingsConfigDict(
        env_file="../.env", extra="ignore", case_sensitive=False
    )


settings = Settings()
