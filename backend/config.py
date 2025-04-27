from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Server settings
    PORT: int = int(os.getenv("PORT", 8000))

    # Slack settings
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")  # Added for Socket Mode
    
    # GitHub settings
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Neo4j settings
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # API Keys for AI services
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    AS1_API_KEY: Optional[str] = None

    # Alternative lowercase versions to match possible environment variables
    gemini_api_key: Optional[str] = None
    as1_api_key: Optional[str] = None

    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# For debugging only - will show that secrets were loaded correctly
# Remove this in production!
print(f"Loaded GitHub webhook secret: {'*' * len(settings.GITHUB_WEBHOOK_SECRET)} (hidden for security)")
print(f"GitHub secret loaded: {bool(settings.GITHUB_WEBHOOK_SECRET)}")
print(f"Slack bot token loaded: {bool(settings.SLACK_BOT_TOKEN)}")
print(f"Slack signing secret loaded: {bool(settings.SLACK_SIGNING_SECRET)}")
print(f"Slack app token loaded: {bool(settings.SLACK_APP_TOKEN)}")