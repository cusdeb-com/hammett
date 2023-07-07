"""The module contains the types used throughout the framework. """

from collections.abc import Callable
from typing import Any, TypeVar

from telegram import Update
from telegram.ext import BaseHandler, CallbackContext
from telegram.ext._utils.types import CCT, ConversationKey

from hammett.core.screen import Button, Screen

CheckUpdateType = tuple[object, ConversationKey, BaseHandler[Update, CCT], object]

Func = TypeVar('Func', bound=Callable[..., Any])

Handler = TypeVar('Handler', bound=Callable[[Screen, Update, CallbackContext], int])

Keyboard = list[list[Button]]

NativeStates = dict[object, list[BaseHandler[Update, CCT]]]

Sources = str | Func | type

States = dict[int, list[type[Screen]]]
