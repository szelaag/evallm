from abc import ABC, abstractmethod
from evallm.models import EvalResult
from evallm.config import Suite


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, expected: str, actual: str) -> EvalResult: ...


class ExactMatchEvaluator(Evaluator):
    def evaluate(self, expected: str, actual: str) -> EvalResult:
        """Compare expected and actual after normalizing case and whitespace"""
        passed = expected.lower().strip() == actual.lower().strip()
        return EvalResult(
            passed=passed,
            score=float(passed),
        )


def create_evaluator(suite: Suite) -> Evaluator:
    """Build an evaluator instance from a suite's evaluator type.

    Args:
        suite: Suite whose evaluator field selects the evaluator.

    Returns:
        An Evaluator implementation matching suite.evaluator.

    Raises:
        ValueError: If suite.evaluator is not a supported evaluator.
    """
    if suite.evaluator == "exact_match":
        return ExactMatchEvaluator()
    else:
        raise ValueError(f"{suite.evaluator} is an unsuported evaluation type")
