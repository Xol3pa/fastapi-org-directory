# Org Directory API

Асинхронный FastAPI‑сервис со справочником организаций, зданий и видов деятельности.

## Быстрый старт
1. `cp .env.example .env`
2. (опционально) поправьте значения `APP_DATABASE__ASYNC_URL`, `APP_DATABASE__SYNC_URL`, `APP_API_KEY`.
3. `docker-compose up --build`

API доступно на `http://localhost:8000`, документация — `/docs`. Все запросы требуют заголовок `X-API-Key`.

## Локально (без Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```

Готово.
