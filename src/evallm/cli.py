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
    with_config(config_path, lambda loaded: click.echo("Config is valid"))


@cli.command()
@click.argument("config_path")
def run(config_path: str) -> None:
    """Run evaluation suites and print results."""

    def do_run(loaded: LoadedConfig) -> None:
        provider = create_provider(loaded.config.system_under_test)
        runner = Runner(loaded.config, provider, loaded.base_dir)
        results = runner.run()
        for result in results:
            click.echo(
                f"ID: {result.id} | Expected: {result.expected} | Actual: {result.actual}"
            )

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
    click.echo(f"Created project: {project_name}")
