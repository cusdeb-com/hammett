"""The module contains the tests for HammettAttachmentsBot."""

# ruff: noqa: I001

import os
import unittest
from unittest.mock import patch

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase, TestInputMediaDocument
from hammett.test.utils import catch_render_config

from demo import START_SCREEN_DESCRIPTION, AttachmentsScreen, StartScreen


class HammettAttachmentsBotTests(BaseTestCase):
    """The class contains the tests for HammettAttachmentsBot."""

    @catch_render_config()
    async def test_start_screen_render_after_calling_jump_handler(self, actual):
        """Test calling the `jump` handler to get the final render config for
        screen with the attachments.
        """
        mock_logo_1500_bytes = b'mock_logo_1500px_content'
        mock_logo_500_bytes = b'mock_logo_500px_content'
        mock_logo_200_bytes = b'mock_logo_200px_content'

        with patch.object(AttachmentsScreen, '_read_file', side_effect=[
            mock_logo_1500_bytes,
            mock_logo_500_bytes,
            mock_logo_200_bytes,
        ]):
            await AttachmentsScreen().jump(self.update, self.context)

        expected_attachments = [
            TestInputMediaDocument(
                media=mock_logo_1500_bytes,
                caption='📄 Big Hammett Logo (1500x1500 px)',
                filename='logo-1500px.png',
            ),
            TestInputMediaDocument(
                media=mock_logo_500_bytes,
                caption='📄 Medium Hammett Logo (500x500 px)',
                filename='logo-500px.png',
            ),
            TestInputMediaDocument(
                media=mock_logo_200_bytes,
                caption='📄 Small Hammett Logo (200x200 px)',
                filename='logo-200px.png',
            ),
        ]

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            attachments=expected_attachments,
            description='',
            keyboard=[],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_start_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await StartScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=START_SCREEN_DESCRIPTION,
            keyboard=[
                [Button(
                    '📄 Source Code',
                    'https://github.com/cusdeb-com/hammett/tree/main/demos/attachments_bot',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button(
                    '🎸 Hammett Homepage',
                    'https://github.com/cusdeb-com/hammett',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()
