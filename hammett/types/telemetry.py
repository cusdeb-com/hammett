"""The module contains types for OpenTelemetry instrumentation hooks."""

from collections.abc import Callable
from typing import Any

from opentelemetry.trace import Span
from telegram import Update
from telegram.ext import CallbackContext

from hammett.core.permission import Permission
from hammett.core.screen import Screen
from hammett.types.core import Handler

TelemetryHandlerHook = Callable[[Span, Handler, Screen], None]

TelemetryPermissionHook = Callable[[Span, Permission, bool], None]

TelemetryUpdateHook = Callable[[Span, Update, CallbackContext[Any, Any, Any, Any]], None]
