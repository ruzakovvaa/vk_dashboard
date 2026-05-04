# VK Dashboard — Анализ аудитории «ЕДИНАЯ РОССИЯ»

Дашборд для анализа активности аудитории сообщества ВКонтакте на основе данных VK API.

## Быстрый старт (5 команд)

```bash
# 1. Поднять PostgreSQL
docker-compose up -d

# 2. Установить зависимости
pip install -e ".[dev]"

# 3. Применить миграции и создать views
alembic upgrade head
python scripts/init_db.py

# 4. Первичный парсинг (последние 14 дней)
python -m src.parser.vk_parser --lookback-days 14

# 5. Запустить дашборд
python -m src.dashboard.app
```

Дашборд доступен на http://localhost:8050

## Конфигурация

Скопируйте `.env.example` в `.env` и заполните:
- `VK_ACCESS_TOKEN` — сервисный токен из [vk.com/dev](https://vk.com/dev)
- `DB_PASSWORD` — пароль PostgreSQL

## Структура проекта

```
vk_dashboard/
├── src/
│   ├── config.py           # pydantic-settings конфиг
│   ├── db/
│   │   ├── engine.py       # SQLAlchemy engine
│   │   ├── models.py       # ORM-модели
│   │   └── views.sql       # DDL для всех представлений
│   ├── parser/
│   │   ├── vk_client.py    # Обёртка над VK API
│   │   ├── vk_parser.py    # Основной скрипт парсинга
│   │   └── schemas.py      # Pydantic-схемы ответов VK
│   ├── metrics/            # Калькуляторы метрик
│   └── dashboard/          # Dash-приложение
├── scripts/
│   ├── init_db.py          # Создание схемы и views
│   └── manual_fetch.py     # Ручной парсинг для отладки
├── tests/
│   ├── test_metrics.py
│   └── test_parser.py
└── alembic/                # Миграции БД
```

## Метрики

| Метрика | Формула | Описание |
|---------|---------|----------|
| ERpost | R/n × 100% | Вовлечённость на публикацию |
| ERday | R_day/n × 100% | Вовлечённость за день |
| ERview | R/V × 100% | Вовлечённость по просмотрам |
| Love Rate | Σlikes/(N×n) × 100% | Доля лайков |
| Talk Rate | Σcomments/(N×n) × 100% | Доля комментариев |
| VRpost | ΣV/(N×n) × 100% | Видимость публикаций |
| VRday | ΣV/(n×d) × 100% | Среднедневная видимость |

где R = лайки + комментарии + репосты, n = подписчики, N = кол-во постов, V = просмотры, d = дней.

## Страницы дашборда

### Обзор (`/`)
- KPI-карточки: просмотры, реакции, комментарии, репосты, публикации
- Коэффициенты вовлечённости: ERpost, ERday, ERview, Love Rate, Talk Rate, VRpost, VRday
- График динамики ERday по дням

### Статистика (`/statistics`)
- Тепловая карта просмотров (день недели × час)
- ERcontent по типам контента (фото, видео, текст, ссылка)
- Топ-10 публикаций по ERpost
