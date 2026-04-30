"""Control-plane dataclass models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from canonical_discovery.control_plane.status import JobStatus, RunStatus, TaskStatus


@dataclass(frozen=True, slots=True)
class Run:
    run_id: str
    created_at: datetime
    trigger_type: str
    requested_mode: str
    status: RunStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat(),
            "trigger_type": self.trigger_type,
            "requested_mode": self.requested_mode,
            "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class Job:
    job_id: str
    run_id: str
    job_kind: str
    service_role: str
    required_tags: tuple[str, ...] = ()
    priority: int = 0
    status: JobStatus = JobStatus.PENDING
    attempt_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "run_id": self.run_id,
            "job_kind": self.job_kind,
            "service_role": self.service_role,
            "required_tags": list(self.required_tags),
            "priority": self.priority,
            "status": self.status.value,
            "attempt_count": self.attempt_count,
        }


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    job_id: str
    task_kind: str
    status: TaskStatus = TaskStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "job_id": self.job_id,
            "task_kind": self.task_kind,
            "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class Lease:
    lease_id: str
    job_id: str
    claimant_id: str
    issued_at: datetime
    expires_at: datetime
    last_heartbeat_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "job_id": self.job_id,
            "claimant_id": self.claimant_id,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_heartbeat_at": self.last_heartbeat_at.isoformat()
            if self.last_heartbeat_at is not None
            else None,
        }


@dataclass(frozen=True, slots=True)
class Heartbeat:
    lease_id: str
    observed_at: datetime
    status: str
    progress: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "observed_at": self.observed_at.isoformat(),
            "status": self.status,
            "progress": self.progress,
        }


@dataclass(frozen=True, slots=True)
class Result:
    result_id: str
    job_id: str
    status: str
    summary: str
    metrics: dict[str, int | float] = field(default_factory=dict)
    artifact_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "job_id": self.job_id,
            "status": self.status,
            "summary": self.summary,
            "metrics": dict(self.metrics),
            "artifact_refs": list(self.artifact_refs),
        }
