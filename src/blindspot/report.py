"""Generates markdown + JSON summary reports from evaluation results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .runner import summarize
from .types import EvalResult, EvalSummary


def generate_json_report(
    results: list[EvalResult],
    output_path: Optional[Path] = None,
) -> dict:
    """Generate a JSON report from evaluation results.

    Args:
        results: List of EvalResult objects.
        output_path: If provided, write JSON to this file.

    Returns:
        The report as a dictionary.
    """
    summary = summarize(results)

    report = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "blindspot",
            "version": "0.1.0",
        },
        "summary": summary.model_dump(),
        "results": [
            {
                "test_case_id": r.test_case.id,
                "defeat_family": r.test_case.defeat_family.value,
                "authority_type": r.test_case.authority_type.value,
                "classification": r.judgment.classification.value,
                "engages_with_defeat": r.judgment.engages_with_defeat,
                "confidence": r.judgment.confidence,
                "reasoning": r.judgment.reasoning,
                "model_response": r.response.raw_response,
                "latency_ms": r.response.latency_ms,
            }
            for r in results
        ],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2))

    return report


def generate_markdown_report(
    results: list[EvalResult],
    output_path: Optional[Path] = None,
) -> str:
    """Generate a markdown report from evaluation results.

    Args:
        results: List of EvalResult objects.
        output_path: If provided, write markdown to this file.

    Returns:
        The markdown report as a string.
    """
    summary = summarize(results)
    md = _build_markdown(summary, results)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md)

    return md


def _build_markdown(summary: EvalSummary, results: list[EvalResult]) -> str:
    """Build the full markdown report string."""
    lines = [
        f"# BlindSpot Evaluation Report",
        "",
        f"**Model:** {summary.model_name}  ",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Total test cases:** {summary.total_cases}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Helps | {summary.helps_count} ({_pct(summary.helps_count, summary.total_cases)}) |",
        f"| Hard Refusals | {summary.hard_refusal_count} ({_pct(summary.hard_refusal_count, summary.total_cases)}) |",
        f"| Deflections | {summary.deflection_count} ({_pct(summary.deflection_count, summary.total_cases)}) |",
        f"| Over-Refusal Rate | {summary.over_refusal_rate:.1%} |",
        f"| Defeat Engagement Rate | {summary.defeat_engagement_rate:.1%} |",
        "",
        "---",
        "",
        "## Breakdown by Defeat Family",
        "",
        "| Family | Helps | Hard Refusal | Deflection | Over-Refusal Rate |",
        "|--------|-------|-------------|------------|-------------------|",
    ]

    for family, counts in sorted(summary.by_defeat_family.items()):
        total = counts.get("total", 1)
        orr = (counts.get("hard_refusal", 0) + counts.get("deflection", 0)) / total
        lines.append(
            f"| {family} | {counts.get('helps', 0)} | "
            f"{counts.get('hard_refusal', 0)} | {counts.get('deflection', 0)} | {orr:.1%} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Breakdown by Authority Type",
        "",
        "| Authority | Helps | Hard Refusal | Deflection | Over-Refusal Rate |",
        "|-----------|-------|-------------|------------|-------------------|",
    ])

    for auth, counts in sorted(summary.by_authority_type.items()):
        total = counts.get("total", 1)
        orr = (counts.get("hard_refusal", 0) + counts.get("deflection", 0)) / total
        lines.append(
            f"| {auth} | {counts.get('helps', 0)} | "
            f"{counts.get('hard_refusal', 0)} | {counts.get('deflection', 0)} | {orr:.1%} |"
        )

    # Individual hard refusals section
    hard_refusals = [r for r in results if r.judgment.classification.value == "hard_refusal"]
    if hard_refusals:
        lines.extend([
            "",
            "---",
            "",
            "## Hard Refusal Details",
            "",
        ])
        for r in hard_refusals:
            lines.extend([
                f"### {r.test_case.id}",
                "",
                f"**Defeat family:** {r.test_case.defeat_family.value}  ",
                f"**Authority:** {r.test_case.authority_type.value}  ",
                f"**Confidence:** {r.judgment.confidence:.2f}",
                "",
                f"> **Rule:** {r.test_case.rule}",
                "",
                f"> **Defeat condition:** {r.test_case.defeat_condition}",
                "",
                f"**Judge reasoning:** {r.judgment.reasoning}",
                "",
                "---",
                "",
            ])

    lines.extend([
        "",
        "*Generated by [BlindSpot](https://github.com/your-org/blindspot)*",
    ])

    return "\n".join(lines)


def _pct(part: int, total: int) -> str:
    """Format a count as a percentage string."""
    if total == 0:
        return "0.0%"
    return f"{part / total:.1%}"
