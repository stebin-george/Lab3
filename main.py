"""Wire the package together and print success or a download error."""

import sys

from tvsummary import (
    DownloadError,
    ResponseError,
    TvMazeSource,
    build_summary,
    write_summary,
)
from tvsummary.config import OUTPUT, SOURCE_URL, TIMEOUT_SECONDS


def main():
    """Download shows, aggregate them, and write the summary."""
    try:
        shows, skipped = TvMazeSource(SOURCE_URL, TIMEOUT_SECONDS).fetch()
    except DownloadError as exc:
        print(f"Download failed: {exc}")
        print("Check your connection and run the program again.")
        sys.exit(1)
    except ResponseError as exc:
        print(f"Download failed: the response could not be used ({exc}).")
        sys.exit(1)

    if len(shows) + skipped < 50:
        print(
            "Download failed: expected at least 50 shows, "
            f"received {len(shows) + skipped}."
        )
        sys.exit(1)

    summary = build_summary(shows, skipped)
    write_summary(summary, OUTPUT)
    print(f"Wrote {summary['records_processed']} shows to {OUTPUT}.")


if __name__ == "__main__":
    main()
