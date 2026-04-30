"""Tests for core enum definitions fixed by the RFCs."""

from __future__ import annotations

import unittest

from canonical_discovery.core import AuthorityMode, AuthorityTier, Category, EdgeType, NodeScope


def enum_values(enum_type: type) -> list[str]:
    return [member.value for member in enum_type]


class NodeScopeTests(unittest.TestCase):
    def test_node_scope_values_match_rfc(self) -> None:
        self.assertEqual(
            enum_values(NodeScope),
            [
                "physical_device",
                "device_component",
                "port",
                "link",
                "ip_address",
                "network_segment",
                "virtual_machine",
                "os_instance",
                "location",
            ],
        )


class EdgeTypeTests(unittest.TestCase):
    def test_edge_type_values_match_rfc(self) -> None:
        self.assertEqual(
            enum_values(EdgeType),
            [
                "contains",
                "hosts",
                "connected_to",
                "member_of",
                "assigned_to",
                "located_in",
                "backs",
                "observed_by",
            ],
        )


class CategoryTests(unittest.TestCase):
    def test_category_values_match_rfc(self) -> None:
        self.assertEqual(
            enum_values(Category),
            [
                "identity",
                "hardware_inventory",
                "module_inventory",
                "virtualization",
                "operating_system",
                "network_l1_l2",
                "network_l3",
                "topology",
                "placement",
                "ownership_context",
                "telemetry",
            ],
        )


class AuthorityTierTests(unittest.TestCase):
    def test_authority_tier_values_match_rfc(self) -> None:
        self.assertEqual(
            enum_values(AuthorityTier),
            ["authoritative", "preferred", "supplemental", "observe_only"],
        )


class AuthorityModeTests(unittest.TestCase):
    def test_authority_mode_values_match_rfc(self) -> None:
        self.assertEqual(
            enum_values(AuthorityMode),
            ["replace", "fill_if_missing", "merge", "observe_only"],
        )


class ExportTests(unittest.TestCase):
    def test_enum_members_are_string_like(self) -> None:
        self.assertEqual(NodeScope.PHYSICAL_DEVICE, "physical_device")
        self.assertEqual(EdgeType.CONNECTED_TO, "connected_to")
        self.assertEqual(Category.HARDWARE_INVENTORY, "hardware_inventory")
        self.assertEqual(AuthorityTier.AUTHORITATIVE, "authoritative")
        self.assertEqual(AuthorityMode.FILL_IF_MISSING, "fill_if_missing")


if __name__ == "__main__":
    unittest.main()
