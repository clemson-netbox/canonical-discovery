"""Tests for the SQLite-backed control-plane repository."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime

from canonical_discovery.control_plane import Job, JobStatus, Lease, Result, Run, RunStatus
from canonical_discovery.repository import SQLiteControlPlaneRepository


class SQLiteControlPlaneRepositoryTests(unittest.TestCase):
    def test_round_trip_run_job_lease_and_result(self) -> None:
        with tempfile.NamedTemporaryFile() as temp_db:
            repository = SQLiteControlPlaneRepository(temp_db.name)

            run = Run(
                run_id="run-1",
                created_at=datetime(2026, 4, 30, 12, 0, 0),
                trigger_type="manual",
                requested_mode="discovery_only",
                status=RunStatus.QUEUED,
            )
            job = Job(
                job_id="job-1",
                run_id="run-1",
                job_kind="collect_source",
                service_role="collector",
                required_tags=("vmware",),
                priority=5,
                status=JobStatus.CLAIMED,
                attempt_count=1,
            )
            lease = Lease(
                lease_id="lease-1",
                job_id="job-1",
                claimant_id="collector-a",
                issued_at=datetime(2026, 4, 30, 12, 0, 0),
                expires_at=datetime(2026, 4, 30, 12, 5, 0),
            )
            result = Result(
                result_id="result-1",
                job_id="job-1",
                status="succeeded",
                summary="collector finished",
                metrics={"nodes": 4, "duration_seconds": 1.5},
                artifact_refs=("artifact-1",),
            )

            repository.save_run(run)
            repository.save_job(job)
            repository.save_lease(lease)
            repository.save_result(result)

            self.assertEqual(repository.get_run("run-1"), run)
            self.assertEqual(repository.get_job("job-1"), job)
            self.assertEqual(repository.get_lease("lease-1"), lease)
            self.assertEqual(repository.get_result("result-1"), result)

    def test_missing_records_return_none(self) -> None:
        with tempfile.NamedTemporaryFile() as temp_db:
            repository = SQLiteControlPlaneRepository(temp_db.name)

            self.assertIsNone(repository.get_run("missing"))
            self.assertIsNone(repository.get_job("missing"))
            self.assertIsNone(repository.get_lease("missing"))
            self.assertIsNone(repository.get_result("missing"))


if __name__ == "__main__":
    unittest.main()
