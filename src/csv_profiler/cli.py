"""
Typer CLI for CSV Profiler
"""

import json
import time
from pathlib import Path

import typer

from csv_profiler.io import read_csv_rows
from csv_profiler.profiling import profile_rows
from csv_profiler.render import build_markdown_report

app = typer.Typer(help="CSV Profiler CLI")


def _write_json_report(profile_data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)


def _write_markdown_report(profile_data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    md = build_markdown_report(profile_data)
    output_path.write_text(md, encoding="utf-8")


@app.command()
def profile(
    file_path: Path = typer.Argument(..., help="Path to CSV file"),
    out_dir: Path = typer.Option(Path("outputs"), "--out-dir", "-o", help="Output directory"),
    report_name: str = typer.Option("profile", "--report-name", "-n", help="Report base name"),
    format: str = typer.Option(
        "both",
        "--format",
        help="Output format: json, markdown, both",
        case_sensitive=False,
    ),
):
    """
    Profile a CSV file and generate reports (JSON + Markdown).
    """
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    fmt = format.lower().strip()
    if fmt not in {"json", "markdown", "both"}:
        raise typer.BadParameter("format must be one of: json, markdown, both")

    # Keep same naming style: profile-sample.json / profile-sample.md by default
    base_name = report_name
    if report_name == "profile":
        base_name = f"{report_name}-{file_path.stem}"

    typer.echo(f"Profiling: {file_path.as_posix()}")
    t0 = time.perf_counter()

    rows = read_csv_rows(file_path)
    typer.echo(f"Read {len(rows)} rows")

    profile_data = profile_rows(rows)

    if fmt in {"json", "both"}:
        json_path = out_dir / f"{base_name}.json"
        _write_json_report(profile_data, json_path)
        typer.echo(f"JSON report saved to: {json_path}")

    if fmt in {"markdown", "both"}:
        md_path = out_dir / f"{base_name}.md"
        _write_markdown_report(profile_data, md_path)
        typer.echo(f"Markdown report saved to: {md_path}")

    dt_ms = (time.perf_counter() - t0) * 1000
    typer.echo(f"Profiling took: {dt_ms:.2f}ms")

    # Optional: print summary if your profile_data has these keys
    try:
        typer.echo("\nSummary:")
        typer.echo(f" Rows: {profile_data.get('rows')}")
        typer.echo(f" Columns: {profile_data.get('columns')}")
        cols = profile_data.get("column_profiles") or profile_data.get("profiles") or []
        for c in cols:
            name = c.get("name")
            typ = c.get("type") or c.get("inferred_type")
            missing = c.get("missing")
            missing_pct = c.get("missing_pct")
            typer.echo(f"  {name}: {typ} ({missing} missing, {missing_pct}%)")
    except Exception:
        pass


if __name__ == "__main__":
    app()


