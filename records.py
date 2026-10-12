"""Download TV Maze shows and write a grouped summary to JSON."""

import json
import sys
from pathlib import Path

import requests

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
OUTPUT = Path("summary.json")
TIMEOUT_SECONDS = 15


def fetch_records(url):
    """Download the show list and return it as a list of dicts."""
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Expected a JSON list of show records.")
    return payload


def shows_per_genre(records):
    """Count how many shows list each genre.

    A show with several genres is counted once in each of them. A genre
    repeated on the same show is counted once, using a set. Shows with no
    genres are reported separately and are not filed under a placeholder.
    """
    counts = {}
    without_genre = 0
    for show in records:
        genres = show.get("genres")
        if not isinstance(genres, list):
            without_genre += 1
            continue
        names = {genre.strip() for genre in genres if isinstance(genre, str) and genre.strip()}
        if not names:
            without_genre += 1
            continue
        for genre in names:
            counts[genre] = counts.get(genre, 0) + 1
    ordered = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    return {"counts": ordered, "shows_without_genre": without_genre}


def average_rating_by_language(records):
    """Return the mean rating for each language.

    A missing rating is skipped. It is not treated as zero, which would
    drag the average down. Shows with no language are skipped the same way.
    Totals are kept as (sum, count) tuples so the two numbers stay paired.
    """
    totals = {}
    skipped = 0
    for show in records:
        language = show.get("language")
        rating = show.get("rating")
        average = rating.get("average") if isinstance(rating, dict) else None
        if not isinstance(language, str) or not language.strip():
            skipped += 1
            continue
        if not isinstance(average, (int, float)):
            skipped += 1
            continue
        total, count = totals.get(language, (0.0, 0))
        totals[language] = (total + float(average), count + 1)

    averages = {
        language: round(total / count, 2)
        for language, (total, count) in sorted(totals.items())
    }
    return {
        "averages": averages,
        "shows_excluded": skipped,
    }


def shows_premiered_per_decade(records):
    """Count shows by the decade of their premiere date.

    A missing or unreadable premiere date is excluded rather than placed
    in an unknown decade.
    """
    counts = {}
    skipped = 0
    for show in records:
        year = _premiere_year(show.get("premiered"))
        if year is None:
            skipped += 1
            continue
        decade = f"{(year // 10) * 10}s"
        counts[decade] = counts.get(decade, 0) + 1
    return {
        "counts": dict(sorted(counts.items())),
        "shows_excluded": skipped,
    }


def _premiere_year(value):
    """Return a plausible premiere year, or None when the date is unusable."""
    if not isinstance(value, str) or len(value) < 4 or not value[:4].isdigit():
        return None
    year = int(value[:4])
    if year < 1900 or year > 2100:
        return None
    return year


def shows_without_broadcast_network(records):
    """Describe shows that have no traditional network.

    Web-only shows are not assigned a country or a made-up network name.
    Their channel names are collected in a set so each name appears once.
    """
    web_channels = set()
    web_only = 0
    missing_both = 0
    for show in records:
        network = show.get("network")
        if isinstance(network, dict) and isinstance(network.get("name"), str) and network["name"].strip():
            continue
        channel = show.get("webChannel")
        channel_name = channel.get("name") if isinstance(channel, dict) else None
        if isinstance(channel_name, str) and channel_name.strip():
            web_only += 1
            web_channels.add(channel_name.strip())
        else:
            missing_both += 1
    return {
        "web_only_shows": web_only,
        "web_channels": sorted(web_channels),
        "shows_with_neither": missing_both,
    }


def build_summary(records):
    """Combine the aggregations into one dict ready to write."""
    usable = [show for show in records if isinstance(show, dict)]
    return {
        "source_url": SOURCE_URL,
        "records_processed": len(usable),
        "records_skipped_malformed": len(records) - len(usable),
        "shows_per_genre": shows_per_genre(usable),
        "average_rating_by_language": average_rating_by_language(usable),
        "shows_premiered_per_decade": shows_premiered_per_decade(usable),
        "shows_without_broadcast_network": shows_without_broadcast_network(usable),
    }


def write_summary(summary, path):
    """Write the summary to a JSON file."""
    destination = Path(path)
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    destination.write_text(text, encoding="utf-8")


def main():
    """Download shows, aggregate them, and write summary.json."""
    try:
        records = fetch_records(SOURCE_URL)
    except requests.RequestException as exc:
        print(f"Download failed: {exc}")
        print("Check your connection and run the program again.")
        sys.exit(1)
    except ValueError as exc:
        print(f"Download failed: the response could not be used ({exc}).")
        sys.exit(1)

    if len(records) < 50:
        print(f"Download failed: expected at least 50 shows, received {len(records)}.")
        sys.exit(1)

    summary = build_summary(records)
    write_summary(summary, OUTPUT)
    print(f"Wrote {summary['records_processed']} shows to {OUTPUT}.")


if __name__ == "__main__":
    main()
