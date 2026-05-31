import os

import requests
from celery import Celery


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")

celery_app = Celery("time_manager_parser", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(name="celery_app.parse_url_task")
def parse_url_task(url: str):
    response = requests.post(
        f"{PARSER_SERVICE_URL}/parse",
        json={"url": url},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
