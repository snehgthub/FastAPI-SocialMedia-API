from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, validator
import os


def load_secret(secret_name: str) -> SecretStr:
    # Try to load from the systemd secure directory first
    credentials_dir = os.getenv("CREDENTIALS_DIRECTORY")
    if credentials_dir:
        secret_file_path = os.path.join(credentials_dir, secret_name)
        with open(secret_file_path, "r") as file:
            secret_value = file.read().strip()
        return SecretStr(secret_value)
    else:
        # Fallback to loading from environment variables
        return SecretStr(os.getenv(secret_name.upper(), ""))


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

    @classmethod
    @validator("*")
    def load_secrets_if_needed(cls, v, values):
        for field_name, field in cls.__fields__.items():
            if field.type_ is SecretStr and field_name in values:
                values[field_name] = load_secret(field_name)
        return v


settings = Settings()  # type: ignore
