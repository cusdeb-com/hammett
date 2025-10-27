```python
from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes


async def send_message_per_hour(context):
    users = await get_users()  # For example, from Redis or API
    for user in users:
        config = RenderConfig(
            chat_id=user['telegram_id'],
            keyboard=[[
                Button('⬅️ Main Menu', MainMenu,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ]]
        )
        await Notification().send(context, config=config)
```
