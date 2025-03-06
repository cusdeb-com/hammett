FROM python:3.13-alpine3.21

WORKDIR /var/www/admin_panel_bot

COPY ./admin_panel_bot .

RUN apk --update add git \
 && pip install -r requirements.txt \
 && apk del git

CMD env HAMMETT_SETTINGS_MODULE=settings python3 -m demo
