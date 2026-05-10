# Сайт объявлений — REST API на aiohttp

CRUD-API для объявлений. Хранилище — SQLite (через `aiosqlite` + SQLAlchemy 2.0 async). Валидация входа — Pydantic.

## Поля объявления

- `id` — идентификатор (генерируется БД)
- `title` — заголовок
- `description` — описание
- `owner` — владелец
- `created_at` — дата создания (ставится БД автоматически)

## Установка и запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Сервер слушает `http://localhost:8080`. SQLite-файл `ads.db` создаётся при старте.

## Эндпоинты

| Метод | URL | Описание |
| --- | --- | --- |
| GET | `/ads` | Список всех объявлений |
| GET | `/ads/{id}` | Получить одно объявление |
| POST | `/ads` | Создать объявление |
| PATCH | `/ads/{id}` | Изменить поля объявления |
| DELETE | `/ads/{id}` | Удалить объявление |

### Примеры

```bash
# создать
curl -X POST http://localhost:8080/ads \
  -H 'Content-Type: application/json' \
  -d '{"title":"Велосипед","description":"Почти новый","owner":"ivan"}'

# список
curl http://localhost:8080/ads

# получить одно
curl http://localhost:8080/ads/1

# обновить (любое подмножество title/description/owner)
curl -X PATCH http://localhost:8080/ads/1 \
  -H 'Content-Type: application/json' \
  -d '{"title":"Велосипед красный"}'

# удалить
curl -X DELETE http://localhost:8080/ads/1
```

## Структура проекта

- [main.py](main.py) — приложение aiohttp, роуты и обработчики
- [models.py](models.py) — модель `Advertisement`, движок и сессии SQLAlchemy
- [schema.py](schema.py) — Pydantic-схемы для валидации входа
- [requirements.txt](requirements.txt) — зависимости
