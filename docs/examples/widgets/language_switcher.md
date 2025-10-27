```python
from hammett.widgets import SingleChoiceWidget


class LanguageSwitcher(SingleChoiceWidget):
    description = 'Choose the language to switch to.'
    choices = (
        ('en', '🇬🇧 English'),
        ('pt-br', '🇧🇷 Português'),
        ('ru', '🇷🇺 Русский'),
    )
```
