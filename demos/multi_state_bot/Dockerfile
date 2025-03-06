FROM python:3.13-alpine3.21

WORKDIR /var/www/multi_state_bot

COPY ./multi_state_bot .

RUN apk --update add git \
 && pip install -r requirements.txt \
 && apk del git

CMD env HAMMETT_SETTINGS_MODULE=settings python3 -m demo
