from pydantic import BaseModel
from evallm.config import Suite
import json
from pathlib import Path


class TestCase(BaseModel):
    id: str
    input: str
    expected: str


class CaseResult(BaseModel):
    id: str
    expected: str
    actual: str


def load_test_cases(suite: Suite) -> list[TestCase]:
    """
    Read path from Suite and return list of TestCase's with added ID

    Args:
        suite: suite from config, name and path to testfile

    Returns:
        list of TestCase's with added ID to each test from file

    ID is based on filename and line number of the test
    """
    parsed_tests: list[TestCase] = []

    with open(Path(suite.file), "r") as file:
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
