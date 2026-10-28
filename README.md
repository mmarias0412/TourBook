# TourBook: бронирование туров

Курсовая работа по дисциплине «Настройка и администрирование сервисного программного обеспечения», тема 72.

## Контейнеры (5)

| Контейнер | Технология | Что делает |
|-----------|------------|------------|
| proxy | nginx | единственная точка входа (порт 8080), направляет запросы на нужный контейнер |
| frontend | nginx | отдаёт страницу сайта (`index.html`) |
| tours | Python, FastAPI | отдаёт список туров |
| bookings | Python, FastAPI | создаёт бронирования, отдаёт их администратору |
| db | PostgreSQL | хранит туры и бронирования |

Сети: `public_net` (proxy, frontend, tours, bookings) и закрытая `data_net` (tours, bookings, db).

## Запуск

```
docker compose up -d --build
```
- сайт: http://localhost:8080 (пароль администратора: `admin123`)
- Swagger: http://localhost:8080/api/tours/docs и http://localhost:8080/api/bookings/docs
- остановить: `docker compose down` (с удалением данных: `docker compose down -v`)

## Кластер (Docker Swarm)

```
docker swarm init
docker compose build
docker stack deploy --resolve-image never -c docker-stack.yml tourbook
docker stack services tourbook
docker stack rm tourbook
```

## CI/CD

Файл `.github/workflows/ci-cd.yml`: при каждом push в `main` GitHub Actions собирает образы, запускает контейнеры, проверяет сайт и API (CI), затем разворачивает стек в Docker Swarm и проверяет его (CD).
