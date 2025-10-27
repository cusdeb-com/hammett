```python
from hammett.widgets import MultiChoiceWidget


class LanguagePoll(MultiChoiceWidget):
    description = 'Which programming language do you code in?'
    choices = (
        ('Python', 'Python'),
        ('C++', 'C++'),
        ('JavaScript', 'JavaScript'),
    )
```
