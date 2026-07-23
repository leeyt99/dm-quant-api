from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from dm_quant_client import DMQuantApiError, create_client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query any DM Quant API endpoint with local credentials.",
    )
    parser.add_argument("--api-path", required=True, help="Full DM API path.")
    payload_group = parser.add_mutually_exclusive_group()
    payload_group.add_argument(
        "--data-json",
        help="Inline JSON payload. Prefer single quotes around the whole string in shell.",
    )
    payload_group.add_argument(
        "--data-file",
        help="Path to a JSON file containing the request payload.",
    )
    parser.add_argument(
        "--return-type",
        choices=["dataframe", "dict"],
        default="dataframe",
        help="Return a DataFrame preview or the raw dict/list structure.",
    )
    parser.add_argument("--output", help="Write output to .csv, .xlsx, or .json.")
    parser.add_argument(
        "--head",
        type=int,
        default=20,
        help="Rows to print for DataFrame preview. Use 0 to print all rows.",
    )
    parser.add_argument("--app-key", help="Override app key.")
    parser.add_argument("--app-secret", help="Override app secret / SM4 key.")
    parser.add_argument("--credentials-file", help="Override credentials file path.")
    parser.add_argument("--base-url", help="Override API base URL.")
    parser.add_argument(
        "--no-pythonic",
        action="store_true",
        help="Disable snake_case to camelCase request conversion.",
    )
    return parser.parse_args()


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.data_file:
        return json.loads(Path(args.data_file).read_text(encoding="utf-8"))
    if args.data_json:
        return json.loads(args.data_json)
    return {}


def write_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    suffix = output_path.suffix.lower()
    if suffix == ".xlsx":
        df.to_excel(output_path, index=False)
        return
    if suffix in {".csv", ".txt"}:
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return
    raise ValueError("DataFrame output must use .csv, .txt, or .xlsx")


def write_dict(data: Any, output_path: Path) -> None:
    suffix = output_path.suffix.lower()
    if suffix != ".json":
        raise ValueError("dict output must use a .json path")
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_dataframe(df: pd.DataFrame, head: int) -> None:
    if df.empty:
        print("(empty DataFrame)")
        return

    preview = df if head == 0 else df.head(head)
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(preview.to_string(index=False))

    if head > 0 and len(df) > head:
        print(f"\n... {len(df) - head} more rows not shown")


def main() -> int:
    args = parse_args()
    payload = load_payload(args)

    client = create_client(
        app_key=args.app_key,
        app_secret=args.app_secret,
        credentials_file=args.credentials_file,
        base_url=args.base_url,
        pythonic=not args.no_pythonic,
    )

    try:
        result = client.post_data(
            payload,
            args.api_path,
            return_type=args.return_type,
        )
    except (DMQuantApiError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.output:
        output_path = Path(args.output).expanduser()
        if args.return_type == "dataframe":
            write_dataframe(result, output_path)
        else:
            write_dict(result, output_path)

    if args.return_type == "dataframe":
        print_dataframe(result, args.head)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
