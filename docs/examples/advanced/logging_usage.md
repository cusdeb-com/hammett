```python
import logging

LOGGER = logging.getLogger(__name__)

LOGGER.debug('The user %s (%s) has moved to the MainMenu screen.', user.username, user.id)

LOGGER.info('The user %s (%s) was added to the admin group.', user.username, user.id)
```
