# Hammett

Hammett is a framework whose main goal is to simplify building *commercial* Telegram bots with clear code and a good architecture. By commercial bots are meant such bots that require the support of
* several roles of users (admin, beta testers, moderators, etc.) to manage the visibility of some parts of the user interface;
* the permissions mechanism to implement a **maintenance mode**, **paywall**, etc.
* storing the users state in and restoring it from Redis.

<p align="center">
    <img src="/logo/1633x1380.png" alt="Hammett" style="max-width: 100%; width: 500px">
</p>

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
