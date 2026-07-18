from evallm.config import Config
from evallm.providers import Provider
from evallm.models import load_test_cases, CaseResult

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

    def run(self) -> list[CaseResult]:
        """Run all suites through the provider and collect results.

        Returns:
            A list of CaseResult, one per test case across all suites.
        """
        test_results: list[CaseResult] = []
        for suite in self.config.suites:
            cases = load_test_cases(suite, self.base_dir)
            for case in cases:
                actual = self.provider.generate(case.input)
                test_results.append(
                    CaseResult(id=case.id, expected=case.expected, actual=actual)
                )
        return test_results
