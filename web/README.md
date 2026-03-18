# Hospital Web (Django)

Веб‑версия проекта из корня репозитория (Telegram‑бот → сайт).

## Быстрый старт (локально, без Docker)

```powershell
cd web
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python hospital_web\manage.py migrate
.\.venv\Scripts\python hospital_web\manage.py createsuperuser
.\.venv\Scripts\python hospital_web\manage.py runserver
```

UI: `http://127.0.0.1:8000/`  
Admin: `http://127.0.0.1:8000/admin/`

Импорт данных из старой SQLite:

```powershell
.\.venv\Scripts\python hospital_web\manage.py import_legacy_sqlite
```

## Docker (Postgres + Redis + Celery)

1) В `web/` создайте `.env` на базе `.env.example`.\n\n2) Запуск:

```bash
docker compose up --build
```

Сайт: `http://localhost:8000/`\n\nCelery:\n- `worker` выполняет фоновые задачи (уведомления, отчёты)\n- `beat` запускает периодический скан уведомлений (каждую минуту)\n\n## HTTPS в облаке (Caddy)

```bash
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up --build
```

В `.env` задайте `DOMAIN=your-domain.com` и корректные `ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS`.

## API (DRF)

- `GET /api/appointments/`\n- `POST /api/appointments/`\n- `POST /api/appointments/{id}/extend` (body: `{ \"extra_minutes\": 15 }`)\n- `POST /api/appointments/{id}/finish`\n- `GET /api/rooms/monitor/?date=YYYY-MM-DD`\n- `GET /api/rooms/available/?date=YYYY-MM-DD&time=HH:MM&duration_minutes=60`\n- `POST /api/reports/` (body: `{ \"kind\": \"doctor_month\", \"year\": 2026, \"month\": 3 }`)\n+- `GET /api/reports/` / `GET /api/reports/{id}/`\n+
