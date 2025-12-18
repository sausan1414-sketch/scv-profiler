"""
Profiling functions
"""

from typing import List, Dict, Any
from .io import is_missing, try_float


def check_empty(value) -> str:
    """D1 Exercise 2: Check if value is empty/falsy"""
    return "empty" if not bool(value) else "not empty"


def count_missing(rows: List[Dict[str, str]]) -> Dict[str, int]:
    """D1 Exercise 5: Count missing values per column"""
    if not rows:
        return {}

    columns = list(rows[0].keys())
    missing = {col: 0 for col in columns}

    for row in rows:
        for col in columns:
            v = row.get(col, "")
            if is_missing(v):
                missing[col] += 1

    return missing


def basic_profile(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """D1 Exercise 6: Basic CSV profiler"""
    if not rows:
        return {"rows": 0, "columns": 0, "column_profiles": []}

    columns = list(rows[0].keys())
    missing_map = count_missing(rows)

    return {
        "rows": len(rows),
        "columns": len(columns),
        "column_profiles": [
            {
                "name": c,
                "type": "text",
                "total": len(rows),
                "missing": missing_map.get(c, 0),
                "missing_pct": (100.0 * missing_map.get(c, 0) / len(rows)) if len(rows) else 0.0,
                "unique": None,
            }
            for c in columns
        ],
    }


def infer_type(values: List[str]) -> str:
    """Infer column type (number/text)."""
    usable = [v for v in values if not is_missing(v)]
    if not usable:
        return "text"

    for v in usable:
        if try_float(v) is None:
            return "text"
    return "number"


def numeric_stats(values: List[str]) -> Dict[str, Any]:
    """Compute statistics for numeric columns."""
    total = len(values)
    usable = [v for v in values if not is_missing(v)]
    missing = total - len(usable)

    nums = []
    for v in usable:
        n = try_float(v)
        if n is not None:
            nums.append(n)

    count = len(nums)
    unique = len(set(nums))

    result: Dict[str, Any] = {
        "total": total,
        "count": count,
        "missing": missing,
        "missing_pct": (100.0 * missing / total) if total else 0.0,
        "unique": unique,
    }

    if nums:
        result["min"] = min(nums)
        result["max"] = max(nums)
        result["mean"] = sum(nums) / count if count else None
    else:
        result["min"] = None
        result["max"] = None
        result["mean"] = None

    return result


def text_stats(values: List[str], top_k: int = 3) -> Dict[str, Any]:
    """Compute statistics for text columns."""
    total = len(values)
    usable = [v for v in values if not is_missing(v)]
    missing = total - len(usable)

    counts: Dict[str, int] = {}
    for v in usable:
        counts[v] = counts.get(v, 0) + 1

    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top = [{"value": v, "count": c} for v, c in sorted_items[:top_k]]

    return {
        "total": total,
        "count": len(usable),
        "missing": missing,
        "missing_pct": (100.0 * missing / total) if total else 0.0,
        "unique": len(counts),
        "top": top,
    }


def get_column_values(rows: List[Dict[str, str]], column: str) -> List[str]:
    """Extract all values for a column."""
    return [row.get(column, "") for row in rows]


def profile_column(name: str, values: List[str]) -> Dict[str, Any]:
    """Profile a single column."""
    col_type = infer_type(values)

    stats = numeric_stats(values) if col_type == "number" else text_stats(values)

    return {
        "name": name,
        "type": col_type,
        **stats,
    }


def profile_rows(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Profile CSV rows.
    Output keys are aligned with CLI summary expectations:
      - rows: int
      - columns: int
      - column_profiles: list[dict]
    """
    if not rows:
        return {"rows": 0, "columns": 0, "column_profiles": []}

    columns = list(rows[0].keys())
    column_profiles = []

    for col in columns:
        values = get_column_values(rows, col)
        column_profiles.append(profile_column(col, values))

    return {
        "rows": len(rows),
        "columns": len(columns),
        "column_profiles": column_profiles,
    }
