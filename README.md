# NavbatGir

## Насб дар сервер

Сервер бояд Python 3.12 ё навтар дошта бошад.

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn server.wsgi:application --bind 0.0.0.0:$PORT
```

Пеш аз оғози сервер ин environment variable-ҳоро танзим кунед:

- `DJANGO_SECRET_KEY` — калиди махфии нав ва қавӣ.
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` — номи домен, масалан `navbatgir.example.com`.
- `DJANGO_CSRF_TRUSTED_ORIGINS` — суроғаи пурра бо HTTPS, масалан `https://navbatgir.example.com`.
- `DJANGO_SECURE_SSL_REDIRECT=True` — танҳо вақте фаъол кунед, ки сервер HTTPS-ро дуруст таъмин мекунад.
- `DJANGO_SECURE_HSTS_SECONDS=31536000` — танҳо баъд аз тасдиқи пурраи HTTPS фаъол кунед.

База ҳоло SQLite аст. Дар сервере, ки файлҳои локалиро пок мекунад ё чанд instance дорад, SQLite ва `db.sqlite3` кофӣ нестанд; базаи беруна ва танзими `DATABASES` лозим мешавад. `db.sqlite3`-ро ҳамчун базаи development ба git ё сервер бор накунед.

## Санҷиши танзимоти амниятӣ

Пас аз гузоштани домен ва environment variable-ҳо:

```bash
python manage.py check --deploy
```

Migration-ҳои кӯҳна нигоҳ дошта шудаанд, чун онҳо барои таърихи schema заруранд.
