"""Group shows. Each grouping is a subclass of Aggregation."""


class Aggregation:
    """One grouping of shows.

    Subclasses override compute. Callers use that method without checking
    which subclass they are holding.
    """

    def __init__(self, name):
        """Store the summary key this aggregation fills."""
        self.name = name

    def compute(self, shows):
        """Return this aggregation's result for the given shows."""
        raise NotImplementedError


class ShowsPerGenre(Aggregation):
    """Count how many shows list each genre."""

    def __init__(self):
        """Name this aggregation shows_per_genre."""
        super().__init__("shows_per_genre")

    def compute(self, shows):
        """Count each genre once per show, and count shows that have none."""
        counts = {}
        without_genre = 0
        for show in shows:
            if not show.genres:
                without_genre += 1
                continue
            for genre in show.genres:
                counts[genre] = counts.get(genre, 0) + 1
        ordered = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
        return {"counts": ordered, "shows_without_genre": without_genre}


class AverageRatingByLanguage(Aggregation):
    """Average the rating of shows that have both a language and a rating."""

    def __init__(self):
        """Name this aggregation average_rating_by_language."""
        super().__init__("average_rating_by_language")

    def compute(self, shows):
        """Skip missing ratings instead of treating them as zero."""
        totals = {}
        skipped = 0
        for show in shows:
            if show.language is None:
                skipped += 1
                continue
            if show.rating is None:
                skipped += 1
                continue
            total, count = totals.get(show.language, (0.0, 0))
            totals[show.language] = (total + show.rating, count + 1)
        averages = {
            language: round(total / count, 2)
            for language, (total, count) in sorted(totals.items())
        }
        return {"averages": averages, "shows_excluded": skipped}


class ShowsPremieredPerDecade(Aggregation):
    """Count shows by the decade of their premiere date."""

    def __init__(self):
        """Name this aggregation shows_premiered_per_decade."""
        super().__init__("shows_premiered_per_decade")

    def compute(self, shows):
        """Leave out shows whose premiere year could not be read."""
        counts = {}
        skipped = 0
        for show in shows:
            if show.premiere_year is None:
                skipped += 1
                continue
            decade = f"{(show.premiere_year // 10) * 10}s"
            counts[decade] = counts.get(decade, 0) + 1
        return {"counts": dict(sorted(counts.items())), "shows_excluded": skipped}


class ShowsWithoutBroadcastNetwork(Aggregation):
    """Describe shows that have no traditional network."""

    def __init__(self):
        """Name this aggregation shows_without_broadcast_network."""
        super().__init__("shows_without_broadcast_network")

    def compute(self, shows):
        """Count web-only shows without assigning them a made-up network."""
        web_channels = set()
        web_only = 0
        missing_both = 0
        for show in shows:
            if show.network_name:
                continue
            if show.web_channel:
                web_only += 1
                web_channels.add(show.web_channel)
            else:
                missing_both += 1
        return {
            "web_only_shows": web_only,
            "web_channels": sorted(web_channels),
            "shows_with_neither": missing_both,
        }
