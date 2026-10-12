"""Tests that use hand-made shows and do not touch the network."""

import unittest

from tvsummary import AverageRatingByLanguage, Show, ShowsPerGenre


def _show(**overrides):
    raw = {
        "name": "Example",
        "genres": ["Drama"],
        "language": "English",
        "rating": {"average": 8},
        "premiered": "2013-06-24",
        "network": {"name": "CBS"},
        "webChannel": None,
    }
    raw.update(overrides)
    return Show(raw)


class ShowTests(unittest.TestCase):
    """Show cleans missing and repeated values when it is created."""

    def test_missing_rating_and_genres_are_left_empty(self):
        show = Show(
            {
                "name": "Utopia",
                "genres": [],
                "language": "English",
                "rating": {"average": None},
                "premiered": "2014-09-07",
                "network": None,
                "webChannel": {"name": "  "},
            }
        )
        self.assertIsNone(show.rating)
        self.assertEqual(show.genres, frozenset())
        self.assertIsNone(show.network_name)
        self.assertIsNone(show.web_channel)
        self.assertEqual(str(show), "Utopia (2014)")

    def test_repeated_genres_are_stored_once(self):
        show = _show(genres=["Drama", " Drama ", "Drama", ""])
        self.assertEqual(show.genres, frozenset({"Drama"}))
        self.assertEqual(show.rating, 8.0)
        self.assertEqual(show.premiere_year, 2013)

    def test_unreadable_premiere_date_is_dropped(self):
        show = _show(premiered="not-a-date", name="   ")
        self.assertIsNone(show.premiere_year)
        self.assertEqual(str(show), "Untitled show")


class AggregationTests(unittest.TestCase):
    """Aggregations run through the shared compute method."""

    def test_genre_and_rating_results_skip_missing_values(self):
        shows = [
            _show(genres=["Drama", "Crime"], rating={"average": 8}),
            _show(name="No Genre", genres=[], rating={"average": None}),
        ]
        aggregations = [ShowsPerGenre(), AverageRatingByLanguage()]
        genre_result, rating_result = [item.compute(shows) for item in aggregations]
        self.assertEqual(genre_result["shows_without_genre"], 1)
        self.assertEqual(genre_result["counts"]["Drama"], 1)
        self.assertEqual(genre_result["counts"]["Crime"], 1)
        self.assertEqual(rating_result["shows_excluded"], 1)
        self.assertEqual(rating_result["averages"]["English"], 8.0)
