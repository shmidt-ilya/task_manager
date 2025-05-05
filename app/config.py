from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')
    
    # Database settings
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "taskman"
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algo: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
