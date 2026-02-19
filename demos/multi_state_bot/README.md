# HammettMultiStateBot

This demo showcases the `move_along_route` feature provided by Hammett. `move_along_route` allows you to navigate between different states while re-rendering the same message. It also demonstrates a basic logging configuration with debug-level output to trace state transitions. Check out the [documentation](https://cusdeb-com.github.io/hammett) for more details.

See the live demo [here](https://t.me/HammettMultiStateBot).

## Table of Contents:

- [Installation](#installation)
- [Run the Bot](#run-the-bot)
- [Run the Tests](#run-the-tests)
- [Docker](#docker)

## Installation

First, navigate to the `demos/multi_state_bot/` directory:

```bash
cd demos/multi_state_bot/
```

Next, create and activate a virtual environment:

```bash
python3 -m venv multi-state-bot-env
source ./multi-state-bot-env/bin/activate
```

Then, install the necessary dependencies from `pyproject.toml`:

```bash
pip install .
```

### Using UV (recommended)

If you prefer using [UV](https://docs.astral.sh/uv/), you can create a virtual environment and install dependencies with:

```bash
uv sync
```

This will automatically create a virtual environment (if needed) and install dependencies defined in `pyproject.toml`.

### Redis Requirement

This demo requires a running Redis-compatible server (e.g. [Redis](https://redis.io/docs/latest/) or [Valkey](https://valkey.io/docs/)).

You can start a compatible server using Docker:

```bash
docker run -d --rm \
  --name hammett-valkey \
  -p "127.0.0.1:6379:6379" \
  valkey/valkey:8.0
```

This will expose Valkey on `127.0.0.1:6379`.

## Run the Bot

Initially, you need to set the `HAMMETT_SETTINGS_MODULE` and `TOKEN` environment variables. After that, run the `demo.py` script using the following command:

```bash
env HAMMETT_SETTINGS_MODULE=settings TOKEN=your-token python3 demo.py
```

Alternatively, you can create a `.env` file to specify the `TOKEN`. In this case, execute these commands:

```bash
source .env
env HAMMETT_SETTINGS_MODULE=settings python3 demo.py
```

After completing these steps, the bot will be up and ready to accept the `/start` command.

## Run the Tests

The demo includes tests located in the `tests.py` module. To run the tests, use the following command:

```bash
python3 tests.py
```

## Docker

To run the demo in a Docker container, first navigate to the `demos/` directory and execute the following command:

```bash
docker compose up --build -d multi-state-bot
```
