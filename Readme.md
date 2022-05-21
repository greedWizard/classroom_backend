# Репозиторий с исходным кодом бэк-энда classroom

## Стэк

### Основа

python3.8+

FastAPI - https://fastapi.tiangolo.com/ (Основной веб фреймворк)

Tortoise-ORM - https://tortoise-orm.readthedocs.io/en/latest/examples/fastapi.html (Асинхронная ORM)

pydantic - https://pydantic-docs.helpmanual.io/ (Сериализация, схемы)

aerich - https://ashfakmeethal.medium.com/tortoise-orm-migrations-with-aerich-5ebb7238bed5 (Миграции, но к сожалению пока что очень сырая штука :( )

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

* ```python3 -m venv venv```

* ```source venv/bin/activate```

* ```pip3 install --upgrade pip```

* ```pip3 install -r requirements.txt```

2. Перейти в ```/src```

* (Желательно) Прогнать тесты, убедиться что всё работает: ```pytest```

* Если всё нормально, там же в папке ```/src``` - ```uvicorn app:app --reload```

### В докере
0. Выполнить шаг 0 в локальной настройке, только в отдельном контейнере постгреса.

* ```sudo apt-get update && sudo apt-get -y upgrade```
* ```sudo-apt-get install docker docker-compose```
* ```docker run --rm -ti -p 8000:8000 --name homework homework/homework_back:latest```

## Миграции

### Локально

* С установленными пакетами и активированным виртуальным окружением:
(После изменений в моделях) ``` aerich migrate --name <Имя миграции, например "добавлено поле email"> ```

* (Обязательно) Перепроверить правильность миграции в ```./migrations```

* После предыдущего пункта: ```aerich upgrade```

* (Если что-то пошло не так) ```aerich downgrade``` - откатывает миграции

### В докере

* ```docker ps``` - скопировать id контейнера с запущенным бэком. Повторить предыдущий шаг через ```docker exec -it {id контейнера} <команда>```
