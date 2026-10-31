from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class DatabaseSettings(Settings):
    def __init__(self) -> None:
        super().__init__()
    DATABASE_URL: str

class RedisSettings(Settings):
    def __init__(self) -> None:
        super().__init__()
    REDIS_URL: str

class SecuritySettings(Settings):
    def __init__(self) -> None:
        super().__init__()
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRE_MINUTES: int
    BCRYPT_SALT_ROUNDS: int

@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()

@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()

@lru_cache()
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()
