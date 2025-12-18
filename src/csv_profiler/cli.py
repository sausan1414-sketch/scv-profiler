"""
Command-line interface for CSV Profiler.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import typer

from csv_profiler.io import read_csv_rows
from csv_profiler.profiling import profile_rows
from csv_profiler.render import build_markdown_report

app = typer.Typer(help="CSV Profiler - Analyze and profile CSV files")


@app.command()
def profile(
    file_path: Path = typer.Argument(..., help="Path to the CSV file to profile"),
    out_dir: Path = typer.Option(Path("outputs"), "--out-dir", "-o", help="Output directory for reports"),
    report_name: str = typer.Option("profile", "--report-name", "-n", help="Report base name"),
    format: str = typer.Option("both", "--format", "-f", help="Output format: json, markdown, or both"),
) -> None:
    """Profile a CSV file and generate reports."""
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    fmt = format.lower().strip()
    if fmt not in {"json", "markdown", "both"}:
        raise typer.BadParameter("format must be one of: json, markdown, both")

    base_name = report_name
    if report_name == "profile":
        base_name = f"{report_name}-{file_path.stem}"

    typer.echo(f"Profiling: {file_path}")
    t0 = time.perf_counter()

    rows = read_csv_rows(file_path)
    typer.echo(f"Read {len(rows)} rows")

    data = profile_rows(rows)

    if fmt in {"json", "both"}:
        json_path = out_dir / f"{base_name}.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        typer.echo(f"JSON report saved to: {json_path}")

    if fmt in {"markdown", "both"}:
        md_path = out_dir / f"{base_name}.md"
        md_path.write_text(build_markdown_report(data), encoding="utf-8")
        typer.echo(f"Markdown report saved to: {md_path}")

    dt_ms = (time.perf_counter() - t0) * 1000
    typer.echo(f"Profiling took: {dt_ms:.2f}ms")

    if __name__ == "__main__":
    app()






