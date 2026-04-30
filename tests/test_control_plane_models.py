"""Tests for control-plane runtime models."""

from __future__ import annotations

import unittest
from datetime import datetime

from canonical_discovery.control_plane import (
    Heartbeat,
    Job,
    JobStatus,
    Lease,
    Result,
    Run,
    RunStatus,
    Task,
    TaskStatus,
)


class RunTests(unittest.TestCase):
    def test_run_to_dict_uses_status_value_and_iso_timestamp(self) -> None:
        run = Run(
            run_id="run-1",
            created_at=datetime(2026, 4, 30, 12, 0, 0),
            trigger_type="manual",
            requested_mode="discovery_only",
            status=RunStatus.QUEUED,
        )

        self.assertEqual(
            run.to_dict(),
            {
                "run_id": "run-1",
                "created_at": "2026-04-30T12:00:00",
                "trigger_type": "manual",
                "requested_mode": "discovery_only",
                "status": "queued",
            },
        )


class JobTests(unittest.TestCase):
    def test_job_defaults_and_serialization(self) -> None:
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

        self.assertEqual(job.to_dict()["status"], "claimed")
        self.assertEqual(job.to_dict()["required_tags"], ["vmware"])
        self.assertEqual(job.to_dict()["attempt_count"], 1)


class TaskTests(unittest.TestCase):
    def test_task_serialization_uses_status_value(self) -> None:
        task = Task(
            task_id="task-1", job_id="job-1", task_kind="adapter", status=TaskStatus.RUNNING
        )

        self.assertEqual(task.to_dict()["status"], "running")


class LeaseTests(unittest.TestCase):
    def test_lease_serialization_handles_optional_heartbeat(self) -> None:
        lease = Lease(
            lease_id="lease-1",
            job_id="job-1",
            claimant_id="collector-a",
            issued_at=datetime(2026, 4, 30, 12, 0, 0),
            expires_at=datetime(2026, 4, 30, 12, 5, 0),
        )

        self.assertIsNone(lease.to_dict()["last_heartbeat_at"])


class HeartbeatTests(unittest.TestCase):
    def test_heartbeat_serialization_preserves_progress(self) -> None:
        heartbeat = Heartbeat(
            lease_id="lease-1",
            observed_at=datetime(2026, 4, 30, 12, 1, 0),
            status="running",
            progress="50%",
        )

        self.assertEqual(heartbeat.to_dict()["progress"], "50%")


class ResultTests(unittest.TestCase):
    def test_result_serialization_copies_metrics_and_artifacts(self) -> None:
        result = Result(
            result_id="result-1",
            job_id="job-1",
            status="succeeded",
            summary="collector finished",
            metrics={"nodes": 4, "duration_seconds": 1.5},
            artifact_refs=("artifact-1",),
        )

        serialized = result.to_dict()

        self.assertEqual(serialized["metrics"], {"nodes": 4, "duration_seconds": 1.5})
        self.assertEqual(serialized["artifact_refs"], ["artifact-1"])


if __name__ == "__main__":
    unittest.main()
