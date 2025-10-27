Permission-механизм позволяет реализовать _проверки прав доступа_ для управления видимостью экранов в боте, т.е. пользователи могут _видеть_ или _не видеть_ те или иные экраны в зависимости от **прав доступа**. Вот пара примеров, в каких случаях этот механизм может использоваться:

- Регистрация, которую обязан пройти пользователь, чтобы **получить разрешение** использовать сервис, предоставляемый ботом.
- Paywall, когда пользователь **не имеет разрешения** продвинутся дальше, пока не оформит подписку на бота.

Проверки прав доступа реализуются в виде классов, которые наследуются от класса [`Permission`](../api_reference/core/permission.md/#hammett.core.permission.Permission) из модуля [`hammett.core.permission`](../api_reference/core/permission.md) и должны реализовать два метода:

1. [`has_permission`](../api_reference/core/permission.md/#hammett.core.permission.Permission.has_permission), в котором содержится логика проверки выдачи разрешения двигаться дальше;
2. [`handle_permission_denied`](../api_reference/core/permission.md/#hammett.core.permission.Permission.handle_permission_denied), в котором содержится логика того, что делать, если метод [`has_permission`](../api_reference/core/permission.md/#hammett.core.permission.Permission.has_permission) вернул `False` (т.е. когда у пользователя нет разрешения получить доступ к тому или иному экрану).

Такие классы называются _классами прав доступа_.

Ниже представлен пример класса прав доступа для проверки, оплатил ли пользователь подписку на бота. Для этого делается вызов функции `has_user_paid`. Если проверка проходит успешно, пользователь сможет пройти дальше, например, к экрану главного меню; в противном случае он будет перенаправлен на экран оплаты `Payment`.

{% include-markdown 'examples/permission_mechanism/paywall_permission_implementation.md' %}

После создания класса его необходимо зарегистрировать.

## <a name="регистрация-классов-прав-доступа"></a> Регистрация классов прав доступа

Регистрация классов прав доступа делается через добавление их полного пути, представленного в виде строки, в параметр конфигурации `PERMISSIONS`, который является списком. Например:

{% include-markdown 'examples/permission_mechanism/permissions_setting.md' %}

Классов прав доступа может быть несколько, и порядок их перечисления в списке регистрации **важен**, т.к. он задает очередность, в которой они будут срабатывать. Например, при добавлении еще одного класса, регистрация прав доступа будет выглядеть так:

{% include-markdown 'examples/permission_mechanism/permissions_setting_with_two_permissions.md' %}

Это _цепочка проверок_. Первой будет вызвана проверка доступа — метод `has_permission` из `MaintenanceModePermission`. Если он вернет `True`, то следующим будет вызван метод `has_permission` из `PaywallPermission`. Но если `has_permission` из `MaintenanceModePermission` вернет `False`, то будет вызван метод `handle_permission_denied` из `MaintenanceModePermission`, и дело до `PaywallPermission` не дойдет.

## <a name="игнорирование-проверок-доступа"></a> Игнорирование проверок доступа

Проверки доступа можно игнорировать, т.е. для указанного обработчика можно отключить _всю цепочку проверок_ из `PERMISSIONS` или только _ее часть_. Это можно сделать, если применить к этому обработчику декоратор [`ignore_permissions`](../api_reference/core/permission.md/#hammett.core.permission.ignore_permissions) с указанием списка классов прав доступа через аргумент `permissions`, которые для него нужно проигнорировать. Например, чтобы пользователь смог оформить подписку на бота, он должен вызвать обработчик оплаты, нажав на кнопку. Но в обычном случае выполнение до кода этого обработчика не дойдет, т.к. снова будет вызван [`handle_permission_denied`](../api_reference/core/permission.md/#hammett.core.permission.Permission.handle_permission_denied). Поэтому в данном случае потребуется использовать [`ignore_permissions`](../api_reference/core/permission.md/#hammett.core.permission.ignore_permissions).

Таким образом, проверки доступа будут срабатывать перед вызовом всех обработчиков, кроме тех, что обернуты в [`ignore_permissions`](../api_reference/core/permission.md/#hammett.core.permission.ignore_permissions), а _также_ обработчика [`send`](../api_reference/core/screen.md#hammett.core.screen.Screen.send).

> **Примечание**: имейте это в виду, когда реализуете логику проверок прав доступа. Если проверка предполагает отправку запроса на сервер, то она может **замедлять** рендеринг экранов. Иногда замедление может быть довольно ощутимым, в зависимости от того, насколько долго придется ждать ответа от сервера. Частично эту проблему можно решить, используя кеширование. Hammett предлагает встроенный механизмом для решения этой задачи (см. [Кеширование](advanced.md#декоратор-cache)).

<!-- -->

> **Примечание**: обработчик [`send`](../api_reference/core/screen.md#hammett.core.screen.Screen.send) используется для отправки экрана в качестве _уведомления_ (см. [Задачи, выполняемые по расписанию](advanced.md#задачи-выполняемые-по-расписанию)) и не имеет доступа к объекту `update`. Если вам необходимо раздавать права на получение уведомлений, то вы можете сами реализовать фильтрацию получаемых (из базы данных или от сервера) идентификаторов пользователей перед рассылкой.

**Важно**: при использовании декоратора [`ignore_permissions`](../api_reference/core/permission.md/#hammett.core.permission.ignore_permissions) совместно с декоратором регистрации какого-либо типа обработчика (см. [Обработчики](screens.md#обработчики)), он должен быть выше декоратора регистрации обработчика. Например:

{% include-markdown 'examples/permission_mechanism/order_of_applying_decorators.md' %}

См. live-пример бота [HammettPaywallBot](https://t.me/HammettPaywallBot) с демонстрацией работы этого функционала.
