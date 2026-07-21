# evallm

> Test and evaluate LLM outputs against expected results - from the command line

**evallm** lets you define test cases (inputs and expected outputs), run them against an LLM, and see where it succeeds or fails. Use it to catch prompt regressions, compare prompts and models, and see results in the terminal or as a self-contained HTML report.

## Installation

```bash
pip install evallm-cli
```

evallm requires Python 3.10+ and an Anthropic API key.

Get an API key from the [Anthropic Console](https://console.anthropic.com/).

Set your API key as an environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

The `export` command only works in the current session. To make it permanent, add it to your shell config — `~/.zshrc` for zsh or `~/.bashrc` for bash.

## Quick start

Create a new evaluation project:

```bash
evallm init my-eval
cd my-eval
```

This creates the project structure. The key files are the config (`evallm.yaml`) and the test suites (`suites/`):

```
my-eval/
├── evallm.yaml
├── suites/
│   └── example.jsonl
└── results/
```

Configure your evaluation in `evallm.yaml`:

```yaml
name: my-sentiment-eval
description: Sentiment classification for product reviews

system_under_test:
  provider: anthropic
  model: claude-sonnet-4-6
  system_prompt: |
    Classify the sentiment of the review as one of: positive, negative, neutral.
    Return only the label, nothing else.
  temperature: 0.0
  max_tokens: 100

suites:
  - name: sentiment_v1
    file: suites/example.jsonl
    evaluator: exact_match
```

Inside `suites/` you can create multiple `.jsonl` files, each a separate test suite. Define test cases in each of them, like in this example:

```jsonl
{"input": "This product is amazing!", "expected": "positive"}
{"input": "Terrible experience, would not recommend", "expected": "negative"}
{"input": "It works as described", "expected": "neutral"}
```

Each line is a single test case with an `input` (sent to the LLM) and an `expected` output (compared against the response).

Run the evaluation:

```bash
evallm run evallm.yaml
```

evallm prints a summary panel with the timestamp, total score, and pass rate, followed by per-suite results.

Use `--report` or `-r` to also generate a self-contained HTML report, saved next to the config file. Use `--cases` or `-c` to see detailed per-case results in the terminal.

## Commands

| Command | Description |
|---------|-------------|
| `evallm init <name>` | Create a new evaluation project |
| `evallm validate <config>` | Check a config file for errors |
| `evallm run <config>` | Run evaluation suites |
| `evallm history` | List past runs |
| `evallm show <run-id>` | Show a past run by ID |

The most useful flags for `run`:

- `-r`, `--report` — also generate a self-contained HTML report
- `-c`, `--cases` — show per-case results in the terminal
- `-d`, `--db` — path to the database file (defaults next to the config)

Run `evallm <command> --help` for the full list of options.

## How it works

evallm runs each test case through your configured LLM and scores the output with an evaluator. Evaluators are modular: exact match is available now, with LLM-as-judge planned next.

Every run is saved to a local SQLite database, so you can review past results with `history` and `show`. Runs can also be exported as a self-contained HTML report.

## License

[MIT](LICENSE)