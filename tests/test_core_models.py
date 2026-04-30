"""Tests for core dataclass models."""

from __future__ import annotations

import unittest
from datetime import datetime

from canonical_discovery.core import (
    AuthorityMode,
    AuthorityTier,
    Category,
    Edge,
    EdgeClaim,
    EdgeType,
    GraphArtifact,
    Node,
    NodeClaim,
    NodeScope,
)


class NodeTests(unittest.TestCase):
    def test_node_captures_key_and_scope(self) -> None:
        node = Node(key="device-1", scope=NodeScope.PHYSICAL_DEVICE)

        self.assertEqual(node.key, "device-1")
        self.assertEqual(node.scope, NodeScope.PHYSICAL_DEVICE)


class EdgeTests(unittest.TestCase):
    def test_edge_captures_type_and_endpoints(self) -> None:
        edge = Edge(
            key="edge-1",
            edge_type=EdgeType.CONNECTED_TO,
            source_key="port-a",
            target_key="port-b",
        )

        self.assertEqual(edge.key, "edge-1")
        self.assertEqual(edge.edge_type, EdgeType.CONNECTED_TO)
        self.assertEqual(edge.source_key, "port-a")
        self.assertEqual(edge.target_key, "port-b")


class NodeClaimTests(unittest.TestCase):
    def test_node_claim_defaults_match_minimal_contract(self) -> None:
        claim = NodeClaim(
            node_key="device-1",
            scope=NodeScope.PHYSICAL_DEVICE,
            category=Category.IDENTITY,
            field_name="hostname",
            value="router-1",
            source_name="example-source",
        )

        self.assertEqual(claim.node_key, "device-1")
        self.assertEqual(claim.scope, NodeScope.PHYSICAL_DEVICE)
        self.assertEqual(claim.category, Category.IDENTITY)
        self.assertEqual(claim.field_name, "hostname")
        self.assertEqual(claim.value, "router-1")
        self.assertEqual(claim.source_name, "example-source")
        self.assertEqual(claim.provenance, {})
        self.assertIsNone(claim.timestamp)
        self.assertEqual(claim.authority_tier, AuthorityTier.SUPPLEMENTAL)
        self.assertEqual(claim.confidence, 0.0)
        self.assertEqual(claim.mode, AuthorityMode.REPLACE)

    def test_node_claim_accepts_explicit_provenance_and_resolution_fields(self) -> None:
        timestamp = datetime(2026, 4, 30, 12, 0, 0)
        claim = NodeClaim(
            node_key="device-1",
            scope=NodeScope.PHYSICAL_DEVICE,
            category=Category.HARDWARE_INVENTORY,
            field_name="serial",
            value="ABC123",
            source_name="inventory-source",
            provenance={"record_id": "42"},
            timestamp=timestamp,
            authority_tier=AuthorityTier.AUTHORITATIVE,
            confidence=1.0,
            mode=AuthorityMode.FILL_IF_MISSING,
        )

        self.assertEqual(claim.provenance, {"record_id": "42"})
        self.assertEqual(claim.timestamp, timestamp)
        self.assertEqual(claim.authority_tier, AuthorityTier.AUTHORITATIVE)
        self.assertEqual(claim.confidence, 1.0)
        self.assertEqual(claim.mode, AuthorityMode.FILL_IF_MISSING)


class EdgeClaimTests(unittest.TestCase):
    def test_edge_claim_defaults_match_minimal_contract(self) -> None:
        claim = EdgeClaim(
            edge_key="edge-1",
            edge_type=EdgeType.CONNECTED_TO,
            category=Category.TOPOLOGY,
            field_name="state",
            value="up",
            source_name="example-source",
        )

        self.assertEqual(claim.edge_key, "edge-1")
        self.assertEqual(claim.edge_type, EdgeType.CONNECTED_TO)
        self.assertEqual(claim.category, Category.TOPOLOGY)
        self.assertEqual(claim.field_name, "state")
        self.assertEqual(claim.value, "up")
        self.assertEqual(claim.source_name, "example-source")
        self.assertEqual(claim.provenance, {})
        self.assertIsNone(claim.timestamp)
        self.assertEqual(claim.authority_tier, AuthorityTier.SUPPLEMENTAL)
        self.assertEqual(claim.confidence, 0.0)
        self.assertEqual(claim.mode, AuthorityMode.REPLACE)


class GraphArtifactTests(unittest.TestCase):
    def test_graph_artifact_groups_nodes_edges_and_claims(self) -> None:
        node = Node(key="device-1", scope=NodeScope.PHYSICAL_DEVICE)
        edge = Edge(
            key="edge-1",
            edge_type=EdgeType.CONTAINS,
            source_key="device-1",
            target_key="component-1",
        )
        claim = NodeClaim(
            node_key="device-1",
            scope=NodeScope.PHYSICAL_DEVICE,
            category=Category.IDENTITY,
            field_name="hostname",
            value="router-1",
            source_name="example-source",
        )

        artifact = GraphArtifact(nodes=(node,), edges=(edge,), claims=(claim,))

        self.assertEqual(artifact.nodes, (node,))
        self.assertEqual(artifact.edges, (edge,))
        self.assertEqual(artifact.claims, (claim,))

    def test_graph_artifact_defaults_to_empty_tuples(self) -> None:
        artifact = GraphArtifact()

        self.assertEqual(artifact.nodes, ())
        self.assertEqual(artifact.edges, ())
        self.assertEqual(artifact.claims, ())


if __name__ == "__main__":
    unittest.main()
