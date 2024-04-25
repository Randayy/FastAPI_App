from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

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

    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int 

    auth0_secret_key: str
    auth0_algorithm: str
    auth0_domain: str
    auth0_issuer: str
    auth0_audience: str

    class Config:
        env_file = ".env"
