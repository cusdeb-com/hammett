Hammett предоставляет инструменты для изолированного тестирования экранов, виджетов и обработчиков без запуска реального экземпляра Telegram Bot API. Предлагаемая система тестирования основана на использовании класса [`BaseTestCase`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase) и предназначена для проверки логики, состояния контекста пользователя и финального рендера сообщений. Она позволяет разрабатывать тесты, полностью повторяющие поведение реального бота, но в контролируемой среде.

Основным элементом инфраструктуры тестирования является класс [`BaseTestCase`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase) из модуля [`hammett.test.base`](../api_reference/test/base.md). Он наследуется от стандартного класса unittest.TestCase и расширяет его дополнительными методами.

Для тестирования результата "рендера" используется декоратор [`catch_render_config`](../api_reference/test/utils.md/#hammett.test.utils.catch_render_config) из модуля [`hammett.test.utils`](../api_reference/test/utils.md). Этот декоратор перехватывает итоговую конфигурацию рендера после выполнения обработчика и сохраняет ее во втором аргументе теста — `actual`. До вызова какого-либо обработчика в теле этого теста его значение будет равно `None`, а после вызова (например, `await TestScreen().jump(self.update, self.context)`) станет доступным объект [`FinalRenderConfig`](../api_reference/core/constants.md/#hammett.core.constants.FinalRenderConfig) через `actual.final_render_config`. Именно с этим объектом будет происходить сравнение ожидаемого и реального [`FinalRenderConfig`](../api_reference/core/constants.md/#hammett.core.constants.FinalRenderConfig). Для проверки содержимого результата применяется функция [`assertFinalRenderConfigEqual`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.assertFinalRenderConfigEqual), которая сравнивает зафиксированный рендер с ожидаемым по параметрам.

> **Примечание**: [`FinalRenderConfig`](../api_reference/core/constants.md/#hammett.core.constants.FinalRenderConfig) это дополненный статическими и вызываемыми (в соответствии с приоритетами отрисовки) атрибутами экрана [`RenderConfig`](../api_reference/core/constants.md/#hammett.core.constants.RenderConfig), который фактически передается внутренним методам отрисовки библиотеки python-telegram-bot (см. [Управление отрисовкой (метод render)](advanced.md#управление-отрисовкой-метод-render)). В нем содержатся такие же атрибуты экрана (клавиатура, описание и пр.), которые реально увидит пользователь.

<!-- -->

> **Примечание**: в качестве объекта для сравнения необходимо создать обычный [`RenderConfig`](../api_reference/core/constants.md/#hammett.core.constants.RenderConfig) с ожидаемыми атрибутами и передать его в [`prepare_final_render_config`](../), который добавляет дополнительные атрибуты для точного сравнения.

Ниже приведен пример теста, демонстрирующего проверку экрана и корректность рендера сообщения. Тест создает имитацию вызова соответствующего обработчика и проверяет, что итоговое состояние и интерфейс соответствуют ожидаемым:

{% include-markdown 'examples/testing/catch_render_config_usage.md' %}

### <a name="изменение-атрибутов-в-моковых-объектах"></a> Изменение атрибутов в моковых объектах

В некоторых случаях при написании тестов может потребоваться изменить параметры моковых объектов, создаваемых по умолчанию в [`BaseTestCase`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase). Например, если необходимо имитировать ситуацию пришедшего сообщения от пользователя для тестирования Start-маркеров (см. [Start-маркеры](advanced.md#start-маркеры)). В этом случае нужно переопределить метод [`get_message`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_message) в классе теста, вернув из него собственный экземпляр Message с нужными параметрами, включая текст команды. Ниже приведен пример:

{% include-markdown 'examples/testing/get_message_method_overriding.md' %}

> **Примечание**: таким образом, метод [`get_message`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_message) возвращает объект [`Message`](https://docs.python-telegram-bot.org/en/v21.6/telegram.message.html#message), который будет использован вместо стандартного при создании моков. Аналогичным образом могут быть переопределены методы [`get_chat`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_chat), [`get_context`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_context), [`get_native_application`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_native_application), [`get_update`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_update), [`get_user`](../api_reference/test/base.md/#hammett.test.base.BaseTestCase.get_user), отвечающие соответственно за объекты [`Chat`](https://docs.python-telegram-bot.org/en/v21.7/telegram.chat.html), [`CallbackContext`](https://docs.python-telegram-bot.org/en/v13.7/telegram.ext.callbackcontext.html), [`Application`](https://docs.python-telegram-bot.org/en/v21.6/telegram.ext.application.html), [`Update`](https://docs.python-telegram-bot.org/en/v21.10/telegram.update.html) и [`User`](https://docs.python-telegram-bot.org/en/v21.5/telegram.user.html). Это позволяет точечно настраивать окружение теста под конкретные сценарии.

<!-- -->

> **Примечание**: при тестировании Permission-механизма необходимо, чтобы каждый тест выполнялся в изолированной среде с собственным экземпляром класса [`Bot`](../api_reference/core/bot.md#hammett.core.bot.Bot) и отдельными экранами. Это требование связано с тем, что экраны в Hammett реализованы как синглтоны, и использование общих экземпляров между тестами может привести к непредсказуемому поведению. Для предотвращения подобных конфликтов рекомендуется создавать отдельные экран(ы) внутри каждого теста.

Ниже приведен пример тестирования Permission-механизма:

{% include-markdown 'examples/testing/permission_mechanism_details.md' %}
