# Hammett

Hammett is a framework whose main goal is to simplify building *commercial* Telegram bots with clear code and a good architecture. By commercial bots are meant such bots that require the support of
* several roles of users (admin, beta testers, moderators, etc.) to manage the visibility of some parts of the user interface;
* the permissions mechanism to implement a **maintenance mode**, **paywall**, etc.
* storing the users state in and restoring it from Redis / Valkey.

<p align="center">
    <img src="/logo/1633x1380.png" alt="Hammett" style="max-width: 100%; width: 500px">
</p>

## Documentation

Here's the **Getting Started** guide, available in both 🇬🇧 [English](https://cusdeb-com.github.io/hammett/getting-started/) and 🇷🇺 [Russian](https://cusdeb-com.github.io/hammett/ru/getting-started/). When you've finished it, don't forget to check out the [Introduction to Bot Development](https://cusdeb-com.github.io/hammett/introduction_to_bot_development/three-pillars/).

## Live Demos

* [admin-panel-bot](https://t.me/HammettAdminPanelBot) showcases how to control the visibility of buttons based on the user role (see the demo's [source](demos/admin_panel_bot)).
* [carousel-bot](https://t.me/HammettCarouselBot) demonstrates how to work with the carousel widget (see the demo's [source](demos/carousel_bot)).
* [clicker-bot](https://t.me/HammettClickerBot) illustrates how to attach a handler to a button (see the demo's [source](demos/clicker_bot)).
* [dynamic-keyboard-bot](https://t.me/HammettDynamicKeyboardBot) shows how to create and work with a dynamic keyboard (see the demo's [source](demos/dynamic_keyboard_bot)).
* [hide-keyboard-bot](https://t.me/HammettHideKeyboardBot) explains how to hide keyboards from previous messages (see the demo's [source](demos/hide_keyboard_bot)).
* [multi-state-bot](https://t.me/HammettMultiStateBot) showcases how to work with multiple states (see the demo's [source](demos/multi_state_bot)).
* [paywall-bot](https://t.me/HammettPaywallBot) demonstrates how to manage access to the bot screens by checking specific conditions (see the demo's [source](demos/paywall_bot)).
* [quiz-bot](https://t.me/HammettQuizBot) showcases the single-choice and multi-choice widgets to tackle various tasks (see the demo's [source](demos/quiz_bot)).
* [reminder-bot](https://t.me/HammettReminderBot) showcases how to send users delayed notifications (see the demo's [source](demos/reminder_bot)).
* [say-hello-bot](https://t.me/HammettSayHelloBot) illustrates how to create a handler for an input command (see the demo's [source](demos/say_hello_bot)).
* [simple-jump-bot](https://t.me/HammettSimpleJumpBot) demonstrates how to switch between screens (see the demo's [source](demos/simple_jump_bot)).

## Real-World Examples

To assess the capabilities of Hammett, you can take a look at some real-world examples. One such example is [TutorInTechBot](https://t.me/TutorInTechBot?start=github), which is a library of open-licensed books on Information Technology available in both Russian and English.

## Tests

To run the tests use the following command:

```bash
env PYTHONPATH=$(pwd) python3 tests/run_tests.py
```

You can also run the tests with coverage, using the following commands:

```bash
env PYTHONPATH=$(pwd) HAMMETT_SETTINGS_MODULE=tests.settings coverage run -m unittest discover -s tests/
coverage report
```

## Authors

See [AUTHORS](AUTHORS.md).

## Licensing

The code of Hammett is licensed under the [Apache License 2.0](https://apache.org/licenses/LICENSE-2.0) except:

* the modules borrowed from [Django](https://djangoproject.com) and licensed under the **[3-Clause BSD License](https://opensource.org/license/bsd-3-clause/)**:
  * `hammett/conf/__init__.py`
  * `hammett/test/base.py`
  * `hammett/test/utils.py`
  * `hammett/utils/module_loading.py`
* the `hammett/core/conversation_handler.py` module borrowed from [PTB](https://python-telegram-bot.org) and licensed under the **[GNU Lesser General Public License version 3](https://opensource.org/license/lgpl-3-0/)**.
