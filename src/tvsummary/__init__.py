"""Summarize one page of TV Maze shows."""

from tvsummary.aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    ShowsPerGenre,
    ShowsPremieredPerDecade,
    ShowsWithoutBroadcastNetwork,
)
from tvsummary.models import Show
from tvsummary.report import build_summary, write_summary
from tvsummary.sources import DownloadError, ResponseError, TvMazeSource

__all__ = [
    "Aggregation",
    "AverageRatingByLanguage",
    "DownloadError",
    "ResponseError",
    "Show",
    "ShowsPerGenre",
    "ShowsPremieredPerDecade",
    "ShowsWithoutBroadcastNetwork",
    "TvMazeSource",
    "build_summary",
    "write_summary",
]
