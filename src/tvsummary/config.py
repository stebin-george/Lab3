"""Settings for the TV Maze summary. Change them here only."""

from pathlib import Path

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
TIMEOUT_SECONDS = 15
OUTPUT = Path("data/processed/summary.json")
