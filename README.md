# TV Maze Show Summary

This package downloads one page of TV shows and summarizes them by genre, language, premiere decade, and broadcast network. The summary is the same one Lab 02 produced. What changed is the structure: records, downloading, grouping, and writing now live in separate modules.

## Data source

https://api.tvmaze.com/shows?page=0

One record is one TV show: name, genres, language, rating, premiere date, and network or web channel. Page 0 returns 240 shows. A show may list several genres or none, a rating may be missing, and a web-only show has no network. `Show` cleans those cases when it is created.

## Setup

```bash
conda env create -f environment.yml
conda activate tvsummary
pip install -r requirements.txt
pip install -e .
```

## Run

```bash
python main.py
```

The program writes `data/processed/summary.json`. If the download fails, it prints `Download failed: ...` and exits without a traceback.

## Test

```bash
python -m unittest discover -s tests
```

## Layout

- `main.py` starts the program, prints errors, and connects the other pieces.
- `src/tvsummary/__init__.py` re-exports the public classes so `from tvsummary import Show` works.
- `src/tvsummary/config.py` holds the source URL, timeout, and output path, which are the settings that change between runs.
- `src/tvsummary/models.py` holds `Show`, because cleaning one record is a different job from counting many of them.
- `src/tvsummary/sources.py` downloads the page. It is separate so it is the only module that imports `requests`.
- `src/tvsummary/aggregations.py` holds the groupings. They are separate so each one can be run on a list of shows without downloading or writing.
- `src/tvsummary/report.py` builds the summary dictionary and writes the JSON file.
- `tests/test_models.py` checks `Show` and two aggregations with hand-made records and no network.

## What moved where

| Lab 02 | Lab 03 |
| --- | --- |
| `fetch_records` | `TvMazeSource.fetch` in `sources.py` |
| `shows_per_genre` | `ShowsPerGenre.compute` in `aggregations.py` |
| `average_rating_by_language` | `AverageRatingByLanguage.compute` in `aggregations.py` |
| `shows_premiered_per_decade` | `ShowsPremieredPerDecade.compute` in `aggregations.py` |
| `_premiere_year` | `Show._premiere_year` in `models.py` |
| `shows_without_broadcast_network` | `ShowsWithoutBroadcastNetwork.compute` in `aggregations.py` |
| `build_summary` | `build_summary` in `report.py` |
| `write_summary` | `write_summary` in `report.py` |
| `main` | `main` in `main.py` |

## Design choices

`Show` exists so every missing or malformed value is handled in one place. A missing rating becomes `None`, genres are stored once in a set, and an unreadable premiere date becomes `None`. The aggregations then read those attributes instead of repeating the checks.

`TvMazeSource` exists only to download. It returns `Show` objects, not raw dictionaries, and turns network or HTTP failures into `DownloadError` so `main.py` can print a message without importing `requests`.

`Aggregation` is the base class. It stores the summary key and defines `compute`. `ShowsPerGenre`, `AverageRatingByLanguage`, `ShowsPremieredPerDecade`, and `ShowsWithoutBroadcastNetwork` each override `compute`. `build_summary` keeps those objects in a list and calls `compute` on each one. It never checks which subclass it has. Adding another grouping means writing one new subclass and appending an instance to that list.

## Known limitations

The package reads only page 0, so the averages describe that page, not every show on TV Maze. Japanese is only four shows, so that average moves if one rating changes. Ratings are TV Maze user scores. The summary does not include show titles.
