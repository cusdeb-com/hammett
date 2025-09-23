"""The module contains the tests for the StartMarker."""

from hammett.start_marker import StartMarker
from hammett.test.base import BaseTestCase

_BOOK_ID = '1'

_EXTRA_VALUE = 'extra_value'

_SOURCE = 'inbio'


class StartMarkerTests(BaseTestCase):
    """The class implements the tests for the StartMarker."""

    def test_duplicate_keys_last_value_wins(self):
        """Test the case when duplicated keys keep the last value."""
        start_marker = StartMarker(f'/start book={_BOOK_ID}=book={int(_BOOK_ID) + 1}')

        self.assertEqual(start_marker['book'], str(int(_BOOK_ID) + 1))

    def test_empty_markers_views_are_empty(self):
        """Test the case when no markers are provided and views are empty."""
        start_marker = StartMarker('/start ')

        self.assertEqual(len(start_marker.items()), 0)
        self.assertEqual(len(start_marker.keys()), 0)
        self.assertEqual(len(start_marker.values()), 0)

    def test_getitem_raises_key_error_for_unknown_key(self):
        """Test the case when requesting an unknown key raises KeyError."""
        start_marker = StartMarker(f'/start book={_BOOK_ID}')

        with self.assertRaises(KeyError):
            start_marker['unknown']

    def test_getting_more_than_one_start_marker(self):
        """Test getting more than one start marker."""
        start_marker = StartMarker(f'/start {_SOURCE}=book={_BOOK_ID}')
        book_id = start_marker['book']
        source = start_marker['source']

        self.assertEqual(book_id, _BOOK_ID)
        self.assertEqual(source, _SOURCE)

    def test_getting_only_one_start_marker_ignoring_others(self):
        """Test getting only one start-marker ignoring others."""
        start_marker = StartMarker(f'/start {_SOURCE}=book={_BOOK_ID}=extra={_EXTRA_VALUE}')
        extra = start_marker['extra']

        self.assertEqual(extra, _EXTRA_VALUE)

    def test_getting_start_marker_which_is_not_source(self):
        """Test getting a start-marker which is not a source."""
        start_marker = StartMarker(f'/start book={_BOOK_ID}')
        book_id = start_marker['book']

        self.assertEqual(book_id, _BOOK_ID)

    def test_getting_start_marker_which_is_source(self):
        """Test getting a start-marker which is a source."""
        start_marker = StartMarker(f'/start {_SOURCE}')
        source = start_marker['source']

        self.assertEqual(source, _SOURCE)

    def test_getting_start_markers_without_any_markers(self):
        """Test getting start-markers without any markers."""
        start_marker = StartMarker('/start ')

        with self.assertRaises(KeyError):
            start_marker['source']

    def test_items_keys_values_with_multiple_markers(self):
        """Test the case when items, keys and values return correct collections."""
        start_marker = StartMarker(f'/start source={_SOURCE}=book={_BOOK_ID}=extra={_EXTRA_VALUE}')

        self.assertEqual(dict(start_marker.items()), {
            'source': _SOURCE,
            'book': _BOOK_ID,
            'extra': _EXTRA_VALUE,
        })
        self.assertSetEqual(set(start_marker.keys()), {'source', 'book', 'extra'})
        self.assertSetEqual(set(start_marker.values()), {_SOURCE, _BOOK_ID, _EXTRA_VALUE})

    def test_trimming_leading_and_trailing_equals(self):
        """Test the case when leading and trailing '=' are ignored."""
        start_marker = StartMarker(f'/start =book={_BOOK_ID}=')

        self.assertEqual(start_marker['book'], _BOOK_ID)
        with self.assertRaises(KeyError):
            start_marker['source']
