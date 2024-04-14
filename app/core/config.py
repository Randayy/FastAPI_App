from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

class Settings(BaseSettings):
    host: str
    port: int
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()