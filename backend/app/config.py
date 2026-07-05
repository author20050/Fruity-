from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/tonydynamic"
    
    # JWT
    secret_key: str = "your-super-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Paystack
    paystack_public_key: str = "pk_test_xxxx"
    paystack_secret_key: str = "sk_test_xxxx"
    paystack_api_url: str = "https://api.paystack.co"
    
    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # App
    app_title: str = "Tony Dynamic"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
