> ```python
> from hammett.core import Button
> from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
> from hammett.core.handlers import register_typing_handler
>
>
> @register_typing_handler
> async def handle_text_input(self, update, context):
>     await self.render(update, context, config=RenderConfig(
>         as_new_message=True,
>         description='Hi, {name}!'.format(name=update.message.text),
>         keyboard=[[Button(
>             'Change Name',
>             IntroductionScreen,
>             source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
>         )]],
>     ))
>     return DEFAULT_STATE
> ```
