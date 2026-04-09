"""Runs eval against any OpenAI-compatible endpoint via litellm."""

from __future__ import annotations

import asyncio
import time
from typing import Optional

from litellm import acompletion

from .dataset import generate_dataset
from .judge import judge_response
from .types import (
    AuthorityType,
    DefeatFamily,
    EvalResult,
    EvalSummary,
    ModelResponse,
    TestCase,
)


async def query_model(
    test_case: TestCase,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> ModelResponse:
    """Send a test case prompt to the model under test and capture the response.

    Args:
        test_case: The test case containing the prompt.
        model: Any litellm-compatible model string.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.

    Returns:
        ModelResponse with raw text and timing info.
    """
    start = time.perf_counter()
    response = await acompletion(
        model=model,
        messages=[{"role": "user", "content": test_case.user_prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    raw_text = response.choices[0].message.content or ""
    token_count = None
    if hasattr(response, "usage") and response.usage:
        token_count = response.usage.total_tokens

    return ModelResponse(
        test_case_id=test_case.id,
        model_name=model,
        raw_response=raw_text,
        latency_ms=elapsed_ms,
        token_count=token_count,
    )


async def run_single(
    test_case: TestCase,
    model: str,
    judge_model: str = "openai/gpt-4o-mini",
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> EvalResult:
    """Run a single test case: query the model, then judge the response.

    Args:
        test_case: The test case to evaluate.
        model: The model under test.
        judge_model: The model to use as judge.
        temperature: Sampling temperature for the model under test.
        max_tokens: Max tokens for the model under test.

    Returns:
        EvalResult combining the test case, response, and judgment.
    """
    response = await query_model(test_case, model, temperature, max_tokens)
    judgment = await judge_response(test_case, response, judge_model)
    return EvalResult(test_case=test_case, response=response, judgment=judgment)


async def run_eval(
    model: str,
    judge_model: str = "openai/gpt-4o-mini",
    defeat_families: Optional[list[DefeatFamily]] = None,
    authority_types: Optional[list[AuthorityType]] = None,
    concurrency: int = 5,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    progress_callback: Optional[callable] = None,
) -> list[EvalResult]:
    """Run the full evaluation pipeline with controlled concurrency.

    Args:
        model: The model under test (any litellm-compatible string).
        judge_model: The model to use as judge.
        defeat_families: Filter to specific defeat families. None = all.
        authority_types: Filter to specific authority types. None = all.
        concurrency: Max parallel requests.
        temperature: Sampling temperature for the model under test.
        max_tokens: Max tokens for the model under test.
        progress_callback: Optional callback(completed, total) for progress updates.

    Returns:
        List of EvalResult objects.
    """
    dataset = generate_dataset(defeat_families, authority_types)
    semaphore = asyncio.Semaphore(concurrency)
    results: list[EvalResult] = []
    completed = 0

    async def _run_one(tc: TestCase) -> EvalResult:
        nonlocal completed
        async with semaphore:
            result = await run_single(tc, model, judge_model, temperature, max_tokens)
            completed += 1
            if progress_callback:
                progress_callback(completed, len(dataset))
            return result

    tasks = [_run_one(tc) for tc in dataset]
    results = await asyncio.gather(*tasks)
    return list(results)


def summarize(results: list[EvalResult]) -> EvalSummary:
    """Compute aggregate statistics from evaluation results.

    Args:
        results: List of EvalResult objects from a run.

    Returns:
        EvalSummary with counts, rates, and breakdowns.
    """
    if not results:
        return EvalSummary(
            model_name="unknown",
            total_cases=0,
            helps_count=0,
            hard_refusal_count=0,
            deflection_count=0,
            defeat_engagement_rate=0.0,
            over_refusal_rate=0.0,
        )

    model_name = results[0].response.model_name
    total = len(results)

    helps = sum(1 for r in results if r.judgment.classification.value == "helps")
    hard_refusals = sum(1 for r in results if r.judgment.classification.value == "hard_refusal")
    deflections = sum(1 for r in results if r.judgment.classification.value == "deflection")
    defeat_engaged = sum(1 for r in results if r.judgment.engages_with_defeat)

    # Breakdowns
    by_family: dict[str, dict[str, int]] = {}
    by_authority: dict[str, dict[str, int]] = {}

    for r in results:
        family = r.test_case.defeat_family.value
        auth = r.test_case.authority_type.value
        cls = r.judgment.classification.value

        if family not in by_family:
            by_family[family] = {"helps": 0, "hard_refusal": 0, "deflection": 0, "total": 0}
        by_family[family][cls] += 1
        by_family[family]["total"] += 1

        if auth not in by_authority:
            by_authority[auth] = {"helps": 0, "hard_refusal": 0, "deflection": 0, "total": 0}
        by_authority[auth][cls] += 1
        by_authority[auth]["total"] += 1

    return EvalSummary(
        model_name=model_name,
        total_cases=total,
        helps_count=helps,
        hard_refusal_count=hard_refusals,
        deflection_count=deflections,
        defeat_engagement_rate=defeat_engaged / total if total else 0.0,
        over_refusal_rate=(hard_refusals + deflections) / total if total else 0.0,
        by_defeat_family=by_family,
        by_authority_type=by_authority,
    )
