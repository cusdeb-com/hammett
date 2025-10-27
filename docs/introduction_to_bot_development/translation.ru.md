В Hammett реализована поддержка файлов переводов. Для ее использования в `settings.py` нужно добавить атрибут `LOCALE_PATHS`. Это список содержащий пути к директориям, в которых находятся директории с файлами переводов.

Структура может быть следующая для поддержки английского, португальского и русского языков:

{% include-markdown 'examples/translation/translation_files_structure.md' %}

А параметр конфигурации `LOCALE_PATHS` будет выглядеть так:

{% include-markdown 'examples/translation/locale_path_setting.md' %}

Ниже приведен пример содержимого файла `hammett.po` для английского языка:

{% include-markdown 'examples/translation/translation_file_content.md' %}

Обратите внимание на `msgstr`. В Hammett это называется _текстовкой_ (caption). Она содержит текст на нужном языке. У каждой текстовки есть `msgid` — ключ, по которому можно ее получить.

Затем на основе `.po` файлов нужно создать `.mo` файлы для каждого языка. Для этого можно воспользоваться следующей командой:

{% include-markdown 'examples/translation/creating_mo_file_command.md' %}

На этом этапе подготовка завершена, и можно приступать к использованию файлов переводов в боте. Для этого импортируйте функцию [`gettext`](../api_reference/utils/translation.md#hammett.utils.translation.gettext) из модуля [`hammett.utils.translation`](../api_reference/utils/translation.md) и передайте ей ключ текстовки и код текущего языка. Ниже приведен пример для перевода текста кнопки:

{% include-markdown 'examples/translation/gettext_usage.md' %}

> **Примечание**: если не передавать код языка явно, то будет использоваться указанный в параметре конфигурации `LANGUAGE_CODE`. По умолчанию он равен `'en'`.

См. live-пример бота [HammettQuizBot](https://t.me/HammettQuizBot) с демонстрацией работы этого функционала.
