> ```python
> from hammett.core import Bot, Screen
> from hammett.core.constants import DEFAULT_STATE, RenderConfig
> from hammett.core.mixins import StartMixin
> from hammett.test.base import BaseTestCase
> from hammett.test.utils import catch_render_config
>
>
> def _get_bot(entry_point, *screens):
>     return Bot(
>         'Test',
>         entry_point=entry_point,
>         states={
>             DEFAULT_STATE: {entry_point, *screens},
>         },
>     )
>
> class HammettTests(BaseTestCase):
>     @catch_render_config()
>     async def test_fake_payment_screen_render_after_calling_move_handler(self, actual):
>         class TestMainMenuScreen(StartMixin):
>             description = 'Main Menu'
>
>         class TestFakePaymentScreen(Screen):
>             description = 'Fake Payment'
>
>         # The bot needs to be initialized for the permissions
>         # to be applied to the screens.
>         _get_bot(TestMainMenuScreen, TestFakePaymentScreen)
>
>         await TestFakePaymentScreen().move(self.update, self.context)
>
>         expected = self.prepare_final_render_config(RenderConfig(
>             description='Fake Payment',
>         ))
>         self.assertFinalRenderConfigEqual(expected, actual.final_render_config)
> ```
