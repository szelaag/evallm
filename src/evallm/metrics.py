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


if __name__ == "__main__":
    from evallm.models import SuiteResult, CaseResult, EvalResult

    def case(exp, act):
        passed = exp == act
        return CaseResult(
            id="x",
            expected=exp,
            actual=act,
            eval_result=EvalResult(passed=passed, score=float(passed)),
        )

    suite = SuiteResult(
        name="sentiment",
        cases=[
            case("positive", "positive"),  # 1
            case("positive", "negative"),  # 2
            case("negative", "negative"),  # 3
            case("neutral", "positive"),  # 4
            case("positive", "positive"),  # 5
            case("negative", "negative"),  # 6
            case("neutral", "neutral"),  # 7
            case("positive", "neutral"),  # 8
            case("negative", "positive"),  # 9
            case("neutral", "positive"),  # 10
        ],
    )

    matrix = build_confusion_matrix(suite)

    print("classes:", matrix.classes)
    print("total:", matrix.total)
    print("correct:", matrix.correct)
    print("accuracy:", matrix.accuracy)
    print()

    classes = matrix.classes
    print("           " + "  ".join(f"{c:>9}" for c in classes))
    for exp in classes:
        row = "  ".join(f"{matrix.matrix[exp][act]:>9}" for act in classes)
        print(f"{exp:>9}  {row}")
