from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_hostname: str
    database_port: str = str(5432)
    database_name: str
    database_username: str
    database_password: SecretStr
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int


settings = Settings()  # type: ignore
