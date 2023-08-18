Для того чтобы изменить значения настроек по умолчанию, создайте конфигурационный файл `settings.py`. Это обычный Python-модуль с _переменными на уровне модуля_ (module-level variables). Hammett ищет этот файл, используя путь, который указан в переменной окружения `HAMMETT_SETTINGS_MODULE`. Она является обязательной для запуска бота (см. [Сборка бота и запуск](assemble-and-run-bot.md)).

> **Примечание**: модуль `settings.py` был вдохновлен одноименным модулем из Django. Большинство настроек перенесены именно [оттуда](https://docs.djangoproject.com/en/5.1/topics/settings/), поэтому если вы сталкивались в своей работе с Django, то `settings.py` вам покажется знакомым.

Чтобы иметь доступ к настройкам из `settings.py` в других модулях, импортируйте его следующим образом:

{% include-markdown 'examples/settings/correct_importing.md' %}

`settings` является "ленивым" объектом, и вы не сможете импортировать из него настройки выборочно. Вот как делать **не следует**:

{% include-markdown 'examples/settings/incorrect_importing.md' %}

Также важно отметить, что ваш код не должен ничего импортировать из модуля [`global_settings.py`](../api_reference/conf/global_settings.md) или вашего модуля `settings.py`. Дело в том, что `hammett.conf.settings` представляет собой _единый интерфейс_ (single interface), а также отделяет настройки проекта от остального кода.

В вашем `settings.py` должен быть как минимум атрибут `TOKEN`. В противном случае будет выброшено исключение [`ImproperlyConfigured`](../api_reference/core/exceptions.md#hammett.core.exceptions.ImproperlyConfigured).
