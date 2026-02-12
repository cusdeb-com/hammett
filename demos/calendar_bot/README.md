# HammettCalendarBot

This demo showcases `CalendarWidget` provided by Hammett. It shows how it can be used to create a calendar with options for selecting a specific date. Check out the [documentation](https://cusdeb-com.github.io/hammett) for more details.

See the live demo [here](https://t.me/HammettCalendarBot).

## Table of Contents:

- [Installation](#installation)
- [Run the Bot](#run-the-bot)
- [Run the Tests](#run-the-tests)
- [Docker](#docker)

## Installation

First, navigate to the `demos/calendar_bot/` directory:

```bash
$ cd demos/calendar_bot/
```

Next, create and activate a virtual environment:

```bash
$ virtualenv -p python3 calendar-bot-env
$ source ./calendar-bot-env/bin/activate
```

Then, install the necessary dependencies from `pyproject.toml`:

```bash
$ pip install .
```

## Run the Bot

Initially, you need to set the `HAMMETT_SETTINGS_MODULE` and `TOKEN` environment variables. After that, run the `demo.py` script using the following command:

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
$ python3 tests.py
```

## Docker

To run the demo in a Docker container, first navigate to the `demos/` directory and execute the following command:

```bash
$ docker compose up --build -d calendar-bot
```
