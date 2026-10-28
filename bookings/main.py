"""Сервис бронирований: создание бронирования и список бронирований для администратора."""
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# Параметры приходят из переменных окружения (см. docker-compose.yml)
DB = dict(
    host=os.getenv("DB_HOST", "db"),
    dbname=os.getenv("DB_NAME", "tourbook"),
    user=os.getenv("DB_USER", "tourbook"),
    password=os.getenv("DB_PASSWORD", "tourbook_pass"),
    connect_timeout=5,
)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Swagger UI: /api/bookings/docs
app = FastAPI(title="Сервис бронирований", docs_url="/api/bookings/docs",
              openapi_url="/api/bookings/openapi.json", redoc_url=None)


class BookingIn(BaseModel):
    tour_id: int
    customer_name: str = Field(min_length=1, max_length=100)
    people: int = Field(ge=1)


def query(sql, params=()):
    """Выполняет SQL-запрос; для SELECT возвращает список строк."""
    conn = psycopg2.connect(**DB)
    try:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall() if cur.description else None
    finally:
        conn.close()


@app.post("/api/bookings", status_code=201)
def create_booking(data: BookingIn):
    if not query("SELECT 1 FROM tours WHERE id = %s", (data.tour_id,)):
        raise HTTPException(status_code=404, detail="Тур не найден")
    query(
        "INSERT INTO bookings (tour_id, customer_name, people) VALUES (%s, %s, %s)",
        (data.tour_id, data.customer_name, data.people),
    )
    return {"status": "ok"}


@app.get("/api/bookings")
def list_bookings(x_admin_password: str | None = Header(default=None)):
    """Список бронирований. Нужен заголовок X-Admin-Password."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверный пароль администратора")
    return query(
        "SELECT b.id, t.title, b.customer_name, b.people "
        "FROM bookings b JOIN tours t ON t.id = b.tour_id ORDER BY b.id DESC"
    )
