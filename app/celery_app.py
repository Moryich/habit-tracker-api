from celery import Celery
from celery.schedules import crontab

from app.core.config import config

celery_app = Celery(broker=f"{config.REDIS_URL}/0")

celery_app.autodiscover_tasks(["app"])

celery_app.conf.update(
    timezone = "Europe/Kyiv",
    beat_schedule = {
        "weekly-reset": {
            "task": "app.tasks.weekly_reset",
            "schedule": crontab(day_of_week=1, hour=0, minute=0)
        }
    }
)
