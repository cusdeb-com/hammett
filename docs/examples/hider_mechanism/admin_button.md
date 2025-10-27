```python
from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.core.hider import ONLY_FOR_ADMIN, Hider


Button('🔒 Available only for admins', SecretRoom,
      hiders=Hider(ONLY_FOR_ADMIN),
      source_type=SourceTypes.MOVE_SOURCE_TYPE)
```
