from evallm.config import Config
from evallm.providers import Provider
from evallm.models import load_test_cases, CaseResult, SuiteResult, RunResult
from evallm.evaluators import create_evaluator

from uuid import uuid4
from datetime import datetime
from pathlib import Path


class Runner:
    """Orchestrate test execution: load cases and run them through a provider."""

    def __init__(
        self,
        config: Config,
        provider: Provider,
        base_dir: Path,
    ):
        self.config = config
        self.provider = provider
        self.base_dir = base_dir

    def run(self) -> RunResult:
        """Run all suites through the provider and collect results.

        Returns:
            RunResult, each with its case results and metrics.
        """
        timestamp = datetime.now()

        suite_results: list[SuiteResult] = []
        for suite in self.config.suites:
            suite_cases: list[CaseResult] = []
            cases = load_test_cases(suite, self.base_dir)
            evaluator = create_evaluator(suite)
            for case in cases:
                expected = case.expected
                actual = self.provider.generate(case.input)
                eval_result = evaluator.evaluate(expected, actual)
                suite_cases.append(
                    CaseResult(
                        id=case.id,
                        expected=expected,
                        actual=actual,
                        eval_result=eval_result,
                    )
                )
            suite_results.append(SuiteResult(name=suite.name, cases=suite_cases))

        return RunResult(id=uuid4(), timestamp=timestamp, suites=suite_results)
