from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    test_database_name: str
    admin_email: str
    admin_password: str

    jwt_secret_key: str
    jwt_algorythm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
