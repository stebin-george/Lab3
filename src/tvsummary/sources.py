"""Download TV Maze shows. This is the only module that uses requests."""

import requests

from tvsummary.models import Show


class DownloadError(Exception):
    """The show list could not be downloaded."""


class ResponseError(Exception):
    """The server response was not a list of show records."""


class TvMazeSource:
    """Fetch shows from a TV Maze URL and return Show objects."""

    def __init__(self, url, timeout):
        """Remember where to download from and how long to wait."""
        self.url = url
        self.timeout = timeout

    def fetch(self):
        """Download the page and return shows plus a malformed-record count.

        Records that are not dictionaries are counted as malformed and are
        not turned into Show objects.
        """
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise DownloadError(str(exc)) from exc

        if not isinstance(payload, list):
            raise ResponseError("Expected a JSON list of show records.")

        shows = []
        skipped = 0
        for item in payload:
            if not isinstance(item, dict):
                skipped += 1
                continue
            shows.append(Show(item))
        return shows, skipped
