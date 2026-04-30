"""Tests for the minimal HCL contract dataclasses."""

from __future__ import annotations

import unittest

from canonical_discovery.config import (
    AuthorityBlock,
    AuthorityCategory,
    AuthorityField,
    AuthorityRule,
    AuthorityScope,
    HclDocument,
    PolicyBlock,
    PolicyClassify,
    ProjectionBlock,
    ProjectionScope,
    SourceBlock,
)
from canonical_discovery.core import AuthorityMode, AuthorityTier, Category, NodeScope


class AuthorityModelTests(unittest.TestCase):
    def test_authority_models_capture_scope_category_and_field_rules(self) -> None:
        serial_field = AuthorityField(
            name="serial",
            rule=AuthorityRule(
                tier=AuthorityTier.OBSERVE_ONLY,
                confidence=0,
                mode=AuthorityMode.OBSERVE_ONLY,
            ),
        )
        category = AuthorityCategory(
            category=Category.HARDWARE_INVENTORY,
            rule=AuthorityRule(
                tier=AuthorityTier.SUPPLEMENTAL,
                confidence=20,
                mode=AuthorityMode.FILL_IF_MISSING,
            ),
            fields=(serial_field,),
        )
        scope = AuthorityScope(
            scope=NodeScope.PHYSICAL_DEVICE,
            categories=(category,),
        )
        authority = AuthorityBlock(scopes=(scope,))

        self.assertEqual(authority.scopes, (scope,))
        self.assertEqual(scope.categories, (category,))
        self.assertEqual(category.fields, (serial_field,))


class SourceBlockTests(unittest.TestCase):
    def test_source_block_matches_minimal_source_authority_example(self) -> None:
        source = SourceBlock(
            name="xclarity",
            api_type="xclarity",
            authority=AuthorityBlock(
                scopes=(
                    AuthorityScope(
                        scope=NodeScope.PHYSICAL_DEVICE,
                        categories=(
                            AuthorityCategory(
                                category=Category.HARDWARE_INVENTORY,
                                rule=AuthorityRule(
                                    tier=AuthorityTier.AUTHORITATIVE,
                                    confidence=100,
                                    mode=AuthorityMode.REPLACE,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        self.assertEqual(source.name, "xclarity")
        self.assertEqual(source.api_type, "xclarity")
        self.assertIsNotNone(source.authority)
        self.assertEqual(source.options, {})


class PolicyBlockTests(unittest.TestCase):
    def test_policy_block_captures_classification_attributes(self) -> None:
        policy = PolicyBlock(
            name="campus-defaults",
            classifications=(
                PolicyClassify(
                    target="location",
                    attributes={"site_map": "regex/site_map"},
                ),
                PolicyClassify(
                    target="physical_device",
                    attributes={"owner_group_map": "map/platform_owner"},
                ),
            ),
        )

        self.assertEqual(policy.name, "campus-defaults")
        self.assertEqual(len(policy.classifications), 2)
        self.assertEqual(policy.classifications[0].attributes["site_map"], "regex/site_map")


class ProjectionBlockTests(unittest.TestCase):
    def test_projection_block_supports_include_scopes_and_scope_resources(self) -> None:
        projection = ProjectionBlock(
            name="netbox",
            include_scopes=(
                NodeScope.PHYSICAL_DEVICE,
                NodeScope.PORT,
                NodeScope.VIRTUAL_MACHINE,
                NodeScope.IP_ADDRESS,
            ),
            scopes=(
                ProjectionScope(
                    scope=NodeScope.PHYSICAL_DEVICE,
                    resource="dcim.devices",
                ),
                ProjectionScope(
                    scope=NodeScope.PORT,
                    resource="dcim.interfaces",
                ),
            ),
        )

        self.assertEqual(projection.name, "netbox")
        self.assertEqual(projection.include_scopes[0], NodeScope.PHYSICAL_DEVICE)
        self.assertEqual(projection.scopes[0].resource, "dcim.devices")


class HclDocumentTests(unittest.TestCase):
    def test_hcl_document_groups_sources_policies_and_projections(self) -> None:
        source = SourceBlock(name="vmware", api_type="vmware")
        policy = PolicyBlock(name="campus")
        projection = ProjectionBlock(name="netbox")

        document = HclDocument(
            sources=(source,),
            policies=(policy,),
            projections=(projection,),
        )

        self.assertEqual(document.sources, (source,))
        self.assertEqual(document.policies, (policy,))
        self.assertEqual(document.projections, (projection,))

    def test_hcl_document_defaults_to_empty_sections(self) -> None:
        document = HclDocument()

        self.assertEqual(document.sources, ())
        self.assertEqual(document.policies, ())
        self.assertEqual(document.projections, ())


if __name__ == "__main__":
    unittest.main()
