import json
from evallm.models import load_test_cases
from evallm.config import Suite


def test_ids_start_from_one(tmp_path):
    test_data_raw = [
        {"input": "This product is amazing!", "expected": "positive"},
        {"input": "Terrible experience, would not recommend", "expected": "negative"},
        {"input": "It works as described", "expected": "neutral"},
    ]

    test_data: list[str] = []

    for test in test_data_raw:
        test_data.append(json.dumps(test))

    test_file = tmp_path / "test.jsonl"
    test_file.write_text("\n".join(test_data))
    test_suite = Suite(
        name="test", file="test.jsonl", evaluator="exact_match"
    )

    cases = load_test_cases(test_suite, tmp_path)
    assert cases[0].id == "test#1"


def test_loads_all_cases(tmp_path):
    test_data_raw = [
        {"input": "This product is amazing!", "expected": "positive"},
        {"input": "Terrible experience, would not recommend", "expected": "negative"},
        {"input": "It works as described", "expected": "neutral"},
    ]

    test_data = [json.dumps(d) for d in test_data_raw]

    test_file = tmp_path / "test.jsonl"
    test_file.write_text("\n".join(test_data))
    test_suite = Suite(
        name="test", file="test.jsonl", evaluator="exact_match"
    )

    cases = load_test_cases(test_suite, tmp_path)
    assert len(cases) == len(test_data_raw)


def test_fields_match_source(tmp_path):
    test_data_raw = [
        {"input": "This product is amazing!", "expected": "positive"},
        {"input": "Terrible experience, would not recommend", "expected": "negative"},
        {"input": "It works as described", "expected": "neutral"},
    ]

    test_data = [json.dumps(d) for d in test_data_raw]

    test_file = tmp_path / "test.jsonl"
    test_file.write_text("\n".join(test_data))
    test_suite = Suite(
        name="test", file="test.jsonl", evaluator="exact_match"
    )

    cases = load_test_cases(test_suite, tmp_path)
    assert cases[0].input == test_data_raw[0]["input"]
    assert cases[0].expected == test_data_raw[0]["expected"]
