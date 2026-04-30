"""SQLite-backed control-plane repository implementation."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from canonical_discovery.control_plane import (
    CollectorSession,
    GraphSubmission,
    Job,
    JobStatus,
    Lease,
    Result,
    Run,
    RunStatus,
)
from canonical_discovery.repository.control_plane import ControlPlaneRepository


class SQLiteControlPlaneRepository(ControlPlaneRepository):
    """SQLite-backed persistence for control-plane runtime records."""

    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        self._shared_connection = (
            sqlite3.connect(self._database_path) if self._database_path == ":memory:" else None
        )
        if self._shared_connection is not None:
            self._shared_connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def save_run(self, run: Run) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id,
                    created_at,
                    trigger_type,
                    requested_mode,
                    status
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.created_at.isoformat(),
                    run.trigger_type,
                    run.requested_mode,
                    run.status.value,
                ),
            )

    def get_run(self, run_id: str) -> Run | None:
        row = self._fetch_one(
            """
            SELECT run_id, created_at, trigger_type, requested_mode, status
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        )
        if row is None:
            return None

        return Run(
            run_id=row[0],
            created_at=datetime.fromisoformat(row[1]),
            trigger_type=row[2],
            requested_mode=row[3],
            status=RunStatus(row[4]),
        )

    def save_job(self, job: Job) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO jobs (
                    job_id,
                    run_id,
                    job_kind,
                    service_role,
                    required_tags,
                    priority,
                    status,
                    attempt_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.run_id,
                    job.job_kind,
                    job.service_role,
                    json.dumps(list(job.required_tags)),
                    job.priority,
                    job.status.value,
                    job.attempt_count,
                ),
            )

    def get_job(self, job_id: str) -> Job | None:
        row = self._fetch_one(
            """
            SELECT job_id, run_id, job_kind, service_role, required_tags,
                   priority, status, attempt_count
            FROM jobs WHERE job_id = ?
            """,
            (job_id,),
        )
        if row is None:
            return None

        return Job(
            job_id=row[0],
            run_id=row[1],
            job_kind=row[2],
            service_role=row[3],
            required_tags=tuple(json.loads(row[4])),
            priority=row[5],
            status=JobStatus(row[6]),
            attempt_count=row[7],
        )

    def list_jobs(
        self, *, status: JobStatus | None = None, service_role: str | None = None
    ) -> list[Job]:
        where_clauses = []
        params: list[str] = []

        if status is not None:
            where_clauses.append("status = ?")
            params.append(status.value)
        if service_role is not None:
            where_clauses.append("service_role = ?")
            params.append(service_role)

        where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = (
            "SELECT job_id, run_id, job_kind, service_role, required_tags, "
            "priority, status, attempt_count "
            f"FROM jobs{where_sql}"
        )

        with self._connection() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [
            Job(
                job_id=row[0],
                run_id=row[1],
                job_kind=row[2],
                service_role=row[3],
                required_tags=tuple(json.loads(row[4])),
                priority=row[5],
                status=JobStatus(row[6]),
                attempt_count=row[7],
            )
            for row in rows
        ]

    def claim_job(
        self,
        *,
        job_id: str,
        claimant_id: str,
        lease_id: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Lease | None:
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE jobs SET status = ? WHERE job_id = ? AND status = ?",
                (JobStatus.CLAIMED.value, job_id, JobStatus.QUEUED.value),
            )
            if cursor.rowcount != 1:
                return None

            connection.execute(
                """
                INSERT OR REPLACE INTO leases (
                    lease_id,
                    job_id,
                    claimant_id,
                    issued_at,
                    expires_at,
                    last_heartbeat_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lease_id,
                    job_id,
                    claimant_id,
                    issued_at.isoformat(),
                    expires_at.isoformat(),
                    None,
                ),
            )

        return Lease(
            lease_id=lease_id,
            job_id=job_id,
            claimant_id=claimant_id,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def save_collector_session(self, session: CollectorSession) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO collector_sessions (
                    collector_instance_id,
                    collector_version,
                    capability_tags,
                    max_concurrent_jobs,
                    current_active_load,
                    last_known_job_ids,
                    placement,
                    last_check_in_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.collector_instance_id,
                    session.collector_version,
                    json.dumps(list(session.capability_tags)),
                    session.max_concurrent_jobs,
                    session.current_active_load,
                    json.dumps(list(session.last_known_job_ids)),
                    json.dumps(session.placement),
                    session.last_check_in_at.isoformat(),
                ),
            )

    def get_collector_session(self, collector_instance_id: str) -> CollectorSession | None:
        row = self._fetch_one(
            """
            SELECT collector_instance_id, collector_version, capability_tags,
                   max_concurrent_jobs, current_active_load, last_known_job_ids,
                   placement, last_check_in_at
            FROM collector_sessions WHERE collector_instance_id = ?
            """,
            (collector_instance_id,),
        )
        if row is None:
            return None

        return CollectorSession(
            collector_instance_id=row[0],
            collector_version=row[1],
            capability_tags=tuple(json.loads(row[2])),
            max_concurrent_jobs=row[3],
            current_active_load=row[4],
            last_known_job_ids=tuple(json.loads(row[5])),
            placement=json.loads(row[6]),
            last_check_in_at=datetime.fromisoformat(row[7]),
        )

    def save_lease(self, lease: Lease) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO leases (
                    lease_id,
                    job_id,
                    claimant_id,
                    issued_at,
                    expires_at,
                    last_heartbeat_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lease.lease_id,
                    lease.job_id,
                    lease.claimant_id,
                    lease.issued_at.isoformat(),
                    lease.expires_at.isoformat(),
                    lease.last_heartbeat_at.isoformat() if lease.last_heartbeat_at else None,
                ),
            )

    def get_lease(self, lease_id: str) -> Lease | None:
        row = self._fetch_one(
            """
            SELECT lease_id, job_id, claimant_id, issued_at, expires_at, last_heartbeat_at
            FROM leases WHERE lease_id = ?
            """,
            (lease_id,),
        )
        if row is None:
            return None

        return Lease(
            lease_id=row[0],
            job_id=row[1],
            claimant_id=row[2],
            issued_at=datetime.fromisoformat(row[3]),
            expires_at=datetime.fromisoformat(row[4]),
            last_heartbeat_at=datetime.fromisoformat(row[5]) if row[5] is not None else None,
        )

    def get_lease_for_job(self, job_id: str) -> Lease | None:
        row = self._fetch_one(
            """
            SELECT lease_id, job_id, claimant_id, issued_at, expires_at, last_heartbeat_at
            FROM leases WHERE job_id = ?
            ORDER BY issued_at DESC
            LIMIT 1
            """,
            (job_id,),
        )
        if row is None:
            return None

        return Lease(
            lease_id=row[0],
            job_id=row[1],
            claimant_id=row[2],
            issued_at=datetime.fromisoformat(row[3]),
            expires_at=datetime.fromisoformat(row[4]),
            last_heartbeat_at=datetime.fromisoformat(row[5]) if row[5] is not None else None,
        )

    def save_result(self, result: Result) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO results (
                    result_id,
                    job_id,
                    status,
                    summary,
                    metrics,
                    artifact_refs
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.result_id,
                    result.job_id,
                    result.status,
                    result.summary,
                    json.dumps(result.metrics),
                    json.dumps(list(result.artifact_refs)),
                ),
            )

    def get_result(self, result_id: str) -> Result | None:
        row = self._fetch_one(
            """
            SELECT result_id, job_id, status, summary, metrics, artifact_refs
            FROM results WHERE result_id = ?
            """,
            (result_id,),
        )
        if row is None:
            return None

        return Result(
            result_id=row[0],
            job_id=row[1],
            status=row[2],
            summary=row[3],
            metrics=json.loads(row[4]),
            artifact_refs=tuple(json.loads(row[5])),
        )

    def save_graph_submission(self, submission: GraphSubmission) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO graph_submissions (
                    submission_id,
                    collector_instance_id,
                    lease_id,
                    payload,
                    submitted_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    submission.submission_id,
                    submission.collector_instance_id,
                    submission.lease_id,
                    json.dumps(submission.payload),
                    submission.submitted_at.isoformat(),
                ),
            )

    def get_graph_submission(self, submission_id: str) -> GraphSubmission | None:
        row = self._fetch_one(
            """
            SELECT submission_id, collector_instance_id, lease_id, payload, submitted_at
            FROM graph_submissions WHERE submission_id = ?
            """,
            (submission_id,),
        )
        if row is None:
            return None

        return GraphSubmission(
            submission_id=row[0],
            collector_instance_id=row[1],
            lease_id=row[2],
            payload=json.loads(row[3]),
            submitted_at=datetime.fromisoformat(row[4]),
        )

    def _initialize_schema(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    requested_mode TEXT NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    job_kind TEXT NOT NULL,
                    service_role TEXT NOT NULL,
                    required_tags TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    attempt_count INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS leases (
                    lease_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    claimant_id TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_heartbeat_at TEXT
                );

                CREATE TABLE IF NOT EXISTS results (
                    result_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    artifact_refs TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS collector_sessions (
                    collector_instance_id TEXT PRIMARY KEY,
                    collector_version TEXT NOT NULL,
                    capability_tags TEXT NOT NULL,
                    max_concurrent_jobs INTEGER NOT NULL,
                    current_active_load INTEGER NOT NULL,
                    last_known_job_ids TEXT NOT NULL,
                    placement TEXT NOT NULL,
                    last_check_in_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS graph_submissions (
                    submission_id TEXT PRIMARY KEY,
                    collector_instance_id TEXT NOT NULL,
                    lease_id TEXT NOT NULL REFERENCES leases(lease_id),
                    payload TEXT NOT NULL,
                    submitted_at TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def _connection(self):
        if self._shared_connection is not None:
            try:
                yield self._shared_connection
                self._shared_connection.commit()
            except Exception:
                self._shared_connection.rollback()
                raise
            return

        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _fetch_one(self, query: str, params: tuple[str, ...]) -> tuple | None:
        with self._connection() as connection:
            row = connection.execute(query, params).fetchone()
        return row
