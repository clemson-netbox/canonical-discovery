"""Graph invariant validation helpers for canonical graph artifacts."""

from __future__ import annotations

from canonical_discovery.core.enums import EdgeType, NodeScope
from canonical_discovery.core.models import GraphArtifact


def validate_graph_invariants(graph: GraphArtifact) -> list[str]:
    """Return invariant violations for the provided canonical graph."""

    node_scope_by_key = {node.key: node.scope for node in graph.nodes}
    errors: list[str] = []
    hosting_edges_by_target = {}
    connected_to_edges_by_link = {}
    seen_device_component_attachments = set()
    valid_device_component_attachments = set()
    seen_ip_address_attachments = set()
    valid_ip_address_attachments = set()

    for edge in graph.edges:
        if edge.source_key not in node_scope_by_key:
            errors.append(f"edge '{edge.key}' references unknown source '{edge.source_key}'")
            continue
        if edge.target_key not in node_scope_by_key:
            errors.append(f"edge '{edge.key}' references unknown target '{edge.target_key}'")
            continue

        source_scope = node_scope_by_key[edge.source_key]
        target_scope = node_scope_by_key[edge.target_key]

        if edge.edge_type is EdgeType.HOSTS and target_scope is NodeScope.OS_INSTANCE:
            if source_scope not in {NodeScope.PHYSICAL_DEVICE, NodeScope.VIRTUAL_MACHINE}:
                errors.append(
                    f"os_instance '{edge.target_key}' must be hosted by a compute object, not "
                    f"'{source_scope.value}'"
                )
            hosting_edges_by_target.setdefault(edge.target_key, []).append(edge.key)

        if edge.edge_type is EdgeType.CONNECTED_TO and source_scope is NodeScope.LINK:
            connected_to_edges_by_link.setdefault(edge.source_key, []).append(
                (edge.key, target_scope)
            )

        if target_scope is NodeScope.DEVICE_COMPONENT and source_scope not in {
            NodeScope.PHYSICAL_DEVICE,
            NodeScope.DEVICE_COMPONENT,
        }:
            seen_device_component_attachments.add(edge.target_key)
            errors.append(
                f"device_component '{edge.target_key}' must attach to a physical_device or "
                f"device_component, not '{source_scope.value}'"
            )
        elif target_scope is NodeScope.DEVICE_COMPONENT:
            seen_device_component_attachments.add(edge.target_key)
            valid_device_component_attachments.add(edge.target_key)

        if (
            edge.edge_type is EdgeType.CONNECTED_TO
            and source_scope is not NodeScope.LINK
            and (source_scope is not NodeScope.PORT or target_scope is not NodeScope.PORT)
        ):
            errors.append(
                f"connected_to edge '{edge.key}' must connect port nodes, not "
                f"'{source_scope.value}' -> '{target_scope.value}'"
            )

        if target_scope is NodeScope.IP_ADDRESS and edge.edge_type is not EdgeType.ASSIGNED_TO:
            seen_ip_address_attachments.add(edge.target_key)
            errors.append(
                f"ip_address '{edge.target_key}' must be attached with assigned_to, not "
                f"'{edge.edge_type.value}'"
            )
        elif target_scope is NodeScope.IP_ADDRESS:
            seen_ip_address_attachments.add(edge.target_key)
            valid_ip_address_attachments.add(edge.target_key)

    for node_key, scope in node_scope_by_key.items():
        if scope is NodeScope.OS_INSTANCE:
            hosting_edges = hosting_edges_by_target.get(node_key, [])
            if len(hosting_edges) != 1:
                errors.append(
                    f"os_instance '{node_key}' must have exactly one hosts edge, found "
                    f"{len(hosting_edges)}"
                )

        if scope is NodeScope.LINK:
            connected_edges = connected_to_edges_by_link.get(node_key, [])
            if len(connected_edges) != 2:
                errors.append(
                    f"link '{node_key}' must connect exactly two port endpoints, found "
                    f"{len(connected_edges)}"
                )
                continue

            if any(target_scope is not NodeScope.PORT for _, target_scope in connected_edges):
                errors.append(f"link '{node_key}' must connect only port endpoints")

        if (
            scope is NodeScope.DEVICE_COMPONENT
            and node_key not in seen_device_component_attachments
            and node_key not in valid_device_component_attachments
        ):
            errors.append(
                f"device_component '{node_key}' must attach to a physical_device or "
                f"device_component"
            )

        if (
            scope is NodeScope.IP_ADDRESS
            and node_key not in seen_ip_address_attachments
            and node_key not in valid_ip_address_attachments
        ):
            errors.append(f"ip_address '{node_key}' must have an explicit assigned_to relationship")

    return errors
