# Начало работы

Здесь описываются первые шаги, которые необходимо пройти для того, чтобы перейти к комфортному чтению [Введения в разработку ботов](introduction_to_bot_development/three-pillars.md).

## Установка

Перед тем как начать установку Hammett, убедитесь, что вы используете **Python 3.10** или выше. Для этого можно выполнить `python3` в терминале. Вывод должен быть примерно следующим:

{% include-markdown 'examples/python_session.md' %}

Затем создайте виртуальное окружение и активируйте его:

{% include-markdown 'examples/environment_creation_command.md' %}

{% include-markdown 'examples/environment_activation_command.md' %}

И, наконец, установите Hammett:

{% include-markdown 'examples/installation_command.md' %}

## Пример простого бота

Создайте два модуля: `bot.py` и `settings.py`

{% include-markdown 'examples/bot.md' %}

{% include-markdown 'examples/settings.md' %}

Запустите бота следующей командой:

{% include-markdown 'examples/running_bot_command.md' %}
