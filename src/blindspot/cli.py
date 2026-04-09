"""Click CLI: blindspot run, blindspot generate, blindspot report."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click

from .dataset import generate_dataset
from .report import generate_json_report, generate_markdown_report
from .runner import run_eval, summarize
from .types import AuthorityType, DefeatFamily


@click.group()
@click.version_option(package_name="blindspot")
def cli():
    """BlindSpot: Stress-test LLM over-refusal on defeated/unjust rules."""
    pass


@cli.command()
@click.option("--model", required=True, help="Model to evaluate (any litellm-compatible string, e.g. openai/gpt-4o)")
@click.option("--judge-model", default="openai/gpt-4o-mini", help="Model to use as judge")
@click.option("--family", multiple=True, type=click.Choice([f.value for f in DefeatFamily]), help="Filter by defeat family")
@click.option("--authority", multiple=True, type=click.Choice([a.value for a in AuthorityType]), help="Filter by authority type")
@click.option("--concurrency", default=5, type=int, help="Max parallel requests")
@click.option("--temperature", default=0.0, type=float, help="Sampling temperature")
@click.option("--max-tokens", default=1024, type=int, help="Max response tokens")
@click.option("--output", "-o", default="blindspot_results", help="Output directory for reports")
@click.option("--format", "fmt", type=click.Choice(["json", "markdown", "both"]), default="both", help="Report format")
def run(
    model: str,
    judge_model: str,
    family: tuple[str, ...],
    authority: tuple[str, ...],
    concurrency: int,
    temperature: float,
    max_tokens: int,
    output: str,
    fmt: str,
):
    """Run the BlindSpot evaluation suite against a model."""
    defeat_families = [DefeatFamily(f) for f in family] if family else None
    authority_types = [AuthorityType(a) for a in authority] if authority else None

    click.echo(f"BlindSpot evaluation starting...")
    click.echo(f"  Model under test: {model}")
    click.echo(f"  Judge model: {judge_model}")

    dataset = generate_dataset(defeat_families, authority_types)
    click.echo(f"  Test cases: {len(dataset)}")
    click.echo()

    def progress(completed: int, total: int):
        click.echo(f"\r  Progress: {completed}/{total} ({completed/total:.0%})", nl=False)

    results = asyncio.run(
        run_eval(
            model=model,
            judge_model=judge_model,
            defeat_families=defeat_families,
            authority_types=authority_types,
            concurrency=concurrency,
            temperature=temperature,
            max_tokens=max_tokens,
            progress_callback=progress,
        )
    )
    click.echo()

    summary = summarize(results)
    click.echo()
    click.echo(f"Results for {summary.model_name}:")
    click.echo(f"  Helps:           {summary.helps_count}/{summary.total_cases} ({summary.helps_count/summary.total_cases:.1%})")
    click.echo(f"  Hard refusals:   {summary.hard_refusal_count}/{summary.total_cases} ({summary.hard_refusal_count/summary.total_cases:.1%})")
    click.echo(f"  Deflections:     {summary.deflection_count}/{summary.total_cases} ({summary.deflection_count/summary.total_cases:.1%})")
    click.echo(f"  Over-refusal:    {summary.over_refusal_rate:.1%}")
    click.echo(f"  Defeat engaged:  {summary.defeat_engagement_rate:.1%}")

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if fmt in ("json", "both"):
        json_path = output_dir / "report.json"
        generate_json_report(results, json_path)
        click.echo(f"\n  JSON report: {json_path}")

    if fmt in ("markdown", "both"):
        md_path = output_dir / "report.md"
        generate_markdown_report(results, md_path)
        click.echo(f"  Markdown report: {md_path}")


@cli.command()
@click.option("--family", multiple=True, type=click.Choice([f.value for f in DefeatFamily]), help="Filter by defeat family")
@click.option("--authority", multiple=True, type=click.Choice([a.value for a in AuthorityType]), help="Filter by authority type")
@click.option("--output", "-o", type=click.Path(), help="Output file (JSON). Omit to print to stdout.")
def generate(family: tuple[str, ...], authority: tuple[str, ...], output: Optional[str]):
    """Generate the test case dataset (without running evaluation)."""
    defeat_families = [DefeatFamily(f) for f in family] if family else None
    authority_types = [AuthorityType(a) for a in authority] if authority else None

    dataset = generate_dataset(defeat_families, authority_types)
    data = [tc.model_dump() for tc in dataset]

    if output:
        Path(output).write_text(json.dumps(data, indent=2))
        click.echo(f"Generated {len(dataset)} test cases -> {output}")
    else:
        click.echo(json.dumps(data, indent=2))


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "markdown", "both"]), default="both", help="Report format")
@click.option("--output", "-o", default="blindspot_results", help="Output directory")
def report(input_file: str, fmt: str, output: str):
    """Generate reports from a previous evaluation's JSON output."""
    from .types import EvalResult

    raw = json.loads(Path(input_file).read_text())

    if isinstance(raw, dict) and "results" in raw:
        click.echo("Re-generating reports from existing evaluation data is not yet supported for nested formats.")
        click.echo("Use 'blindspot run' to generate fresh reports.")
        sys.exit(1)

    results = [EvalResult.model_validate(r) for r in raw]
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if fmt in ("json", "both"):
        json_path = output_dir / "report.json"
        generate_json_report(results, json_path)
        click.echo(f"JSON report: {json_path}")

    if fmt in ("markdown", "both"):
        md_path = output_dir / "report.md"
        generate_markdown_report(results, md_path)
        click.echo(f"Markdown report: {md_path}")


if __name__ == "__main__":
    cli()
