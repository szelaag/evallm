from pydantic import BaseModel, Field
from evallm.config import Suite
import json
from pathlib import Path


class TestCase(BaseModel):
    id: str
    input: str
    expected: str


class EvalResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)


class CaseResult(BaseModel):
    id: str
    expected: str
    actual: str
    eval_result: EvalResult


class SuiteResult(BaseModel):
    name: str
    cases: list[CaseResult]

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed_count(self) -> int:
        passed = 0
        for case in self.cases:
            passed += 1 if case.eval_result.passed else 0
        return passed

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed_count / self.total


def load_test_cases(suite: Suite, base_dir: Path) -> list[TestCase]:
    """
    Read path from Suite and return list of TestCase's with added ID

    Args:
        suite: suite from config, name and path to testfile
        base_dir: Directory the config was loaded from; suite file paths resolve against it.

    Returns:
        list of TestCase's with added ID to each test from file

    ID is based on filename and line number of the test
    """
    parsed_tests: list[TestCase] = []

    with open(base_dir / suite.file) as file:
        for i, line in enumerate(file, start=1):
            test = json.loads(line)

            parsed_tests.append(
                TestCase(
                    id=f"{suite.name}#{i}",
                    input=test["input"],
                    expected=test["expected"],
                )
            )
    return parsed_tests
