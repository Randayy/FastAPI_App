from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str
    port: int
    debug: bool = False

    class Config:
        env_file = ".env"
