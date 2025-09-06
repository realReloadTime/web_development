from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = "secret_key_12345"
    REFRESH_SECRET_KEY: str = "refresh_secret_key_12345"
    ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = getenv('DATABASE_URL')
    VERSION: str = "1.1.0"
    DOMAIN: str = "localhost:8000"
