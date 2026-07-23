from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

DEFAULT_DICTIONARY_PATH = (
    Path(__file__).resolve().parents[1] / "references" / "edb-levels.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search the local EDB hierarchy dictionary by keyword.",
    )
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Keyword to match. Repeat the flag to require multiple keywords.",
    )
    parser.add_argument("--level-id", help="Filter by full or partial edb_level_id.")
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum rows to print or export after filtering.",
    )
    parser.add_argument("--output", help="Optional .csv output path.")
    parser.add_argument(
        "--dictionary",
        default=str(DEFAULT_DICTIONARY_PATH),
        help="Override dictionary CSV path.",
    )
    return parser.parse_args()


def load_dictionary(path: str) -> pd.DataFrame:
    dataframe = pd.read_csv(path, dtype=str).fillna("")
    dataframe.columns = [column.strip() for column in dataframe.columns]
    return dataframe


def filter_dataframe(
    dataframe: pd.DataFrame,
    *,
    keywords: list[str],
    level_id: str | None,
) -> pd.DataFrame:
    if not keywords and not level_id:
        raise ValueError("provide at least one --keyword or --level-id filter")

    search_columns = [column for column in dataframe.columns if column != "edb_level_id"]
    haystack = dataframe[search_columns].agg(" ".join, axis=1).str.lower()
    mask = pd.Series(True, index=dataframe.index)

    for keyword in keywords:
        pattern = re.escape(keyword.lower())
        mask &= haystack.str.contains(pattern, regex=True)

    if level_id:
        mask &= dataframe["edb_level_id"].str.contains(level_id, case=False, regex=False)

    return dataframe.loc[mask].reset_index(drop=True)


def main() -> int:
    args = parse_args()
    dataframe = load_dictionary(args.dictionary)

    try:
        filtered = filter_dataframe(
            dataframe,
            keywords=args.keyword,
            level_id=args.level_id,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    limited = filtered.head(args.limit)

    if args.output:
        output_path = Path(args.output).expanduser()
        limited.to_csv(output_path, index=False, encoding="utf-8-sig")

    if limited.empty:
        print("(no matching EDB levels)")
        return 0

    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(limited.to_string(index=False))

    if len(filtered) > len(limited):
        print(f"\n... {len(filtered) - len(limited)} more rows not shown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
