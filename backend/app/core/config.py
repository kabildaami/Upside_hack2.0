from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    db_port: int = 5432
    db_sslmode: str = 'prefer'
    sql_echo: bool = False
    jwt_secret: str = Field(min_length=32)  # required; generate with secrets.token_urlsafe(48)
    jwt_issuer: str = 'upside-school'
    access_token_minutes: int = 30
    frontend_origin: str = 'http://localhost:5173'

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / '.env'), env_file_encoding='utf-8', extra='ignore', case_sensitive=False)

    @property
    def database_url(self) -> URL:
        return URL.create('postgresql+psycopg', username=self.db_user, password=self.db_password,
                          host=self.db_host, port=self.db_port, database=self.db_name,
                          query={'sslmode': self.db_sslmode})

@lru_cache

def get_settings() -> Settings:
    return Settings()
