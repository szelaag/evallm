"""Command-line interface for evallm."""

import click
import yaml
from pathlib import Path
from pydantic import ValidationError
from evallm.config import load_config, LoadedConfig
from evallm.providers import create_provider
from evallm.runner import Runner
from collections.abc import Callable
from textwrap import dedent
from evallm.reporting import show_run_results, show_message
from evallm.storage import create_storage
from evallm.reports.html import generate_report
from datetime import datetime


def with_config(config_path: str, action: Callable[[LoadedConfig], None]) -> None:
    try:
        loaded = load_config(Path(config_path))
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {config_path}")
    except ValidationError as e:
        raise click.ClickException(f"Invalid config:\n{e}")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML syntax:\n{e}")
    else:
        action(loaded)


@click.group()
def cli() -> None:
    """evallm - LLM evaluation framework."""
    pass


@cli.command()
@click.argument("config_path")
def validate(config_path: str) -> None:
    """Validate an evallm config file."""
    with_config(
        config_path,
        lambda loaded: show_message("Config is [bright_green bold]valid[/]"),
    )


@cli.command()
@click.argument("config_path")
@click.option(
    "--db", "-d", default=None, help="Path to the database file (default: alongside config)"
)
@click.option(
    "--cases", "-c", is_flag=True, help="Show detailed results of cases in terminal"
)
@click.option(
    "--report", "-r", is_flag=True, help="Generate HTML report in results/"
)
def run(config_path: str, db: str | None, cases: bool, report: bool) -> None:
    """Run evaluation suites and print results."""

    def do_run(loaded: LoadedConfig) -> None:
        provider = create_provider(loaded.config.system_under_test)
        runner = Runner(loaded.config, provider, loaded.base_dir)
        result = runner.run()

        db_path = Path(db) if db else loaded.base_dir / "evallm.db"
        storage = create_storage(db_path)
        storage.save_run(result)

        if report:
            results_dir = loaded.base_dir / "results"
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_path = results_dir / f"report_{timestamp}.html"
            generate_report(result, report_path)
            show_message(f"Report saved to [bright_green bold]{report_path}[/]")

        show_run_results(result, cases) # cases=True : detailed

    with_config(config_path, do_run)


@cli.command()
@click.argument("project_name")
def init(project_name: str) -> None:
    """Create a new evallm project with example config and suite."""
    path = Path(project_name)
    path.mkdir()
    (path / "suites").mkdir()
    (path / "results").mkdir()
    config_content = dedent("""\
        name: my-eval-project

        system_under_test:
          provider: anthropic
          model: claude-sonnet-4-6
          system_prompt: |
            Classify the sentiment of the review as one of: positive, negative, neutral.
            Return only the label, nothing else.
          temperature: 0.0
          max_tokens: 100

        suites:
          - name: example
            file: suites/example.jsonl
            evaluator: exact_match
    """)
    suite_content = dedent("""\
        {"input": "This product is amazing!", "expected": "positive"}
        {"input": "Terrible experience, would not recommend", "expected": "negative"}
        {"input": "It works as described", "expected": "neutral"}
    """)
    (path / "evallm.yaml").write_text(config_content)
    (path / "suites" / "example.jsonl").write_text(suite_content)
    show_message(f"Created project [bright_green bold]{project_name}[/]")
