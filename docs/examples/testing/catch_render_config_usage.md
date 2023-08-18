```python
from hammett.core import Screen
from hammett.core.constants import RenderConfig
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config


class MyScreen(Screen):
    description = 'My screen description.'


class MyTests(BaseTestCase):
    @catch_render_config()
    async def test_screen_render_after_calling_jump_handler(self, actual):
        await MyScreen().jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=MyScreen.description,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)
```
