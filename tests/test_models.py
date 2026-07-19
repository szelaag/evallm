import json
from evallm.models import load_test_cases
from evallm.models import SuiteResult, CaseResult, EvalResult
from evallm.config import Suite
import pytest


@pytest.fixture
def loader_suite(tmp_path) -> tuple[Suite, list[dict]]:
    test_data_raw = [
        {"input": "This product is amazing!", "expected": "positive"},
        {"input": "Terrible experience, would not recommend", "expected": "negative"},
        {"input": "It works as described", "expected": "neutral"},
    ]

    test_data = [json.dumps(d) for d in test_data_raw]

    test_file = tmp_path / "test.jsonl"
    test_file.write_text("\n".join(test_data))
    test_suite = Suite(name="test", file="test.jsonl", evaluator="exact_match")
  
    return test_suite, test_data_raw


def test_ids_start_from_one(loader_suite, tmp_path):
    test_suite, _ = loader_suite

    cases = load_test_cases(test_suite, tmp_path)
    assert cases[0].id == "test#1"


def test_loads_all_cases(loader_suite, tmp_path):
    test_suite, test_data_raw = loader_suite
    cases = load_test_cases(test_suite, tmp_path)
    assert len(cases) == len(test_data_raw)


def test_fields_match_source(loader_suite, tmp_path):
    test_suite, test_data_raw = loader_suite
    cases = load_test_cases(test_suite, tmp_path)
    assert cases[0].input == test_data_raw[0]["input"]
    assert cases[0].expected == test_data_raw[0]["expected"]


def test_suite_result_with_working_cases():
    test_cases = [
        CaseResult(
            id="test#1",
            expected="true",
            actual="true",
            eval_result=EvalResult(passed=True, score=1.0),
        ),
        CaseResult(
            id="test#2",
            expected="true",
            actual="false",
            eval_result=EvalResult(passed=False, score=0.0),
        ),
        CaseResult(
            id="test#3",
            expected="good",
            actual="bad",
            eval_result=EvalResult(passed=False, score=0.0),
        ),
        CaseResult(
            id="test#4",
            expected="good",
            actual="good",
            eval_result=EvalResult(passed=True, score=1.0),
        ),
    ]
    suite_result = SuiteResult(name="test", cases=test_cases)
    assert suite_result.total == 4
    assert suite_result.passed_count == 2
    assert suite_result.pass_rate == 0.5


def test_suite_result_with_zero_cases():
    test_cases = []
    suite_result = SuiteResult(name="test", cases=test_cases)
    assert suite_result.total == 0
    assert suite_result.passed_count == 0
    assert suite_result.pass_rate == 0.0
