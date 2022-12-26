FILE=/etc/letsencrypt/live/bezpart.ru/privkey.pem

if test -f "$FILE"; then
    poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload --ssl-keyfile /etc/letsencrypt/live/bezpart.ru/privkey.pem --ssl-certfile /etc/letsencrypt/live/bezpart.ru/fullchain.pem
else
    poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
fi
