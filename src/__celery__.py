from celery import Celery
from config import Config

def make_celery():
    return Celery(
        "sardine",
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND
    )

celery = make_celery()