"""Сервис туров: отдаёт список туров для карточек на сайте."""
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI

# Параметры подключения к БД приходят из переменных окружения (см. docker-compose.yml)
DB = dict(
    host=os.getenv("DB_HOST", "db"),
    dbname=os.getenv("DB_NAME", "tourbook"),
    user=os.getenv("DB_USER", "tourbook"),
    password=os.getenv("DB_PASSWORD", "tourbook_pass"),
    connect_timeout=5,
)

# Swagger UI: /api/tours/docs
app = FastAPI(title="Сервис туров", docs_url="/api/tours/docs",
              openapi_url="/api/tours/openapi.json", redoc_url=None)


@app.get("/api/tours")
def list_tours():
    conn = psycopg2.connect(**DB)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, title, description, price, emoji FROM tours ORDER BY id")
            return cur.fetchall()
    finally:
        conn.close()
