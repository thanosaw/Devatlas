from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # GitHub webhook secret for verifying webhook requests
    GITHUB_WEBHOOK_SECRET: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    
    # GitHub API credentials for making authenticated requests
    GITHUB_API_TOKEN: str = ""
    
    # Path to store processed GitHub webhook events
    ACTIONS_FILE_PATH: str = "actions.json"
    
    # Optional logging level
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        
settings = Settings()

# For debugging only - will show that secrets were loaded correctly
# Remove this in production!
# print(f"Loaded GitHub webhook secret: {'*' * len(GITHUB_WEBHOOK_SECRET)} (hidden for security)")
# print(f"GitHub API token loaded: {bool(settings.GITHUB_API_TOKEN)}")
# print(f"Actions file path: {settings.ACTIONS_FILE_PATH}")