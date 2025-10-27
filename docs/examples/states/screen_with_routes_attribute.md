```python
from hammett.core import Screen
from hammett.core.constants import DEFAULT_STATE
from hammett.core.mixins import RouteMixin


class IntroductionScreen(RouteMixin, Screen):
    routes = (
        ({DEFAULT_STATE}, TYPE_NAME_STATE),
    )
```
