from jinja2 import Environment, FileSystemLoader
from evallm.models import RunResult
from evallm.metrics import build_confusion_matrix
from pathlib import Path


def generate_report(run: RunResult, output_path: Path) -> None:
    templates_dir = Path(__file__).parent / "templates"

    env = Environment(loader=FileSystemLoader(templates_dir))

    template = env.get_template("report.html.j2")

    matrices = {suite.name: build_confusion_matrix(suite) for suite in run.suites}

    html = template.render(run=run, matrices=matrices)
    output_path.write_text(html)


if __name__ == "__main__":
    from datetime import datetime
    from uuid import uuid4
    from evallm.models import RunResult, SuiteResult, CaseResult, EvalResult

    def _case(cid: str, expected: str, actual: str, passed: bool) -> CaseResult:
        return CaseResult(
            id=cid,
            expected=expected,
            actual=actual,
            eval_result=EvalResult(passed=passed, score=float(passed)),
        )

    fake_run = RunResult(
        id=uuid4(),
        timestamp=datetime.now(),
        suites=[
            SuiteResult(
                name="sentiment",
                cases=[
                    _case("sentiment#1", "positive", "positive", True),
                    _case("sentiment#2", "negative", "positive", False),
                    _case("sentiment#3", "neutral", "neutral", True),
                    _case("sentiment#4", "positive", "positive", True),
                    _case("sentiment#5", "negative", "negative", True),
                ],
            ),
            SuiteResult(
                name="topic_classification",
                cases=[
                    _case("topic#1", "sport", "sport", True),
                    _case("topic#2", "politics", "sport", False),
                    _case("topic#3", "tech", "tech", True),
                    _case("topic#4", "business", "politics", False),
                ],
            ),
            SuiteResult(
                name="intent_detection",
                cases=[
                    _case("intent#1", "question", "question", True),
                    _case("intent#2", "command", "command", True),
                    _case("intent#3", "statement", "statement", True),
                ],
            ),
        ],
    )

    generate_report(fake_run, Path("/tmp/test_report.html"))
    print("Report saved to /tmp/test_report.html")
