# TV Maze Show Summary

This program downloads one page of TV shows and summarizes them by genre, language, premiere decade, and broadcast network. The summary is a quicker way to see what that page of the catalog is made of than reading each show record.

## Data source

https://api.tvmaze.com/shows?page=0

One record is one TV show: name, genres, language, rating, premiere date, and network or web channel. Page 0 returns 240 shows, which is above the 50-record minimum. Later pages exist, but this program uses only the first page.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python records.py
```

The program writes `summary.json` in the current directory. If the download fails, it prints `Download failed: ...` and exits without a traceback.

## Example output

```json
{
  "source_url": "https://api.tvmaze.com/shows?page=0",
  "records_processed": 240,
  "shows_per_genre": {
    "counts": {
      "Drama": 154,
      "Comedy": 66,
      "Crime": 57
    },
    "shows_without_genre": 5
  },
  "average_rating_by_language": {
    "averages": {
      "English": 7.58,
      "Japanese": 7.88
    },
    "shows_excluded": 4
  }
}
```

Drama is the most common genre on this page. Genre counts add up to more than 240 because a show can belong to several genres. English-language shows average 7.58, based on the 236 shows that have both a language and a rating. The four shows with no rating are left out of that average.

## Data quirks

- A show can list several genres, or none. Each listed genre is counted once per show. The five shows with an empty genre list are stored in `shows_without_genre` and are not given a fake genre.
- The same genre could appear twice on one show. Those repeats are collapsed with a set before counting.
- Four shows have `"rating": {"average": null}`. They are excluded from the language averages. Treating the missing value as 0 would make every language look worse than it is.
- Premiere dates are strings such as `"2013-06-24"`. Only the year is used, and only when the first four characters are a year between 1900 and 2100. A missing or broken date is excluded from the decade counts. On this page every show had a usable date, so `shows_excluded` is 0.
- Eleven shows have `"network": null` because they were released on a web channel (Netflix, Hulu, and others). They are counted as web-only shows. They are not assigned a country or a stand-in network name. None of the shows on this page lacked both a network and a web channel.

## Design choices

- **List.** The download is a list of show records, and `build_summary` keeps only the entries that are dictionaries with a list comprehension. Order from the API is preserved until an aggregation sorts its own result.
- **Dictionary.** Each aggregation groups by a field: genre, language, or decade. A dictionary is the right structure because the key is the group and the value is the count or the average.
- **Set.** Genres on a single show are put in a set so a repeated label is not counted twice. Web channel names for shows with no network are also collected in a set so each channel appears once.
- **Tuple.** While computing an average, each language stores a `(total, count)` tuple. The two numbers have to stay together, and a tuple is enough because nothing else needs to be attached to them.

## Known limitations

The program reads only page 0, so the averages describe that page, not every show on TV Maze. Japanese is only four shows, so that average moves a lot if one rating changes. Ratings are TV Maze user scores. The summary does not include show titles, which would make the file much longer without changing the groupings.
