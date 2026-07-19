from evallm.providers import Provider
import json
from evallm.models import Suite
from evallm.config import Config, SystemUnderTest
from evallm.runner import Runner


class MockProvider(Provider):
    def __init__(self, responses: dict[str, str]):
        self.responses = responses

    def generate(self, input: str) -> str:
        return self.responses[input]


def test_runner_orchestration(tmp_path):
    test_data_raw = [
        {"input": "good", "expected": "positive"},
        {"input": "good", "expected": "positive"},
        {"input": "bad", "expected": "negative"},
        {"input": "bad", "expected": "positive"},
    ]
    mock_provider = MockProvider({"good": "positive", "bad": "negative"})

    test_data = [json.dumps(d) for d in test_data_raw]

    test_file = tmp_path / "test.jsonl"
    test_file.write_text("\n".join(test_data))
    test_suite = Suite(name="test", file="test.jsonl", evaluator="exact_match")

    config = Config(
        name="runner_test",
        system_under_test=SystemUnderTest(
            provider="anthropic", model="", system_prompt=""
        ),
        suites=[test_suite],
    )

    runner = Runner(config, mock_provider, tmp_path)
    result = runner.run()

    assert len(result.suites) == 1
    assert result.suites[0].total == 4
    assert result.suites[0].passed_count == 3
    assert result.suites[0].cases[0].actual == "positive"
    assert result.suites[0].cases[2].actual == "negative"

    assert result.total == 4
    assert result.passed_count == 3
