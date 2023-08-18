```python
from hammett.conf import settings
from hammett.core.hider import HidersChecker


class MyHidersChecker(HidersChecker):
    async def is_admin(self, update, context):
        user = update.effective_user
        return user.id in settings.ADMIN_GROUP
```
