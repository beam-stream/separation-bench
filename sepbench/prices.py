"""`prices.toml`, read once.

Every published rate lives in that file with its source and the date it was read. The adapters
bill a run with the same figure the report prices it with, so neither carries a rate of its own:
a vendor's price change is one edit, in the file that records where the number came from.
"""

from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def table() -> dict:
    return tomllib.loads((ROOT / "prices.toml").read_text(encoding="utf-8"))


def api(key: str) -> dict:
    """One `[api.<key>]` row. A missing row is fatal: a run that cannot be priced is a run whose
    cost would be invented later."""
    row = table().get("api", {}).get(key)
    if row is None:
        raise SystemExit(f"prices.toml has no [api.{key}]; add it with its source and read date")
    return row


def usd_per_minute(key: str, field: str = "usd_per_minute") -> float:
    row = api(key)
    if field not in row:
        raise SystemExit(f"prices.toml [api.{key}] has no {field}")
    return float(row[field])
