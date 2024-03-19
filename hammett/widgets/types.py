"""The module contains types intended for use in the widgets only."""

Choice = tuple[str, str]

Choices = tuple[Choice] | tuple[()]

WidgetState = list[tuple[str, str]]
