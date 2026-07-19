from evallm.config import Config, load_config
import pytest
from pydantic import ValidationError
from pathlib import Path
import yaml


def test_valid_config_builds():
    config = Config(
        name="test-eval",
        system_under_test={
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "system_prompt": "Classify sentiment.",
        },
        suites=[
            {"name": "s1", "file": "suites/s.jsonl", "evaluator": "exact_match"},
        ],
    )
    assert config.name == "test-eval"


def test_temperature_out_of_range_raises():
    with pytest.raises(ValidationError):
        Config(
            name="test-eval",
            system_under_test={
                "provider": "anthropic",
                "model": "claude-sonnet-4-6",
                "system_prompt": "x",
                "temperature": 5.0,
            },
            suites=[
                {"name": "s1", "file": "suites/s.jsonl", "evaluator": "exact_match"},
            ],
        )


def test_empty_suites_raises():
    with pytest.raises(ValidationError):
        Config(
            name="test-eval",
            system_under_test={
                "provider": "anthropic",
                "model": "claude-sonnet-4-6",
                "system_prompt": "x",
            },
            suites=[],
        )


def test_invalid_evaluator_raises():
    with pytest.raises(ValidationError):
        Config(
            name="test-eval",
            system_under_test={
                "provider": "anthropic",
                "model": "claude-sonnet-4-6",
                "system_prompt": "x",
            },
            suites=[
                {"name": "s1", "file": "suites/s.jsonl", "evaluator": "exact_matcher"},
            ],
        )


def test_load_config_returns_config(tmp_path):
    config_data = {
        "name": "test-eval",
        "system_under_test": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "system_prompt": "Classify sentiment.",
        },
        "suites": [
            {"name": "s1", "file": "suites/s.jsonl", "evaluator": "exact_match"},
        ],
    }
    config_file = tmp_path / "test.yaml"
    config_file.write_text(yaml.dump(config_data))
    loaded = load_config(config_file)
    assert loaded.config.name == "test-eval"


def test_load_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config(Path("does_not_exist.yaml"))
