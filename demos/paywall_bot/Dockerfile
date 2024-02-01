FROM python:3.13-alpine3.20

WORKDIR /var/www/paywall_bot

COPY ./paywall_bot .

RUN apk --update add git \
 && pip install -r requirements.txt \
 && apk del git

CMD env HAMMETT_SETTINGS_MODULE=settings python3 -m demo
