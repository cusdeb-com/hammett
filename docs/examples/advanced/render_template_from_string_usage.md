```python
import httpx
from hammett.template import render_template_from_string


response = await httpx.AsyncClient().get(
    'https://some/url/path/to/get/subscription/end/date/',
    params={'user_id': update.effective_user.id}
)
description = render_template_from_string(
    'The subscription ends on: {{date}}.', {
        'date': response.json()['date'],
    },
)
```
