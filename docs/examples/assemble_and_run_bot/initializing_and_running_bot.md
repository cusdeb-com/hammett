```python
from hammett.core import Bot, Screen
from hammett.core.constants import DEFAULT_STATE
from hammett.core.mixins import StartMixin


class MainMenu(StartMixin, Screen):
   description = 'Main menu description'

def main():
    bot = Bot(
        'name',
        entry_point=MainMenu,
        states={DEFAULT_STATE: {MainMenu}},
    )
    bot.run()


if __name__ == '__main__':
    main()
```
