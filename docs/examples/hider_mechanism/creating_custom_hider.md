```python
from hammett.conf import settings
from hammett.core.hider import HidersChecker


ONLY_FOR_STUDENTS = 3

def is_student(update, context):
    user = update.effective_user
    return user.id in settings.STUDENTS_GROUP


class MyHidersChecker(HidersChecker):
    custom_hiders = {
        ONLY_FOR_STUDENTS: is_student,
    }
```
