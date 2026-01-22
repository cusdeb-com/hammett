"""Tests for stopwatch stats processors."""

# ruff: noqa: ASYNC230, ASYNC240, SLF001

import json
import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from hammett.core.handlers import get_handler_name
from hammett.stopwatch.stats import BaseStatsProcessor, JsonStatsProcessor, PrintStatsProcessor
from hammett.test.base import BaseTestCase
from tests.base import BaseTestScreenWithHandler


class AlternateTestScreen(BaseTestScreenWithHandler):
    """The class represents an alternate screen for stopwatch stats tests."""


class StopWatchStatsProcessorTests(BaseTestCase):
    """The class implements tests for the stopwatch stats processors."""

    async def test_base_stats_processor_stores_handler_and_stats_and_is_abstract(self):
        """Test that BaseStatsProcessor stores values and keeps process abstract."""
        handler = BaseTestScreenWithHandler().handler
        stats = {
            'cpu_time': 0.0,
            'select_time': 0.0,
            'other_io_time': 0.0,
            'real_time': 0.0,
        }
        processor = BaseStatsProcessor(handler, stats)

        self.assertIs(processor.handler, handler)
        self.assertIs(processor.stats, stats)

        with self.assertRaises(NotImplementedError):
            await processor.process()

    async def test_print_stats_processor_prints_expected_message(self):
        """Test that PrintStatsProcessor outputs formatted stats."""
        stats = {
            'cpu_time': 1.0,
            'select_time': 0.5,
            'other_io_time': 0.25,
            'real_time': 2.0,
        }

        handler_name = get_handler_name(BaseTestScreenWithHandler().handler)
        processor = PrintStatsProcessor(BaseTestScreenWithHandler().handler, stats)

        buffer = StringIO()
        with redirect_stdout(buffer):
            await processor.process()

        output = buffer.getvalue()

        expected = (
            f'{handler_name}:\n'
            '  CPU time: 1.0\n'
            '  Select time: 0.5\n'
            '  Other IO time: 0.25\n'
            '  Real time: 2.0\n'
            '\n'
        )
        self.assertEqual(expected, output)

    async def test_json_stats_processor_collects_and_dumps_stats(self):
        """Test that JsonStatsProcessor aggregates stats per handler and writes JSON."""
        JsonStatsProcessor._all_stats = {}

        with TemporaryDirectory() as tmpdir:
            previous_cwd = Path.cwd()
            os.chdir(tmpdir)

            primary_handler = BaseTestScreenWithHandler().handler
            secondary_handler = AlternateTestScreen().handler
            stats_one = {
                'cpu_time': 1.0,
                'select_time': 0.0,
                'other_io_time': 0.5,
                'real_time': 1.5,
            }
            stats_two = {
                'cpu_time': 2.0,
                'select_time': 1.0,
                'other_io_time': 0.0,
                'real_time': 3.0,
            }

            try:
                processor_one = JsonStatsProcessor(primary_handler, stats_one)
                processor_two = JsonStatsProcessor(secondary_handler, stats_two)

                await processor_one.process()
                await processor_two.process()

                expected_in_memory = {
                    get_handler_name(secondary_handler): [stats_one, stats_two],
                }

                self.assertEqual(JsonStatsProcessor._all_stats, expected_in_memory)

                await JsonStatsProcessor.on_exit()

                output_file = Path('handler_stats.json')
                self.assertTrue(output_file.exists())

                with output_file.open(encoding='utf-8') as fp:
                    dumped = json.load(fp)
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(dumped, expected_in_memory)
