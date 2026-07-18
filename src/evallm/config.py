from typing import Literal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Suite(BaseModel):
    name: str
    file: str
    evaluator: Literal["exact_match"]


class SystemUnderTest(BaseModel):
    provider: Literal["anthropic"]
    model: str
    system_prompt: str
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, gt=0)


class Config(BaseModel):
    name: str
    description: str | None = None
    system_under_test: SystemUnderTest
    suites: list[Suite] = Field(min_length=1)


def load_config(path: Path) -> Config:
    """Load and validate an evallm config file.

    Args:
        path: Path to the YAML config file.

    Returns:
        A validated Config object.
    """
    raw_text = path.read_text()
    data = yaml.safe_load(raw_text)
    return Config(**data)
