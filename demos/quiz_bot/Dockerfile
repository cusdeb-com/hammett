FROM python:3.13-alpine3.21

WORKDIR /var/www/quiz_bot

COPY ./quiz_bot .

RUN apk --update add git gettext \
 && pip install -r requirements.txt \
 && apk del git \
 \
 && msgfmt locale/en/LC_MESSAGES/hammett.po -o locale/en/LC_MESSAGES/hammett.mo \
 && msgfmt locale/pt-br/LC_MESSAGES/hammett.po -o locale/pt-br/LC_MESSAGES/hammett.mo \
 && msgfmt locale/ru/LC_MESSAGES/hammett.po -o locale/ru/LC_MESSAGES/hammett.mo

CMD env HAMMETT_SETTINGS_MODULE=settings python3 -m demo
