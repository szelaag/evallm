import pytest
from evallm.evaluators import ExactMatchEvaluator


@pytest.mark.parametrize(
    "expected, actual, should_pass, expected_score",
    [
        ("positive", "positive", True, 1.0),
        ("positive", "Positive", True, 1.0),
        ("positive", " positive ", True, 1.0),
        ("positive", "negative", False, 0.0),
        ("positive", "positive.", False, 0.0),
    ],
)
def test_exact_match(expected, actual, should_pass, expected_score):
    evaluator = ExactMatchEvaluator()
    result = evaluator.evaluate(expected, actual)
    assert result.passed == should_pass
    assert result.score == expected_score
