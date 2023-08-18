```python
from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.core.hider import ONLY_FOR_ADMIN, ONLY_FOR_BETA_TESTERS, Hider


Button('🔒 Secret Room', SecretRoom,
      hiders=Hider(ONLY_FOR_ADMIN) | Hider(ONLY_FOR_BETA_TESTERS),
      source_type=SourceTypes.MOVE_SOURCE_TYPE)
```
