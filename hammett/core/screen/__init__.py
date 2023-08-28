"""The package contains the implementation of the screen components
(i.e., cover, description and keyboard).
"""

from typing import TYPE_CHECKING

from telegram.error import BadRequest
from telegram.ext import ConversationHandler as NativeConversationHandler

from hammett.core.screen.screen import Button, RenderConfig, Screen, StartScreen

if TYPE_CHECKING:
    from typing import Any

    from telegram import Update
    from telegram.ext import Application
    from telegram.ext._utils.types import CCT
    from typing_extensions import Self

    from hammett.types import CheckUpdateType

__all__ = (
    'Button',
    'ConversationHandler',
    'RenderConfig',
    'Screen',
    'StartScreen',
)


class ConversationHandler(NativeConversationHandler['Any']):
    """The class for subclassing `telegram.ext.ConversationHandler` to
    override its `handle_update` method. The main purpose of this is to
    add custom error handling logic.
    """

    async def handle_update(  # type: ignore[override]
        self: 'Self',
        update: 'Update',
        application: 'Application[Any, CCT, Any, Any, Any, Any]',
        check_result: 'CheckUpdateType[CCT]',
        context: 'CCT',
    ) -> object | None:
        """Catches and handles `BadRequest` exceptions that may occur during
        the handling of updates.
        """

        try:
            res = await super().handle_update(update, application, check_result, context)
        except BadRequest as exc:  # noqa: TRY302
            raise exc  # noqa: TRY201
        else:
            return res

