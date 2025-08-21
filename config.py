from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 * 2
    MAX_CONTENT_LENGTH = 1024 * 1024 * 24
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    PORT = os.getenv("PORT", 5000)
    DEBUG = os.getenv("DEBUG", False)