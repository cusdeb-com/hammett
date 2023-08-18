> ```python
> from hammett.core.handlers import register_button_handler
>
>
> @register_button_handler
> async def handle_payment(self, update, _context):
>     if has_paid(update.effective_user.id):
>         self.description = 'You have successfully paid'
>
>     ...
> ```
