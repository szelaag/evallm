from evallm.models import RunResult, SuiteResult, CaseResult, EvalResult
from uuid import UUID
from abc import ABC, abstractmethod
from pathlib import Path
import sqlite3
from datetime import datetime


class Storage(ABC):
    @abstractmethod
    def save_run(self, run: RunResult) -> None: ...
    @abstractmethod
    def get_runs(self) -> list[RunResult]: ...
    @abstractmethod
    def get_run(self, id: UUID) -> RunResult | None: ...


class SQLiteStorage(Storage):
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            pass_rate REAL NOT NULL CHECK (pass_rate >= 0 AND pass_rate <= 1),
            passed_count INTEGER NOT NULL,
            total INTEGER NOT NULL
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS suites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            name TEXT NOT NULL,
            pass_rate REAL NOT NULL CHECK (pass_rate >= 0 AND pass_rate <= 1),
            passed_count INTEGER NOT NULL,
            total INTEGER NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suite_id INTEGER NOT NULL,
            case_label TEXT NOT NULL,
            expected TEXT NOT NULL,
            actual TEXT NOT NULL,
            passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
            score REAL NOT NULL CHECK (score >= 0 AND score <= 1),
            FOREIGN KEY (suite_id) REFERENCES suites(id)
        )
        """)

        self.conn.commit()

    def save_run(self, run: RunResult) -> None:
        self.conn.execute(
            "INSERT INTO runs (id, timestamp, pass_rate, passed_count, total) VALUES (?, ?, ?, ?, ?)",
            (
                str(run.id),
                run.timestamp.isoformat(),
                run.pass_rate,
                run.passed_count,
                run.total,
            ),
        )
        for suite in run.suites:
            cursor = self.conn.execute(
                "INSERT INTO suites (run_id, name, pass_rate, passed_count, total) VALUES (?, ?, ?, ?, ?)",
                (
                    str(run.id),
                    suite.name,
                    suite.pass_rate,
                    suite.passed_count,
                    suite.total,
                ),
            )
            suite_id = cursor.lastrowid
            for case in suite.cases:
                self.conn.execute(
                    "INSERT INTO cases (suite_id, case_label, expected, actual, passed, score) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        suite_id,
                        case.id,
                        case.expected,
                        case.actual,
                        int(case.eval_result.passed),
                        case.eval_result.score,
                    ),
                )
        self.conn.commit()

    def _get_cases(self, suite_id: int) -> list[CaseResult]:
        cases: list[CaseResult] = []
        cursor = self.conn.execute(
            "SELECT * FROM cases WHERE suite_id = ?", (suite_id,)
        )
        rows = cursor.fetchall()
        for row in rows:
            cases.append(
                CaseResult(
                    id=row[2],  # case_label
                    expected=row[3],
                    actual=row[4],
                    eval_result=EvalResult(passed=bool(row[5]), score=row[6]),
                )
            )
        return cases

    def _get_suites(self, run_id: str) -> list[SuiteResult]:
        suites: list[SuiteResult] = []
        cursor = self.conn.execute("SELECT * FROM suites WHERE run_id = ?", (run_id,))
        rows = cursor.fetchall()
        for row in rows:
            suites.append(SuiteResult(name=row[2], cases=self._get_cases(row[0])))
        return suites

    def get_run(self, id: UUID) -> RunResult | None:
        cursor = self.conn.execute("SELECT * FROM runs WHERE id = ?", (str(id),))
        row = cursor.fetchone()

        if row is None:
            return None

        return RunResult(
            id=id,
            timestamp=datetime.fromisoformat(row[1]),
            suites=self._get_suites(row[0]),
        )

    def get_runs(self) -> list[RunResult]:
        runs: list[RunResult] = []
        cursor = self.conn.execute("SELECT * FROM runs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        for row in rows:
            runs.append(
                RunResult(
                    id=UUID(row[0]),
                    timestamp=datetime.fromisoformat(row[1]),
                    suites=self._get_suites(row[0]),
                )
            )
        return runs


def create_storage(db_path: Path) -> Storage:
    return SQLiteStorage(db_path)
