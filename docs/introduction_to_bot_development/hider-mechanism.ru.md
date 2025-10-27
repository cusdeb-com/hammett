Hider-механизм позволяет управлять видимостью кнопок в зависимости от роли пользователя. Так, например, администратор может видеть кнопки, которые будут оставаться невидимыми для рядовых пользователей.

Эти проверки называются _хайдерами_. Хайдеры реализуются в виде классов, которые наследуются от класса [`HidersChecker`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker) из модуля [`hammett.core.hider`](../api_reference/core/hider.md). Этот класс содержит _методы проверки_ условий — показывать кнопку или нет. По умолчанию предоставляются следующие проверки для переопределения: [`is_admin`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker.is_admin), [`is_beta_tester`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker.is_beta_tester) и [`is_moderator`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker.is_moderator), отвечающие за проверку роли пользователя на админа, бета-тестера и модератора соответственно.

{% include-markdown 'examples/hider_mechanism/hiders_checker_is_admin_check.md' %}

Затем хайдер необходимо зарегистрировать. Это делается через добавление его полного пути, представленного в виде строки, в параметр конфигурации `HIDERS_CHECKER`. Например:

{% include-markdown 'examples/hider_mechanism/hider_checker_setting.md' %}

Для того чтобы воспользоваться хайдером, нужно выбрать кнопку (класс [`Button`](../api_reference/core/button.md#hammett.core.button.Button)), которая нуждается в проверке на видимость, и передать ей объект класса [`Hider`](../api_reference/core/hider.md/#hammett.core.hider.Hider) через аргумент `hiders`. При инициализации объекта [`Hider`](../api_reference/core/hider.md/#hammett.core.hider.Hider) ему нужно передать соответствующий ключ, по которому будет определен метод проверки. Метод [`is_admin`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker.is_admin) привязан к ключу `ONLY_FOR_ADMIN`, метод [`is_beta_tester`](../api_reference/core/hider.md/#hammett.core.hider.HidersChecker.is_beta_tester) привязан к ключу `ONLY_FOR_BETA_TESTERS` и т.д.

Ниже приведен пример кнопки, которая видна только администраторам:

{% include-markdown 'examples/hider_mechanism/admin_button.md' %}

Хайдеры также можно **объединять** в цепочку через логический оператор | (OR):

{% include-markdown 'examples/hider_mechanism/admin_or_beta_tester_button.md' %}

В этом случае пользователь сможет увидеть кнопку, ведущую в "секретную комнату", если он администратор _или_ бета-тестер.

См. live-пример бота [HammettAdminPanelBot](https://t.me/HammettAdminPanelBot) с демонстрацией работы этого функционала.

## <a name="свои-проверки-для-hider-механизма"></a> Свои проверки для Hider-механизма

Если имеющихся методов проверки не хватает или нет подходящих, то можно создать свой и зарегистрировать его для дальнейшего использования. Ниже приведен пример:

{% include-markdown 'examples/hider_mechanism/creating_custom_hider.md' %}

Типом значения для ключа в `custom_hiders` должно быть `int`. Для корректной работы **не следует использовать числа в диапазоне от 0 до 2**, т.к. они зарезервированы для встроенных методов проверок.

> **Примечание**: возможно после изучения и применения Hider-механизма у вас может появиться соблазн использовать его в бизнес-логике управления видимостью той или иной кнопки, например, чтобы показывать или скрывать кнопку "Дальше" в опросах. Так делать не рекомендуется. Дело в том, что Hider-механизм разрабатывался для управления видимостью кнопок в зависимости от _ролей пользователей_, поэтому методам проверок следует включать обработку именно этих условий, а не других. Иначе это не _Hammett way_.
