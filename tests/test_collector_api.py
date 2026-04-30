"""Tests for the collector lifecycle API."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime

from fastapi.testclient import TestClient

from canonical_discovery.api import create_app
from canonical_discovery.control_plane import Job, JobStatus, Run, RunStatus
from canonical_discovery.repository import SQLiteControlPlaneRepository


class CollectorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile()
        self.repository = SQLiteControlPlaneRepository(self.temp_db.name)
        self.client = TestClient(create_app(self.repository))

        self.repository.save_run(
            Run(
                run_id="run-1",
                created_at=datetime(2026, 4, 30, 12, 0, 0),
                trigger_type="manual",
                requested_mode="discovery_only",
                status=RunStatus.QUEUED,
            )
        )
        self.repository.save_job(
            Job(
                job_id="job-1",
                run_id="run-1",
                job_kind="collect_source",
                service_role="collector",
                required_tags=("vmware",),
                status=JobStatus.QUEUED,
            )
        )

    def tearDown(self) -> None:
        self.temp_db.close()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_check_in_registers_collector(self) -> None:
        response = self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["registered"])

    def test_claim_work_returns_matching_queued_job(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )

        response = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["jobs"]), 1)
        self.assertEqual(self.repository.get_job("job-1").status, JobStatus.CLAIMED)

    def test_claim_work_does_not_double_lease_same_job(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-2",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )

        first = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )
        second = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-2",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )

        self.assertEqual(len(first.json()["jobs"]), 1)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["jobs"], [])

    def test_heartbeat_requires_existing_lease(self) -> None:
        response = self.client.post(
            "/collectors/heartbeat",
            json={
                "collector_instance_id": "collector-1",
                "lease_id": "missing",
                "current_execution_status": "running",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_graph_submission_requires_existing_lease(self) -> None:
        response = self.client.post(
            "/collectors/graph-submissions",
            json={
                "collector_instance_id": "collector-1",
                "lease_id": "missing",
                "payload": {"nodes": []},
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_heartbeat_rejects_claimant_mismatch(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        claim_response = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )
        lease_id = claim_response.json()["jobs"][0]["lease_id"]

        response = self.client.post(
            "/collectors/heartbeat",
            json={
                "collector_instance_id": "collector-2",
                "lease_id": lease_id,
                "current_execution_status": "running",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_result_submission_persists_result_and_updates_job(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        claim_response = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )
        self.assertEqual(claim_response.status_code, 200)

        response = self.client.post(
            "/collectors/results",
            json={
                "collector_instance_id": "collector-1",
                "job_id": "job-1",
                "status": "succeeded",
                "summary": "done",
                "metrics": {"nodes": 4},
                "artifact_refs": ["artifact-1"],
            },
        )

        self.assertEqual(response.status_code, 200)
        result_id = response.json()["result_id"]
        self.assertEqual(self.repository.get_result(result_id).summary, "done")
        self.assertEqual(self.repository.get_job("job-1").status, JobStatus.SUCCEEDED)

    def test_result_submission_rejects_invalid_status_before_persisting_result(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )

        response = self.client.post(
            "/collectors/results",
            json={
                "collector_instance_id": "collector-1",
                "job_id": "job-1",
                "status": "not-a-status",
                "summary": "done",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_result_submission_rejects_non_terminal_status(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )

        response = self.client.post(
            "/collectors/results",
            json={
                "collector_instance_id": "collector-1",
                "job_id": "job-1",
                "status": "queued",
                "summary": "done",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_graph_submission_is_persisted_in_repository(self) -> None:
        self.client.post(
            "/collectors/check-in",
            json={
                "collector_instance_id": "collector-1",
                "collector_version": "1.0",
                "capability_tags": ["vmware"],
                "max_concurrent_jobs": 2,
                "current_active_load": 0,
                "last_known_job_ids": [],
                "placement": {},
            },
        )
        claim_response = self.client.post(
            "/collectors/claim-work",
            json={
                "collector_instance_id": "collector-1",
                "current_load": 0,
                "available_capacity": 1,
                "capability_tags": ["vmware"],
            },
        )
        lease_id = claim_response.json()["jobs"][0]["lease_id"]

        response = self.client.post(
            "/collectors/graph-submissions",
            json={
                "collector_instance_id": "collector-1",
                "lease_id": lease_id,
                "payload": {"nodes": []},
            },
        )

        self.assertEqual(response.status_code, 200)
        submission_id = response.json()["submission_id"]
        self.assertEqual(self.repository.get_graph_submission(submission_id).lease_id, lease_id)


if __name__ == "__main__":
    unittest.main()
