"""The module contains the tests for HammettMultiStateBot."""

# ruff: noqa: I001

import os
import unittest
from datetime import datetime, timezone

from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from telegram import Message

from demo import (
    ANONYMOUS_SCREEN_DESCRIPTION,
    INTRODUCTION_SCREEN_WITH_NAME_DESCRIPTION,
    INTRODUCTION_SCREEN_WITHOUT_NAME_DESCRIPTION,
    TYPE_NAME_STATE,
    AnonymousScreen,
    IntroductionScreen,
)

_TEST_NAME = 'Hammett'


class HammettMultiStateBotTests(BaseTestCase):
    """The class contains the tests for HammettMultiStateBot."""

    def get_message(self):
        """Return the `Message` object with text attribute for testing purposes."""
        return Message(
            self.message_id,
            datetime.now(tz=timezone.utc),
            self.chat,
            from_user=self.user,
            text=_TEST_NAME,
        )

    @catch_render_config()
    async def test_anonymous_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await AnonymousScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=ANONYMOUS_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('Introduce Yourself', IntroductionScreen,
                       source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/multi_state_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    async def test_changing_states_after_calling_move_along_route_handler(self):
        """Test calling the `move_along_route` handler to get the changed state."""
        # Sometimes it's necessary to set context.user_data['current_state'] in tests
        # because the initial state is None, which isn't registered in
        # the IntroductionScreen.routes attribute.
        self.context.user_data['current_state'] = DEFAULT_STATE

        state = await IntroductionScreen().move_along_route(self.update, self.context)
        self.assertEqual(state, TYPE_NAME_STATE)

    @catch_render_config()
    async def test_introduction_screen_render_after_calling_handle_text_input_handler(self, actual):
        """Test calling the `handle_text_input` handler to get the final render config."""
        await IntroductionScreen().handle_text_input(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=INTRODUCTION_SCREEN_WITH_NAME_DESCRIPTION.format(name=_TEST_NAME),
            keyboard=[
                [Button('Change Name', IntroductionScreen,
                       source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/multi_state_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_introduction_screen_render_after_calling_move_along_route_handler(self, actual):
        """Test calling the `move_along_route` handler to get the final render config."""
        await IntroductionScreen().move_along_route(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=INTRODUCTION_SCREEN_WITHOUT_NAME_DESCRIPTION,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()
