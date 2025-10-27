```python
import json
import httpx

from hammett.core import Button, Screen
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes


class ListOfProducts(Screen):
    async def move(self, update, context, **kwargs):
        keyboard = []
        try:
            response = await httpx.AsyncClient().get('https://some/url/path/to/products/')
            products = response.json()
        except (json.JSONDecodeError, httpx.HTTPError):
            config = RenderConfig(description="Couldn't fetch the products")
        else:
            config = RenderConfig(description='Here are the products:\n')
            keyboard = [
                [
                    Button(f'{product["title"]}',
                           SelectedProduct,
                           source_type=SourceTypes.MOVE_SOURCE_TYPE)
                ] for product in products
            ]

        config.keyboard = [
            *keyboard,
            [Button('Main Menu', MainMenu,
                   source_type=SourceTypes.MOVE_SOURCE_TYPE)],
        ]

        await self.render(update, context, config=config)
        return DEFAULT_STATE
```
