"""One TV Maze show, with missing values cleaned at creation."""


class Show:
    """A single show record.

    Missing ratings, empty genres, and unreadable dates are normalized
    here so later code can trust the attributes.
    """

    def __init__(self, raw):
        """Store a cleaned show from one API object."""
        if not isinstance(raw, dict):
            raise TypeError("A show record must be a dictionary.")
        name = raw.get("name")
        self.name = name if isinstance(name, str) else None
        self.genres = self._genres(raw.get("genres"))
        self.language = self._language(raw.get("language"))
        self.rating = self._rating(raw.get("rating"))
        self.premiere_year = self._premiere_year(raw.get("premiered"))
        self.network_name = self._nested_name(raw.get("network"))
        self.web_channel = self._nested_name(raw.get("webChannel"))

    def __str__(self):
        """Return the title and premiere year when the year is known."""
        if isinstance(self.name, str) and self.name.strip():
            title = self.name.strip()
        else:
            title = "Untitled show"
        if self.premiere_year is None:
            return title
        return f"{title} ({self.premiere_year})"

    @staticmethod
    def _genres(value):
        """Return the show's genres, with blanks and repeats removed."""
        if not isinstance(value, list):
            return frozenset()
        return frozenset(
            genre.strip()
            for genre in value
            if isinstance(genre, str) and genre.strip()
        )

    @staticmethod
    def _language(value):
        """Return the language text, or None when it is missing."""
        if not isinstance(value, str) or not value.strip():
            return None
        return value

    @staticmethod
    def _rating(value):
        """Return the average rating, or None when it is missing."""
        average = value.get("average") if isinstance(value, dict) else None
        if isinstance(average, bool) or not isinstance(average, (int, float)):
            return None
        return float(average)

    @staticmethod
    def _premiere_year(value):
        """Return a plausible premiere year, or None when the date is unusable."""
        if not isinstance(value, str) or len(value) < 4 or not value[:4].isdigit():
            return None
        year = int(value[:4])
        if year < 1900 or year > 2100:
            return None
        return year

    @staticmethod
    def _nested_name(value):
        """Return a stripped network or channel name, or None."""
        if not isinstance(value, dict):
            return None
        name = value.get("name")
        if not isinstance(name, str) or not name.strip():
            return None
        return name.strip()
