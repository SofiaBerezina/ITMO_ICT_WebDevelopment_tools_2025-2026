import os

import psycopg2
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/time_manager_db",
)

app = FastAPI()


class ParseRequest(BaseModel):
    url: HttpUrl


@app.post("/parse")
def parse(payload: ParseRequest):
    url = str(payload.url)

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else "No title"

    conn = psycopg2.connect(DATABASE_URL)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM priority WHERE name = 'medium'")
        priority_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM status WHERE name = 'pending'")
        status_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM tasktype WHERE name = 'work'")
        task_type_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM \"user\" WHERE username = 'parser'")
        user_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO task (
                title,
                description,
                estimated_hours,
                actual_hours,
                priority_id,
                status_id,
                task_type_id,
                user_id,
                created_at
            )
            VALUES (%s, %s, 0.0, 0.0, %s, %s, %s, %s, NOW())
            RETURNING id
            """,
            (
                f"Прочитать: {title_text[:50]}",
                f"Спарсено с {url}",
                priority_id,
                status_id,
                task_type_id,
                user_id,
            ),
        )
        task_id = cursor.fetchone()[0]
        conn.commit()
    finally:
        conn.close()

    return {
        "message": "Parsing completed",
        "url": url,
        "title": title_text,
        "task_id": task_id,
    }
