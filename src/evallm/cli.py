"""Command-line interface for evallm."""

import click
import yaml
from pathlib import Path
from pydantic import ValidationError
from evallm.config import load_config


@click.group()
def cli() -> None:
    """evallm - LLM evaluation framework."""
    pass


@cli.command()
@click.argument("config_path")
def validate(config_path: str) -> None:
    """Validate an evallm config file."""
    try:
        load_config(Path(config_path))
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {config_path}")
    except ValidationError as e:
        raise click.ClickException(f"Invalid config:\n{e}")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML syntax:\n{e}")
    else:
        click.echo("Config is valid")
