import os

class Settings:
    PROJECT_NAME: str = "gym-reservation-api"
    ALLOWED_ORIGINS: list = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000,http://127.0.0.1:3000"
        ).split(",")
    ]

settings = Settings()


