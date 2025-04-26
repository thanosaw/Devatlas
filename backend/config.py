from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    GITHUB_WEBHOOK_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        
settings = Settings()

# For debugging only - will show that secret was loaded correctly
# Remove this in production!
print(f"Loaded GitHub webhook secret: {'*' * len(settings.GITHUB_WEBHOOK_SECRET)} (hidden for security)")
print(f"Secret loaded: {bool(settings.GITHUB_WEBHOOK_SECRET)}")