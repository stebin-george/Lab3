"""Build the summary dictionary and write it to JSON."""

import json
from pathlib import Path

from tvsummary.aggregations import (
    AverageRatingByLanguage,
    ShowsPerGenre,
    ShowsPremieredPerDecade,
    ShowsWithoutBroadcastNetwork,
)
from tvsummary.config import SOURCE_URL


def build_summary(shows, skipped_malformed):
    """Combine every aggregation into one dict ready to write."""
    aggregations = [
        ShowsPerGenre(),
        AverageRatingByLanguage(),
        ShowsPremieredPerDecade(),
        ShowsWithoutBroadcastNetwork(),
    ]
    summary = {
        "source_url": SOURCE_URL,
        "records_processed": len(shows),
        "records_skipped_malformed": skipped_malformed,
    }
    for aggregation in aggregations:
        summary[aggregation.name] = aggregation.compute(shows)
    return summary


def write_summary(summary, path):
    """Write the summary to a JSON file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    destination.write_text(text, encoding="utf-8")
