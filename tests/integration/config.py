from functools import lru_cache

from app.core.config import Settings

class TestsSettings(Settings):
    def __init__(self) -> None:
        super().__init__()

    TEST_DATABASE_URL: str
    TEST_REDIS_URL: str

@lru_cache()
def get_tests_settings() -> TestsSettings:
    return TestsSettings()
