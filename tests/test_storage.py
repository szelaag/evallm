from evallm.storage import SQLiteStorage, AmbiguousPrefixError
from evallm.models import RunResult, SuiteResult, CaseResult, EvalResult
from uuid import uuid4
from datetime import datetime
import pytest


def _case(cid: str, expected: str, actual: str, passed: bool) -> CaseResult:
    return CaseResult(
        id=cid,
        expected=expected,
        actual=actual,
        eval_result=EvalResult(passed=passed, score=float(passed)),
    )


def _sample_run() -> RunResult:
    return RunResult(
        id=uuid4(),
        timestamp=datetime.now(),
        suites=[
            SuiteResult(
                name="sentiment",
                cases=[
                    _case("sentiment#1", "positive", "positive", True),
                    _case("sentiment#2", "negative", "positive", False),
                    _case("sentiment#3", "neutral", "neutral", True),
                ],
            ),
            SuiteResult(
                name="topic",
                cases=[
                    _case("topic#1", "sport", "sport", True),
                    _case("topic#2", "politics", "sport", False),
                ],
            ),
        ],
    )


def _assert_run_equal(loaded: RunResult, expected: RunResult) -> None:
    assert loaded is not None
    assert loaded.id == expected.id
    assert loaded.timestamp == expected.timestamp
    assert loaded.total == expected.total
    assert loaded.passed_count == expected.passed_count
    assert loaded.pass_rate == expected.pass_rate
    assert len(loaded.suites) == len(expected.suites)
    assert loaded.suites[0].passed_count == expected.suites[0].passed_count


def test_sqlite_storage_round_trip(tmp_path):

    run = _sample_run()
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(run)
    loaded = storage.get_run(run.id)

    _assert_run_equal(loaded, run)


def test_get_runs_returns_all(tmp_path):
    run1 = _sample_run()
    run2 = _sample_run()
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(run1)
    storage.save_run(run2)

    loaded_runs = storage.get_runs()

    loaded_ids = {r.id for r in loaded_runs}
    assert run1.id in loaded_ids
    assert run2.id in loaded_ids
    assert len(loaded_runs) == 2


def test_get_run_nonexistent_returns_none(tmp_path):
    storage = SQLiteStorage(tmp_path / "test.db")
    assert storage.get_run(uuid4()) is None


def test_get_run_by_prefix_returns_correct_run(tmp_path):
    run = _sample_run()
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(run)
    loaded = storage.get_run_by_prefix(str(run.id)[:8])

    _assert_run_equal(loaded, run)


def test_get_run_by_prefix_returns_none_if_nonexistent(tmp_path):
    run = _sample_run()
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(run)
    loaded = storage.get_run_by_prefix("nonexistentrun")
    assert loaded is None


def test_get_run_by_prefix_raises_on_ambiguous(tmp_path):
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(_sample_run())
    storage.save_run(_sample_run())
    with pytest.raises(AmbiguousPrefixError):
        storage.get_run_by_prefix("")
