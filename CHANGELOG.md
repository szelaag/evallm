# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-21

### Added

- Run classification evaluations against Anthropic models with an exact-match evaluator.
- Define evaluations in a YAML config: system prompt, model, and one or more test suites.
- Test cases in JSONL format, with inputs and expected outputs.
- Command-line interface: `init`, `validate`, `run`, `history`, and `show`.
- Persistent run history stored in a local SQLite database.
- Look up past runs by ID prefix (git-style short IDs).
- Rich terminal output with per-suite results and pass rates.
- Self-contained HTML reports with per-suite confusion matrices.