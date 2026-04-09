"""Quick start example for BlindSpot."""

import asyncio

from blindspot.dataset import generate_dataset, generate_test_case
from blindspot.runner import run_eval, run_single, summarize
from blindspot.report import generate_json_report, generate_markdown_report
from blindspot.types import AuthorityType, DefeatFamily


async def main():
    # --- 1. Generate and inspect test cases ---
    print("=== Generating dataset ===")
    full_dataset = generate_dataset()
    print(f"Full dataset: {len(full_dataset)} test cases")

    # Generate a single case
    case = generate_test_case(DefeatFamily.MORAL_OVERRIDE, AuthorityType.HOA)
    print(f"\nExample case: {case.id}")
    print(f"  Rule: {case.rule}")
    print(f"  Defeat: {case.defeat_condition}")
    print(f"  Prompt preview: {case.user_prompt[:100]}...")

    # --- 2. Run a small evaluation ---
    print("\n=== Running evaluation (2 families, 2 authorities) ===")
    results = await run_eval(
        model="openai/gpt-4o-mini",          # Model under test
        judge_model="openai/gpt-4o-mini",    # Judge model
        defeat_families=[DefeatFamily.MORAL_OVERRIDE, DefeatFamily.ABSURDITY],
        authority_types=[AuthorityType.HOA, AuthorityType.EMPLOYER],
        concurrency=3,
    )

    # --- 3. Summarize results ---
    summary = summarize(results)
    print(f"\nResults for {summary.model_name}:")
    print(f"  Total: {summary.total_cases}")
    print(f"  Helps: {summary.helps_count}")
    print(f"  Hard refusals: {summary.hard_refusal_count}")
    print(f"  Deflections: {summary.deflection_count}")
    print(f"  Over-refusal rate: {summary.over_refusal_rate:.1%}")
    print(f"  Defeat engagement: {summary.defeat_engagement_rate:.1%}")

    # --- 4. Generate reports ---
    from pathlib import Path

    generate_json_report(results, Path("example_results/report.json"))
    generate_markdown_report(results, Path("example_results/report.md"))
    print("\nReports saved to example_results/")


if __name__ == "__main__":
    asyncio.run(main())
