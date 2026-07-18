"""Command-line interface for evallm."""

import click
import yaml
from pathlib import Path
from pydantic import ValidationError
from evallm.config import load_config, Config
from evallm.providers import create_provider
from evallm.runner import Runner
from collections.abc import Callable


def with_config(config_path: str, action: Callable[[Config], None]) -> None:
    try:
        config = load_config(Path(config_path))
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {config_path}")
    except ValidationError as e:
        raise click.ClickException(f"Invalid config:\n{e}")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML syntax:\n{e}")
    else:
        action(config)


@click.group()
def cli() -> None:
    """evallm - LLM evaluation framework."""
    pass


@cli.command()
@click.argument("config_path")
def validate(config_path: str) -> None:
    """Validate an evallm config file."""
    with_config(config_path, lambda config: click.echo("Config is valid"))


@cli.command()
@click.argument("config_path")
def run(config_path: str) -> None:
    """Run evaluation suites and print results."""

    def do_run(config: Config) -> None:
        provider = create_provider(config.system_under_test)
        runner = Runner(config, provider)
        results = runner.run()
        for result in results:
            click.echo(
                f"ID: {result.id} | Expected: {result.expected} | Actual: {result.actual}"
            )

    with_config(config_path, do_run)
