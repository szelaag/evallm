from evallm.storage import SQLiteStorage
from evallm.models import RunResult, SuiteResult, CaseResult, EvalResult
from uuid import uuid4
from datetime import datetime


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


def test_sqlite_storage_round_trip(tmp_path):

    run = _sample_run()
    storage = SQLiteStorage(tmp_path / "test.db")
    storage.save_run(run)
    loaded = storage.get_run(run.id)

    assert loaded is not None
    assert loaded.id == run.id
    assert loaded.timestamp == run.timestamp
    assert loaded.total == run.total
    assert loaded.passed_count == run.passed_count
    assert loaded.pass_rate == run.pass_rate
    assert len(loaded.suites) == len(run.suites)
    assert loaded.suites[0].passed_count == run.suites[0].passed_count


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
