from evallm.config import Config
from evallm.providers import Provider
from evallm.models import load_test_cases, CaseResult


class Runner:
    """Orchestrate test execution: load cases and run them through a provider."""

    def __init__(
        self,
        config: Config,
        provider: Provider,
    ):
        self.config = config
        self.provider = provider

    def run(self) -> list[CaseResult]:
        """Run all suites through the provider and collect results.

        Returns:
            A list of CaseResult, one per test case across all suites.
        """
        test_results: list[CaseResult] = []
        for suite in self.config.suites:
            cases = load_test_cases(suite)
            for case in cases:
                actual = self.provider.generate(case.input)
                test_results.append(
                    CaseResult(id=case.id, expected=case.expected, actual=actual)
                )
        return test_results
