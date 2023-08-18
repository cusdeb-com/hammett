> ```python
> from hammett.core.handlers import register_command_handler
>
>
> @register_command_handler('say_hello')
> async def handle_typing_say_hello_command(self, update, context):
>     ...
> ```
