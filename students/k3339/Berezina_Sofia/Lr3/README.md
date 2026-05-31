# Лабораторная работа 3

Проект упаковывает FastAPI-приложение, PostgreSQL, HTTP-сервис парсера, Redis и Celery worker в Docker Compose.

## Запуск

```bash
docker compose up --build
```

После запуска:

- основное API: http://localhost:8000/docs
- parser-service: http://localhost:8001/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Прямой вызов парсера через FastAPI

```bash
curl -X POST http://localhost:8000/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.python.org"}'
```

Основное приложение отправит HTTP-запрос в контейнер `parser`, parser-service скачает страницу, достанет `<title>` и сохранит новую задачу в PostgreSQL.

## Вызов парсера через Celery и Redis

```bash
curl -X POST http://localhost:8000/parser/parse-async \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.python.org"}'
```

Ответ содержит `task_id`.
