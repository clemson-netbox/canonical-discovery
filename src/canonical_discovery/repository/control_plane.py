"""Repository protocol for control-plane persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from canonical_discovery.control_plane import Job, JobStatus, Lease, Result, Run


class ControlPlaneRepository(ABC):
    """Persistence interface for control-plane runtime records."""

    @abstractmethod
    def save_run(self, run: Run) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_run(self, run_id: str) -> Run | None:
        raise NotImplementedError

    @abstractmethod
    def save_job(self, job: Job) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_job(self, job_id: str) -> Job | None:
        raise NotImplementedError

    @abstractmethod
    def list_jobs(
        self, *, status: JobStatus | None = None, service_role: str | None = None
    ) -> list[Job]:
        raise NotImplementedError

    @abstractmethod
    def save_lease(self, lease: Lease) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_lease(self, lease_id: str) -> Lease | None:
        raise NotImplementedError

    @abstractmethod
    def save_result(self, result: Result) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_result(self, result_id: str) -> Result | None:
        raise NotImplementedError
