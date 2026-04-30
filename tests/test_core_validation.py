"""Tests for canonical graph invariant validation."""

from __future__ import annotations

import unittest

from canonical_discovery.core import (
    Edge,
    EdgeType,
    GraphArtifact,
    Node,
    NodeScope,
    validate_graph_invariants,
)


class GraphInvariantValidationTests(unittest.TestCase):
    def test_valid_graph_has_no_invariant_errors(self) -> None:
        graph = GraphArtifact(
            nodes=(
                Node(key="device-1", scope=NodeScope.PHYSICAL_DEVICE),
                Node(key="component-1", scope=NodeScope.DEVICE_COMPONENT),
                Node(key="port-a", scope=NodeScope.PORT),
                Node(key="port-b", scope=NodeScope.PORT),
                Node(key="os-1", scope=NodeScope.OS_INSTANCE),
                Node(key="ip-1", scope=NodeScope.IP_ADDRESS),
            ),
            edges=(
                Edge(
                    key="edge-component",
                    edge_type=EdgeType.CONTAINS,
                    source_key="device-1",
                    target_key="component-1",
                ),
                Edge(
                    key="edge-link",
                    edge_type=EdgeType.CONNECTED_TO,
                    source_key="port-a",
                    target_key="port-b",
                ),
                Edge(
                    key="edge-hosts",
                    edge_type=EdgeType.HOSTS,
                    source_key="device-1",
                    target_key="os-1",
                ),
                Edge(
                    key="edge-ip",
                    edge_type=EdgeType.ASSIGNED_TO,
                    source_key="port-a",
                    target_key="ip-1",
                ),
            ),
        )

        self.assertEqual(validate_graph_invariants(graph), [])

    def test_os_instance_requires_exactly_one_hosting_edge(self) -> None:
        graph = GraphArtifact(
            nodes=(
                Node(key="device-1", scope=NodeScope.PHYSICAL_DEVICE),
                Node(key="device-2", scope=NodeScope.PHYSICAL_DEVICE),
                Node(key="os-1", scope=NodeScope.OS_INSTANCE),
            ),
            edges=(
                Edge(
                    key="edge-hosts-1",
                    edge_type=EdgeType.HOSTS,
                    source_key="device-1",
                    target_key="os-1",
                ),
                Edge(
                    key="edge-hosts-2",
                    edge_type=EdgeType.HOSTS,
                    source_key="device-2",
                    target_key="os-1",
                ),
            ),
        )

        self.assertEqual(
            validate_graph_invariants(graph),
            ["os_instance 'os-1' must have exactly one hosts edge, found 2"],
        )

    def test_connected_to_requires_port_nodes(self) -> None:
        graph = GraphArtifact(
            nodes=(
                Node(key="device-1", scope=NodeScope.PHYSICAL_DEVICE),
                Node(key="port-1", scope=NodeScope.PORT),
            ),
            edges=(
                Edge(
                    key="edge-link",
                    edge_type=EdgeType.CONNECTED_TO,
                    source_key="device-1",
                    target_key="port-1",
                ),
            ),
        )

        self.assertEqual(
            validate_graph_invariants(graph),
            [
                "connected_to edge 'edge-link' must connect port nodes, not "
                "'physical_device' -> 'port'"
            ],
        )

    def test_device_component_requires_supported_parent_scope(self) -> None:
        graph = GraphArtifact(
            nodes=(
                Node(key="vm-1", scope=NodeScope.VIRTUAL_MACHINE),
                Node(key="component-1", scope=NodeScope.DEVICE_COMPONENT),
            ),
            edges=(
                Edge(
                    key="edge-component",
                    edge_type=EdgeType.CONTAINS,
                    source_key="vm-1",
                    target_key="component-1",
                ),
            ),
        )

        self.assertEqual(
            validate_graph_invariants(graph),
            [
                "device_component 'component-1' must attach to a physical_device or "
                "device_component, not 'virtual_machine'"
            ],
        )

    def test_ip_address_requires_assigned_to_relationship(self) -> None:
        graph = GraphArtifact(
            nodes=(
                Node(key="port-1", scope=NodeScope.PORT),
                Node(key="ip-1", scope=NodeScope.IP_ADDRESS),
            ),
            edges=(
                Edge(
                    key="edge-ip",
                    edge_type=EdgeType.CONTAINS,
                    source_key="port-1",
                    target_key="ip-1",
                ),
            ),
        )

        self.assertEqual(
            validate_graph_invariants(graph),
            ["ip_address 'ip-1' must be attached with assigned_to, not 'contains'"],
        )

    def test_unknown_edge_endpoint_is_reported(self) -> None:
        graph = GraphArtifact(
            nodes=(Node(key="port-1", scope=NodeScope.PORT),),
            edges=(
                Edge(
                    key="edge-missing",
                    edge_type=EdgeType.CONNECTED_TO,
                    source_key="port-1",
                    target_key="port-2",
                ),
            ),
        )

        self.assertEqual(
            validate_graph_invariants(graph),
            ["edge 'edge-missing' references unknown target 'port-2'"],
        )


if __name__ == "__main__":
    unittest.main()
