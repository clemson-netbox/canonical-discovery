"""Minimal collector lifecycle API application."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from canonical_discovery.control_plane import (
    CollectorSession,
    GraphSubmission,
    Job,
    JobStatus,
    Lease,
    Result,
)
from canonical_discovery.repository import ControlPlaneRepository, SQLiteControlPlaneRepository

LEASE_TTL_SECONDS = 300
CHECK_IN_INTERVAL_SECONDS = 60


class CollectorCheckInRequest(BaseModel):
    collector_instance_id: str
    collector_version: str
    capability_tags: list[str] = Field(default_factory=list)
    max_concurrent_jobs: int
    current_active_load: int
    last_known_job_ids: list[str] = Field(default_factory=list)
    placement: dict[str, str] = Field(default_factory=dict)


class CollectorCheckInResponse(BaseModel):
    collector_instance_id: str
    registered: bool
    next_check_in_seconds: int


class ClaimWorkRequest(BaseModel):
    collector_instance_id: str
    current_load: int
    available_capacity: int
    capability_tags: list[str] = Field(default_factory=list)
    preferred_batch_size: int | None = None


class ClaimedJobResponse(BaseModel):
    job_id: str
    run_id: str
    lease_id: str
    lease_expires_at: str
    job_kind: str
    execution_parameters: dict[str, Any] = Field(default_factory=dict)
    artifact_submission_required: bool = True


class ClaimWorkResponse(BaseModel):
    jobs: list[ClaimedJobResponse]


class HeartbeatRequest(BaseModel):
    collector_instance_id: str
    lease_id: str
    current_execution_status: str
    progress_summary: str | None = None


class HeartbeatResponse(BaseModel):
    lease_id: str
    lease_expires_at: str
    accepted: bool


class GraphSubmissionRequest(BaseModel):
    collector_instance_id: str
    lease_id: str
    payload: dict[str, Any]


class GraphSubmissionResponse(BaseModel):
    submission_id: str
    accepted: bool


class ResultSubmissionRequest(BaseModel):
    collector_instance_id: str
    job_id: str
    status: str
    summary: str
    metrics: dict[str, int | float] = Field(default_factory=dict)
    artifact_refs: list[str] = Field(default_factory=list)


class ResultSubmissionResponse(BaseModel):
    result_id: str
    accepted: bool


def create_app(repository: ControlPlaneRepository) -> FastAPI:
    app = FastAPI(title="canonical-discovery")
    app.state.repository = repository

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/collectors/check-in", response_model=CollectorCheckInResponse)
    def collector_check_in(request: CollectorCheckInRequest) -> CollectorCheckInResponse:
        repository.save_collector_session(
            CollectorSession(
                collector_instance_id=request.collector_instance_id,
                collector_version=request.collector_version,
                capability_tags=tuple(request.capability_tags),
                max_concurrent_jobs=request.max_concurrent_jobs,
                current_active_load=request.current_active_load,
                last_known_job_ids=tuple(request.last_known_job_ids),
                placement=dict(request.placement),
                last_check_in_at=datetime.now(UTC),
            )
        )
        return CollectorCheckInResponse(
            collector_instance_id=request.collector_instance_id,
            registered=True,
            next_check_in_seconds=CHECK_IN_INTERVAL_SECONDS,
        )

    @app.post("/collectors/claim-work", response_model=ClaimWorkResponse)
    def claim_work(request: ClaimWorkRequest) -> ClaimWorkResponse:
        session = repository.get_collector_session(request.collector_instance_id)
        if session is None:
            raise HTTPException(status_code=404, detail="collector session not found")

        available_capacity = max(request.available_capacity, 0)
        claim_limit = request.preferred_batch_size or available_capacity
        capability_tags = set(request.capability_tags)
        claimed_jobs: list[ClaimedJobResponse] = []

        for job in repository.list_jobs(status=JobStatus.QUEUED, service_role="collector"):
            if available_capacity <= 0 or len(claimed_jobs) >= claim_limit:
                break
            if not set(job.required_tags).issubset(capability_tags):
                continue

            issued_at = datetime.now(UTC)
            expires_at = issued_at + timedelta(seconds=LEASE_TTL_SECONDS)
            lease = Lease(
                lease_id=str(uuid4()),
                job_id=job.job_id,
                claimant_id=request.collector_instance_id,
                issued_at=issued_at,
                expires_at=expires_at,
            )
            repository.save_lease(lease)
            repository.save_job(
                Job(
                    job_id=job.job_id,
                    run_id=job.run_id,
                    job_kind=job.job_kind,
                    service_role=job.service_role,
                    required_tags=job.required_tags,
                    priority=job.priority,
                    status=JobStatus.CLAIMED,
                    attempt_count=job.attempt_count,
                )
            )
            claimed_jobs.append(
                ClaimedJobResponse(
                    job_id=job.job_id,
                    run_id=job.run_id,
                    lease_id=lease.lease_id,
                    lease_expires_at=lease.expires_at.isoformat(),
                    job_kind=job.job_kind,
                )
            )
            available_capacity -= 1

        return ClaimWorkResponse(jobs=claimed_jobs)

    @app.post("/collectors/heartbeat", response_model=HeartbeatResponse)
    def heartbeat(request: HeartbeatRequest) -> HeartbeatResponse:
        lease = repository.get_lease(request.lease_id)
        if lease is None:
            raise HTTPException(status_code=404, detail="lease not found")
        if lease.claimant_id != request.collector_instance_id:
            raise HTTPException(status_code=403, detail="lease claimant mismatch")
        if lease.expires_at <= datetime.now(UTC):
            raise HTTPException(status_code=409, detail="lease expired")

        updated_lease = Lease(
            lease_id=lease.lease_id,
            job_id=lease.job_id,
            claimant_id=lease.claimant_id,
            issued_at=lease.issued_at,
            expires_at=datetime.now(UTC) + timedelta(seconds=LEASE_TTL_SECONDS),
            last_heartbeat_at=datetime.now(UTC),
        )
        repository.save_lease(updated_lease)

        return HeartbeatResponse(
            lease_id=updated_lease.lease_id,
            lease_expires_at=updated_lease.expires_at.isoformat(),
            accepted=True,
        )

    @app.post("/collectors/graph-submissions", response_model=GraphSubmissionResponse)
    def graph_submission(request: GraphSubmissionRequest) -> GraphSubmissionResponse:
        lease = repository.get_lease(request.lease_id)
        if lease is None:
            raise HTTPException(status_code=404, detail="lease not found")
        if lease.claimant_id != request.collector_instance_id:
            raise HTTPException(status_code=403, detail="lease claimant mismatch")
        if lease.expires_at <= datetime.now(UTC):
            raise HTTPException(status_code=409, detail="lease expired")

        submission = GraphSubmission(
            submission_id=str(uuid4()),
            collector_instance_id=request.collector_instance_id,
            lease_id=request.lease_id,
            payload=dict(request.payload),
            submitted_at=datetime.now(UTC),
        )
        repository.save_graph_submission(submission)

        return GraphSubmissionResponse(submission_id=submission.submission_id, accepted=True)

    @app.post("/collectors/results", response_model=ResultSubmissionResponse)
    def result_submission(request: ResultSubmissionRequest) -> ResultSubmissionResponse:
        job = repository.get_job(request.job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        lease = repository.get_lease_for_job(request.job_id)
        if lease is None:
            raise HTTPException(status_code=409, detail="active lease not found for job")
        if lease.claimant_id != request.collector_instance_id:
            raise HTTPException(status_code=403, detail="lease claimant mismatch")
        if lease.expires_at <= datetime.now(UTC):
            raise HTTPException(status_code=409, detail="lease expired")
        if job.status not in {JobStatus.CLAIMED, JobStatus.RUNNING}:
            raise HTTPException(
                status_code=409, detail="job is not claimable for terminal result submission"
            )

        try:
            next_status = JobStatus(request.status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid job status") from exc

        result = Result(
            result_id=str(uuid4()),
            job_id=request.job_id,
            status=request.status,
            summary=request.summary,
            metrics=dict(request.metrics),
            artifact_refs=tuple(request.artifact_refs),
        )
        repository.save_result(result)
        repository.save_job(
            Job(
                job_id=job.job_id,
                run_id=job.run_id,
                job_kind=job.job_kind,
                service_role=job.service_role,
                required_tags=job.required_tags,
                priority=job.priority,
                status=next_status,
                attempt_count=job.attempt_count,
            )
        )

        return ResultSubmissionResponse(result_id=result.result_id, accepted=True)

    return app


DEFAULT_DB_PATH = os.environ.get(
    "CANONICAL_DISCOVERY_DB_PATH", "/var/lib/canonical-discovery/control-plane.db"
)

app = create_app(SQLiteControlPlaneRepository(DEFAULT_DB_PATH))
