```python
from datetime import UTC, datetime

from hammett.core.constants import RenderConfig
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from telegram import Message


class MainMenuTests(BaseTestCase):
    def get_message(self):
        return Message(
            self.message_id,
            datetime.now(tz=UTC),
            self.chat,
            from_user=self.user,
            text='/start ',
        )

    @catch_render_config()
    async def test_main_menu_config_jump_handler(self, actual):
        await MainMenu().jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
           as_new_message=True,
           description=MAIN_MENU_DESCRIPTION,
           keyboard=MAIN_MENU_KEYBOARD,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)
```
