# Contributing to BlindSpot

Thank you for your interest in contributing to BlindSpot! This project aims to improve LLM safety calibration by identifying over-refusal patterns.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/blindspot.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b my-feature`

## Development

```bash
# Run tests
pytest -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/
```

## Adding New Scenarios

The test case matrix lives in `src/blindspot/dataset.py`. To add scenarios:

1. Add entries to `_SCENARIO_SEEDS` for your (defeat_family, authority_type) combination
2. Each entry is a tuple of (rule, defeat_condition, action)
3. Run `pytest tests/test_dataset.py` to verify

## Adding New Authority Types or Defeat Families

1. Add the new enum value to `src/blindspot/types.py`
2. Add the label to `_AUTHORITY_LABELS` in `dataset.py`
3. Add scenario seeds for all combinations in `_SCENARIO_SEEDS`
4. Add template if new defeat family in `_DEFEAT_TEMPLATES`
5. Update tests

## Pull Requests

- Keep PRs focused on a single change
- Include tests for new functionality
- Ensure `ruff check` passes
- Update documentation if adding new features

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
