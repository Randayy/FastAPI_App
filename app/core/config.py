from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str
    port: int
    debug: bool = False

    redis_host: str
    redis_port: int

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    class Config:
        env_file = ".env"
