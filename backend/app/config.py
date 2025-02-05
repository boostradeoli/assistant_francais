import os

class Settings:
    PROJECT_NAME: str = "AI Email Assistant"
    ENV: str = os.getenv("ENV", "development")
    # Add other configuration variables as needed, for example:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    # Email settings, paths, etc.
    EMAIL_API_URL: str = os.getenv("EMAIL_API_URL", "https://api.emailprovider.com")
    DEBUG: bool = ENV == "development"

settings = Settings()
