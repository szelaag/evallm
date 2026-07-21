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
