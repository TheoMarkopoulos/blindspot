"""Tests for the BlindSpot dataset generator."""

from blindspot.dataset import generate_dataset, generate_test_case
from blindspot.types import AuthorityType, DefeatFamily, TestCase


class TestGenerateTestCase:
    def test_returns_test_case(self):
        tc = generate_test_case(DefeatFamily.MORAL_OVERRIDE, AuthorityType.HOA)
        assert isinstance(tc, TestCase)

    def test_id_format(self):
        tc = generate_test_case(DefeatFamily.LEGAL_INVALIDITY, AuthorityType.EMPLOYER)
        assert tc.id == "legal_invalidity__employer"

    def test_defeat_family_matches(self):
        tc = generate_test_case(DefeatFamily.ABSURDITY, AuthorityType.GYM)
        assert tc.defeat_family == DefeatFamily.ABSURDITY

    def test_authority_type_matches(self):
        tc = generate_test_case(DefeatFamily.UNENFORCEABILITY, AuthorityType.DMV)
        assert tc.authority_type == AuthorityType.DMV

    def test_prompt_contains_scenario(self):
        tc = generate_test_case(DefeatFamily.MORAL_OVERRIDE, AuthorityType.LIBRARY)
        assert "library" in tc.user_prompt.lower()

    def test_prompt_contains_defeat_suffix(self):
        tc = generate_test_case(DefeatFamily.LEGAL_INVALIDITY, AuthorityType.LANDLORD)
        assert "legally disregard" in tc.user_prompt.lower()

    def test_scenario_includes_rule(self):
        tc = generate_test_case(DefeatFamily.AUTHORITY_EXCEEDED, AuthorityType.TSA)
        assert tc.rule in tc.scenario


class TestGenerateDataset:
    def test_full_dataset_has_95_cases(self):
        dataset = generate_dataset()
        assert len(dataset) == 95

    def test_all_defeat_families_present(self):
        dataset = generate_dataset()
        families = {tc.defeat_family for tc in dataset}
        assert families == set(DefeatFamily)

    def test_all_authority_types_present(self):
        dataset = generate_dataset()
        authorities = {tc.authority_type for tc in dataset}
        assert authorities == set(AuthorityType)

    def test_filter_by_defeat_family(self):
        dataset = generate_dataset(defeat_families=[DefeatFamily.ABSURDITY])
        assert len(dataset) == 19
        assert all(tc.defeat_family == DefeatFamily.ABSURDITY for tc in dataset)

    def test_filter_by_authority_type(self):
        dataset = generate_dataset(authority_types=[AuthorityType.HOA])
        assert len(dataset) == 5
        assert all(tc.authority_type == AuthorityType.HOA for tc in dataset)

    def test_filter_both(self):
        dataset = generate_dataset(
            defeat_families=[DefeatFamily.MORAL_OVERRIDE, DefeatFamily.ABSURDITY],
            authority_types=[AuthorityType.HOA, AuthorityType.GYM],
        )
        assert len(dataset) == 4

    def test_unique_ids(self):
        dataset = generate_dataset()
        ids = [tc.id for tc in dataset]
        assert len(ids) == len(set(ids))

    def test_no_empty_prompts(self):
        dataset = generate_dataset()
        for tc in dataset:
            assert len(tc.user_prompt) > 50

    def test_no_empty_scenarios(self):
        dataset = generate_dataset()
        for tc in dataset:
            assert len(tc.scenario) > 20
            assert len(tc.rule) > 10
            assert len(tc.defeat_condition) > 10
