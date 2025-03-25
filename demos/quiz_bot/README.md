# HammettQuizBot

This demo showcases the `SingleChoiceWidget` and `MultiChoiceWidget` widgets to tackle various tasks. It demonstrates how they can be used to create a quiz with options for selecting one or multiple correct answers. Additionally, the bot illustrates how to use the `.po` files to create multilingual interfaces. Check out the [documentation](https://cusdeb-com.github.io/hammett) for more details.

See the live demo [here](https://t.me/HammettQuizBot).

## Table of Contents:

- [Installation](#installation)
- [Run the Bot](#run-the-bot)
- [Run the Tests](#run-the-tests)
- [Docker](#docker)

## Installation

First, navigate to the `demos/quiz_bot/` directory:

```bash
$ cd demos/quiz_bot/
```

Next, create and activate a virtual environment:

```bash
$ virtualenv -p python3 quiz-bot-env
$ source ./quiz-bot-env/bin/activate
```

Then, install the necessary dependencies from `requirements.txt`:

```bash
$ pip install -r requirements.txt
```

## Run the Bot

Firstly, you need to generate .mo files for a translation support using the following command:

```bash
$ msgfmt demos/quiz_bot/locale/en/LC_MESSAGES/hammett.po -o demos/quiz_bot/locale/en/LC_MESSAGES/hammett.mo \
&& msgfmt demos/quiz_bot/locale/pt-br/LC_MESSAGES/hammett.po -o demos/quiz_bot/locale/pt-br/LC_MESSAGES/hammett.mo \
&& msgfmt demos/quiz_bot/locale/ru/LC_MESSAGES/hammett.po -o demos/quiz_bot/locale/ru/LC_MESSAGES/hammett.mo
```

Secondly, you need to set the `HAMMETT_SETTINGS_MODULE` and `TOKEN` environment variables. And only after that, run the `demo.py` script using the following command:

```bash
$ env HAMMETT_SETTINGS_MODULE=settings TOKEN=your-token python3 demo.py
```

Alternatively, you can create a `.env` file to specify the `TOKEN`. In this case, execute these commands:

```bash
$ source .env
$ env HAMMETT_SETTINGS_MODULE=settings python3 demo.py
```

After completing these steps, the bot will be up and ready to accept the `/start` command.

## Run the Tests

The demo includes tests located in the `tests.py` module. To run the tests, use the following command:

```bash
$ env TOKEN=test-token python3 tests.py
```

## Docker

To run the demo in a Docker container, first navigate to the `demos/` directory and execute the following command:

```bash
$ docker compose up --build -d quiz-bot
```
