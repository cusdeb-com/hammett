Hammett предлагает _виджеты_, которые представляют собой "экраны на стероидах", предназначенные для решения разных типовых задач. Каждый виджет имеет встроенную клавиатуру, соответствующую его функциональности, и реализует дополнительную логику поведения.

В отличие от обычных экранов, виджеты не используют метод [`add_default_keyboard`](../api_reference/core/screen.md#hammett.core.screen.Screen.add_default_keyboard). Вместо него для добавления дополнительных элементов применяется его аналог — [`add_extra_keyboard`](../api_reference/widgets/base.md/#hammett.widgets.base.BaseWidget.add_extra_keyboard).

> **Примечание**: все виджеты могут использоваться в качестве уведомлений, т.к. они реализуют свой обработчик [`send`](../api_reference/core/screen.md#hammett.core.screen.Screen.send) (см. [Задачи, выполняемые по расписанию](advanced.md#задачи-выполняемые-по-расписанию)).

<!-- -->

> **Примечание**: у каждого виджета есть свое уникальное состояние, которое не пересекается в чате с другим таким же виджетом. То есть, если в чате есть два одинаковых сообщения с одним и тем же виджетом, то изменения в одном не влияют на другой.

## <a name="виджеты-выбора"></a> Виджеты выбора

Виджеты выбора представляют собой такие же виджеты как, например, на веб-сайте, только в рамках Telegram и предназначены для отображения набора опций в виде кнопок. Существует два варианта:

1. [`SingleChoiceWidget`](../api_reference/widgets/single_choice_widget.md/#hammett.widgets.single_choice_widget.SingleChoiceWidget) — с одним выбором;
2. [`MultiChoiceWidget`](../api_reference/widgets/multi_choice_widget.md/#hammett.widgets.multi_choice_widget.MultiChoiceWidget) — с несколькими выборами.

Набор опций определяется через атрибут `choices` или метод [`get_choices`](../api_reference/widgets/base.md/#hammett.widgets.base.BaseChoiceWidget.get_choices). Их типизация описана в модуле описана в модуле [`hammett.widgets.types`](../api_reference/widgets/types.md):

{% include-markdown 'examples/widgets/choices_typing.md' %}

Здесь первый элемент — значение, передаваемое в обработчик (считайте это [полезной нагрузкой](screens.md#полезная-нагрузка)), а второй — текст, отображающийся на кнопке рядом с индикатором состояния.

Ниже приведен пример атрибута `choices`:

{% include-markdown 'examples/widgets/choices_attribute.md' %}

Для визуализации выбора используются эмодзи, задаваемые атрибутами `chosen_emoji` и `unchosen_emoji`.

Метод [`switch`](../api_reference/widgets/base.md/#hammett.widgets.base.BaseChoiceWidget.switch) управляет визуальной составляющей. При совершении выбора, он перерисовывает кнопки и предлагает интерфейс для добавления своей логики. При этом важно в конце вызвать `super` родительского класса, чтобы продолжить перерисовку экрана.

Ниже приведен пример:

{% include-markdown 'examples/widgets/switch_usage.md' %}

Теперь поговорим отдельно про каждый из типов виджетов.

### <a name="виджет-с-одним-выбором"></a> Виджет с одним выбором

[`SingleChoiceWidget`](../api_reference/widgets/single_choice_widget.md/#hammett.widgets.single_choice_widget.SingleChoiceWidget) предлагает возможность выбора _одного_ варианта ответа из имеющихся. Хорошим примером его использования является экран выбора языка:

{% include-markdown 'examples/widgets/language_switcher.md' %}

Конкретно в этом примере нам нужно указать значение по умолчанию, так как интерфейс уже имеет какой-то язык, например, английский. В этом случае, следует воспользоваться атрибутом `initial_value` или методом [`get_initial_value`](../api_reference/widgets/single_choice_widget.md/#hammett.widgets.single_choice_widget.SingleChoiceWidget.get_initial_value).

{% include-markdown 'examples/widgets/language_switcher_with_initial_value.md' %}

См. live-пример бота [HammettQuizBot](https://t.me/HammettQuizBot) с демонстрацией работы этого функционала.

### <a name="виджет-с-несколькими-выборами"></a> Виджет с несколькими выборами

[`MultiChoiceWidget`](../api_reference/widgets/multi_choice_widget.md/#hammett.widgets.multi_choice_widget.MultiChoiceWidget) , позволяет пользователю выбрать _несколько_ вариантов из списка. Хорошим примером его использования является экран для прохождения опроса с выбором нескольких ответов:

{% include-markdown 'examples/widgets/language_poll.md' %}

Для этого виджета значение/я по умолчанию задаются атрибутом `initial_values` или методом [`get_initial_values`](../api_reference/widgets/multi_choice_widget.md/#hammett.widgets.multi_choice_widget.MultiChoiceWidget.get_initial_values).

{% include-markdown 'examples/widgets/language_poll_with_initial_values.md' %}

См. live-пример бота [HammettQuizBot](https://t.me/HammettQuizBot) с демонстрацией работы этого функционала.

## <a name="виджет-карусели"></a> Виджет карусели

[`CarouselWidget`](../api_reference/widgets/carousel_widget.md/#hammett.widgets.carousel_widget.CarouselWidget) — виджет, отображающий последовательность изображений с возможностью перехода между ними с помощью кнопок навигации. Примером может послужить создание галереи.

Набор изображений и описаний к ним определяется через атрибут `images`или метод [`get_images`](../api_reference/widgets/carousel_widget.md/#hammett.widgets.carousel_widget.CarouselWidget.get_images). Его типизация:

{% include-markdown 'examples/widgets/images_typing.md' %}

Здесь первый элемент — путь к изображению, а второй — соответствующий текст, на экране для этого изображения.

Ниже приведен пример атрибута `images`:

{% include-markdown 'examples/widgets/gallery.md' %}

По умолчанию карусель не является _бесконечной_ (или зацикленной). Таким образом, когда пользователь дойдет до конца списка изображений, он увидит, что кнопка для переключения на следующее изображение окажется недоступной. Чтобы изменить это поведение и сделать карусель бесконечной, нужно установить атрибут `infinity` в `True`. После этого пользователь сможет попасть в начало списка изображений, когда дойдет до конца.

Чтобы управлять внешним видом стрелок, можно воспользоваться атрибутами `back_caption` — для кнопки перехода к предыдущему изображению, `next_caption` — для кнопки перехода к следующему изображению и `disable_caption` — для кнопки бездействия, когда достигнут конец списка изображений.

См. live-пример бота [HammettCarouselBot](https://t.me/HammettCarouselBot) с демонстрацией работы этого функционала.

## <a name="виджет-календаря"></a> Виджет календаря

[`CalendarWidget`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget) — это виджет, клавиатура которого представляет собой слоты календаря (год, месяц или день) с навигационными элементами для переключения между периодами. Виджет предназначен для реализации сценариев выбора даты, например, при планировании мероприятий или встреч.

> **Примечание**: [`CalendarWidget`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget) наследуется от [`I18NMixin`](../api_reference/core/mixins.md/#hammett.core.mixins.I18NMixin) [(`hammett.core.mixins`)](../api_reference/core/mixins.md) и поддерживает перевод аббревиатур месяцев и дней недели. Миксин реализует методы [`get_language_code`](../api_reference/core/mixins.md/#hammett.core.mixins.I18NMixin.get_language_code) и [`set_language_code`](../api_reference/core/mixins.md/#hammett.core.mixins.I18NMixin.set_language_code), обеспечивающие получение и сохранение текущего кода языка пользователя. По умолчанию фреймворк поддерживает перевод на **английский**, **бразильский португальский** и **русский** языки [(см. Переводы)](../introduction_to_bot_development/translation.md).

После завершения выбора вызывается метод [`get_confirm_description`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.get_confirm_description), возвращающий строковое представление выбранной даты (по умолчанию формат: `1 Jan 2025`). Этот метод можно переопределить для расширения описания:

{% include-markdown 'examples/widgets/get_confirm_description_overriding.md' %}

### <a name="обработка-выбора-дня"></a> Обработка выбора дня

Для обработки события выбора даты и перехода на другой экран используется обработчик [`on_day_click`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.on_day_click). По умолчанию он ререндерит виджет с описанием, полученным от [`get_confirm_description`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.get_confirm_description). Если это поведение вас не устраивает, то обработчик можно переопределить, например, для перенаправления на другой экран:

{% include-markdown 'examples/widgets/on_day_click_overriding.md' %}

### <a name="управление-начальными-параметрами"></a> Управление начальными параметрами

Начальными параметрами можно управлять с помощью следующих атрибутов:

| Атрибут          | Тип             | Назначение                                                   | Значение по умолчанию |
| ---------------- | --------------- | ------------------------------------------------------------ | --------------------- |
| `initial_unit`   | `CalendarUnit`  | Определяет первый отображаемый период (год, месяц или день). | `CalendarUnit.YEAR`   |
| `current_date`   | `datetime.date` | Текущая дата.                                                | Системная дата        |
| `left_boundary`  | `datetime.date` | Минимально доступная дата.                                   | `0001-01-01`          |
| `right_boundary` | `datetime.date` | Максимально доступная дата.                                  | `2999-12-31`          |

> **Примечание**: Если задать `initial_unit` равным `CalendarUnit.MONTH` или `CalendarUnit.DAY`, то значения месяца и года синхронизируются с `current_date`.

<!-- -->

> **Примечание**: Все кнопки навигации автоматически блокируются при достижении границ, заданных `left_boundary` и `right_boundary`.

Ниже приведен пример календаря, в котором нельзя выбрать дату меньше, чем текущая:

{% include-markdown 'examples/widgets/set_left_boundary_overriding.md' %}

### <a name="настройка-описаний"></a> Настройка описаний

Для управления текстами, отображаемыми на каждом экране выбора, используются следующие атрибуты:

1. `day_description` / [`get_day_description`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.get_day_description) — описание экрана выбора дня.
2. `month_description` / [`get_month_description`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.get_month_description) — описание экрана выбора месяца.
3. `year_description` / [`get_year_description`](../api_reference/widgets/calendar_widget.md/#hammett.widgets.calendar_widget.CalendarWidget.get_year_description) — описание экрана выбора года.

Эти атрибуты могут задаваться статически или формироваться динамически. При использовании динамического подхода, каждый из методов имеет доступ к текущей выбранной дате. Это может помочь конкретизировать текст на экране. Ниже приведен пример описания с указанием выбранного года на странице выбора месяца:

{% include-markdown 'examples/widgets/get_month_description_overriding.md' %}

### <a name="настройка-клавиатуры-и-навигации"></a> Настройка клавиатуры и навигации

Клавиатурой и навигацией можно управлять с помощью следующих атрибутов:

| Атрибут                | Назначение                                                 | Значение по умолчанию |
| ---------------------- | ---------------------------------------------------------- | --------------------- |
| `back_caption`         | Подпись кнопки возврата к предыдущему периоду              | ↞                     |
| `next_caption`         | Подпись кнопки перехода к следующему периоду               | ↠                     |
| `disable_caption`      | Подпись неактивной кнопки при достижении предела диапазона | 🞩                     |
| `middle_day_caption`   | Подпись центральной кнопки навигации для выбора дня        | `{month} {year}`      |
| `middle_month_caption` | Подпись центральной кнопки навигации для выбора месяца     | `{year}`              |
| `middle_year_caption`  | Подпись центральной кнопки навигации для выбора года       | —                     |

### <a name="размерность-сетки"></a> Размерность сетки

Размерностью сетки можно управлять с помощью следующих атрибутов:

| Атрибут            | Назначение                                 | Значение по умолчанию |
| ------------------ | ------------------------------------------ | --------------------- |
| `month_row_size`   | Количество кнопок в ряду при выборе месяца | `3`                   |
| `year_row_size`    | Количество строк при выборе года           | `3`                   |
| `year_column_size` | Количество столбцов при выборе года        | `4`                   |

> **Примечание**: Для корректного построения сетки месяцев рекомендуется выбирать значение `month_row_size` кратное двум или трем. Так же учитывайте, что максимальное количество кнопок на клавиатуре по горизонтали составляет **8**.

См. live-пример бота [HammettCalendarBot](https://t.me/HammettCalendarBot) с демонстрацией работы этого функционала.
