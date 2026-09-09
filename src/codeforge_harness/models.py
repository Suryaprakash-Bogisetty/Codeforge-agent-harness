"""Core data types shared across the harness."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Outcome(StrEnum):
    """Terminal state of a run (see codeforge-benchmark/CONTRACT.md §5)."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    REGRESSED = "regressed"
    ERRORED = "errored"
    BUDGET_EXCEEDED = "budget_exceeded"
    STUCK = "stuck"
    INFRA_FAILURE = "infra_failure"


class TaskConstraints(BaseModel):
    max_iterations: int
    timeout_seconds: int
    max_tool_calls: int
    max_cost_usd: float


class FailToPass(BaseModel):
    public: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)

    @property
    def all(self) -> list[str]:
        return [*self.public, *self.hidden]


class TaskSpec(BaseModel):
    """A benchmark task, resolved from tasks/<id>/task.yaml + statement.md."""

    id: str
    title: str
    category: str
    difficulty: int
    base_commit: str
    bug_patch: str | None = None  # filename within task_dir, applied to the workspace
    statement: str  # full text of statement.md
    forbidden_paths: list[str] = Field(default_factory=list)
    fail_to_pass: FailToPass
    pass_to_pass: list[str]
    test_command: str
    test_timeout_seconds: int = 300
    constraints: TaskConstraints

    task_dir: Path
    reference_patch: str | None = None  # filename within task_dir; never given to the agent


class ExecResult(BaseModel):
    """Outcome of one command run inside the sandbox."""

    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool = False
    truncated: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


class TestReport(BaseModel):
    """Result of running one group of pytest node ids."""

    node_ids: list[str]
    returncode: int
    duration_s: float
    failures: list[str] = Field(default_factory=list)  # node ids that did not pass
    collection_error: bool = False
    raw_tail: str = ""

    @property
    def all_passed(self) -> bool:
        return self.returncode == 0 and not self.collection_error and not self.failures


class RunRecord(BaseModel):
    """Written to runs/<run_id>/result.json."""

    run_id: str
    task_id: str
    agent: str
    outcome: Outcome
    started_at: str
    finished_at: str
    iterations: int = 0
    tool_calls: int = 0
    fail_to_pass_passed: bool = False
    pass_to_pass_passed: bool = False
    regressions: list[str] = Field(default_factory=list)
    diff: str = ""
    error: str | None = None
