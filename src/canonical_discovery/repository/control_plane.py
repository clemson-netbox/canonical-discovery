"""Repository protocol for control-plane persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from canonical_discovery.control_plane import (
    CollectorSession,
    GraphSubmission,
    Job,
    JobStatus,
    Lease,
    Result,
    Run,
)


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
    def claim_job(
        self,
        *,
        job_id: str,
        claimant_id: str,
        lease_id: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Lease | None:
        raise NotImplementedError

    @abstractmethod
    def save_collector_session(self, session: CollectorSession) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_collector_session(self, collector_instance_id: str) -> CollectorSession | None:
        raise NotImplementedError

    @abstractmethod
    def save_lease(self, lease: Lease) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_lease(self, lease_id: str) -> Lease | None:
        raise NotImplementedError

    @abstractmethod
    def get_lease_for_job(self, job_id: str) -> Lease | None:
        raise NotImplementedError

    @abstractmethod
    def save_result(self, result: Result) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_result(self, result_id: str) -> Result | None:
        raise NotImplementedError

    @abstractmethod
    def save_graph_submission(self, submission: GraphSubmission) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_graph_submission(self, submission_id: str) -> GraphSubmission | None:
        raise NotImplementedError

    @abstractmethod
    def get_graph_submission_for_lease(self, lease_id: str) -> GraphSubmission | None:
        raise NotImplementedError

    @abstractmethod
    def finalize_job_result(
        self,
        *,
        job: Job,
        lease_id: str,
        result: Result,
        next_status: JobStatus,
    ) -> bool:
        raise NotImplementedError
