import os

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from celery_app import parse_url_task


PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")

router = APIRouter(prefix="/parser", tags=["parser"])


class ParseRequest(BaseModel):
    url: HttpUrl


@router.post("/parse")
def parse_via_http(payload: ParseRequest):
    try:
        response = requests.post(
            f"{PARSER_SERVICE_URL}/parse",
            json={"url": str(payload.url)},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return response.json()


@router.post("/parse-async")
def parse_via_queue(payload: ParseRequest):
    task = parse_url_task.delay(str(payload.url))
    return {
        "message": "Parsing task started",
        "task_id": task.id,
    }
