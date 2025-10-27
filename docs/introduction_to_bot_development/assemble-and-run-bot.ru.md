На протяжении всей документации приводились примеры тех или иных частей кода, которые демонстрировали принципы работы или какие-то возможности Hammett, но ни разу не приводился пример запуска бота. Настало время рассказать об этом.

Бот — это набор экранов с обработчиками, которые "склеиваются" в одно целое посредством объекта класса [`Bot`](../api_reference/core/bot.md#hammett.core.bot.Bot) из модуля [`hammett.core.bot`](../api_reference/core/bot.md). Его обязательными атрибутами являются `name` — имя бота и `entry_point` — точка входа — экран, который увидит пользователь в ответ на ввод команды `/start`. Одним из родительских классов этого экрана должен быть [`StartMixin`](../api_reference/core/mixins.md/#hammett.core.mixins.StartMixin), который находится в модуле [`hammett.core.mixins`](../api_reference/core/mixins.md) и расширяет базовый функционал экрана обработчиком [`start`](../api_reference/core/mixins.md/#hammett.core.mixins.StartMixin.start).

> **Примечание**: Hammett берет на себя регистрацию метода [`start`](../api_reference/core/mixins.md/#hammett.core.mixins.StartMixin.start), поэтому не нужно регистрировать его самостоятельно никаким из декораторов для регистрации обработчиков (см. [Регистрация обработчиков](states.md#регистрация-обработчиков)).

Ниже приведен пример инициализации и запуска бота с одним экраном:

{% include-markdown 'examples/assemble_and_run_bot/initializing_and_running_bot.md' %}

Ниже приведена команда для запуска бота с указанием переменной окружения `HAMMETT_SETTINGS_MODULE` (см. [Конфигурационный файл](settings.md)):

{% include-markdown 'examples/assemble_and_run_bot/setting_hammett_settings_module_in_cli.md' %}

**Важно**: если вы устанавливаете переменную окружения `HAMMETT_SETTINGS_MODULE` с помощью пакета `os` следующим образом:

{% include-markdown 'examples/assemble_and_run_bot/setting_hammett_settings_module_with_os.md' %}

то убедитесь, что это происходит до инициализации бота.
