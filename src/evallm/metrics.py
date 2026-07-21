from evallm.models import SuiteResult
from dataclasses import dataclass


@dataclass
class ConfusionMatrix:
    matrix: dict[str, dict[str, int]]
    classes: list[str]

    @property
    def total(self) -> int:
        return sum(count for row in self.matrix.values() for count in row.values())

    @property
    def correct(self) -> int:
        return sum(self.matrix[c][c] for c in self.classes)

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return self.correct / self.total


def build_confusion_matrix(suite: SuiteResult) -> ConfusionMatrix:
    class_set: set[str] = set()

    for case in suite.cases:
        class_set.add(case.actual)
        class_set.add(case.expected)

    classes = sorted(class_set)

    matrix = {exp: {act: 0 for act in classes} for exp in classes}

    for case in suite.cases:
        matrix[case.expected][case.actual] += 1

    return ConfusionMatrix(matrix=matrix, classes=classes)
