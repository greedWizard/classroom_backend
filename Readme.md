# Репозиторий с исходным кодом бэк-энда classroom

## Стэк

### Основа

python3.9+

FastAPI - https://fastapi.tiangolo.com/ (Основной веб фреймворк)

SQLAlchemy (asyncpg) - https://www.sqlalchemy.org/ (ORM)

pydantic - https://pydantic-docs.helpmanual.io/ (Сериализация, схемы)

alembic - https://alembic.sqlalchemy.org/en/latest/ (Миграции)

### Тестирование

pytest - https://docs.pytest.org/en/6.2.x/contents.html (Основной фреймворк для тестов)

faker - https://zetcode.com/python/faker/ (Фейковые данные)

Актуальные версии всех библиотек указаны в requirements.txt

## Развернуть проект

### Локально

0. Заранее создать базу в PostgreSQL и прописать данные с пользователем, самой бд и портами в
```src/core/config/.env``` примеры можно брать из ```.envexample``` в той же директории.

1. Установить виртуальное окружение

* ```sudo apt-get update && sudo apt-get -y upgrade```

* ```sudo-apt-get install -y python3-venv```

* ```poetry install```

* (Желательно) Прогнать тесты, убедиться что всё работает: ```poetry run pytest```

* Если всё нормально ```poetry run auvicorn app:app --reload```

### В докере
0. Выполнить шаг 0 в локальной настройке, только в отдельном контейнере постгреса.

* ```sudo apt-get update && sudo apt-get -y upgrade```
* ```sudo-apt-get install docker docker-compose```
* ```docker run --rm -ti -p 8000:8000 --name classroom classroom/classroom_back:latest```

## Миграции

### Локально

* С установленными пакетами и активированным виртуальным окружением:
(После изменений в моделях) ``` alembic revision --autogenerate -m <Имя миграции, например "добавлено поле email"> ```

* После предыдущего пункта: ```alembic upgrade head```

### В докере

* Повторить предыдущий шаг через ```docker exec -it classroom-back <команда>```

# TODO:

* Репозитории должны инжектится в сервисы через DI.
* Логирование, возможно подключить сентри
* Pre-commit: Black и isort сильно конфликтуют, длинная строка с одним импортом не даёт сделать коммит
* Создавать диалог может только ученик с преподавателем, надо запрещать всем подряд начинать диалоги с кем попало
* Переделать чат на вебсокетах? Слишком большое количество подключений одновременно не убьёт сервер?
* Проверить везде DI, не создавать нигде объекты вручную (возможно только тесты)
* Почистить ненужные методы в сервисах и моделях
* релогинить при смене имейла и запрашивать активацию по новой (срочно)
