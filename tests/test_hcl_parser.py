"""Tests for the minimal HCL parser contract."""

from __future__ import annotations

import unittest
from io import StringIO

import hcl2

from canonical_discovery.config import HclConfigError, parse_hcl_document, parse_hcl_text
from canonical_discovery.core import AuthorityMode, AuthorityTier, Category, NodeScope


class HclParserTests(unittest.TestCase):
    def test_parse_hcl_document_supports_python_hcl2_output_shape(self) -> None:
        loaded = hcl2.load(
            StringIO(
                'source "vmware" {\n'
                '  api_type = "vmware"\n'
                "  authority {\n"
                '    scope "physical_device" {\n'
                '      category "hardware_inventory" {\n'
                '        tier = "supplemental"\n'
                "        confidence = 20\n"
                '        mode = "fill_if_missing"\n'
                "      }\n"
                '      field "serial" {\n'
                '        tier = "observe_only"\n'
                '        mode = "observe_only"\n'
                "      }\n"
                "    }\n"
                "  }\n"
                "}\n"
                'policy "campus-defaults" {\n'
                '  classify "location" {\n'
                '    site_map = "regex/site_map"\n'
                "  }\n"
                "}\n"
                'projection "netbox" {\n'
                '  include_scopes = ["physical_device", "port"]\n'
                '  scope "physical_device" {\n'
                '    resource = "dcim.devices"\n'
                "  }\n"
                '  scope "port" {\n'
                '    resource = "dcim.interfaces"\n'
                "  }\n"
                "}\n"
            )
        )

        document = parse_hcl_document(loaded)

        source = document.sources[0]
        authority_scope = source.authority.scopes[0]  # type: ignore[union-attr]
        authority_category = authority_scope.categories[0]
        authority_field = authority_scope.fields[0]
        policy = document.policies[0]
        projection = document.projections[0]

        self.assertEqual(source.name, "vmware")
        self.assertEqual(source.api_type, "vmware")
        self.assertEqual(authority_scope.scope, NodeScope.PHYSICAL_DEVICE)
        self.assertEqual(authority_category.category, Category.HARDWARE_INVENTORY)
        self.assertEqual(authority_category.rule.tier, AuthorityTier.SUPPLEMENTAL)
        self.assertEqual(authority_category.rule.mode, AuthorityMode.FILL_IF_MISSING)
        self.assertEqual(authority_category.rule.confidence, 20)
        self.assertEqual(authority_field.name, "serial")
        self.assertEqual(authority_field.rule.confidence, None)
        self.assertEqual(policy.classifications[0].target, NodeScope.LOCATION)
        self.assertEqual(policy.classifications[0].attributes["site_map"], "regex/site_map")
        self.assertEqual(projection.include_scopes, (NodeScope.PHYSICAL_DEVICE, NodeScope.PORT))
        self.assertEqual(projection.scopes[1].scope, NodeScope.PORT)

    def test_parse_hcl_text_uses_python_hcl2_backend(self) -> None:
        document = parse_hcl_text(
            'policy "campus-defaults" {\n'
            '  classify "location" {\n'
            '    site_map = "regex/site_map"\n'
            "  }\n"
            "}\n"
        )

        self.assertEqual(
            document.policies[0].classifications[0].attributes["site_map"], "regex/site_map"
        )

    def test_parse_hcl_document_rejects_invalid_scope_name(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "invalid node scope"):
            parse_hcl_document(
                {
                    "source": [
                        {
                            "vmware": {
                                "api_type": "vmware",
                                "authority": [{"scope": [{"not_a_scope": {}}]}],
                            }
                        }
                    ]
                }
            )

    def test_parse_hcl_document_rejects_invalid_authority_tier(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "invalid authority tier"):
            parse_hcl_document(
                {
                    "source": [
                        {
                            "vmware": {
                                "api_type": "vmware",
                                "authority": [
                                    {
                                        "scope": [
                                            {
                                                "physical_device": {
                                                    "category": [
                                                        {
                                                            "hardware_inventory": {
                                                                "tier": "wrong",
                                                                "mode": "replace",
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                ],
                            }
                        }
                    ]
                }
            )

    def test_parse_hcl_document_rejects_non_numeric_confidence(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "confidence must be a number"):
            parse_hcl_document(
                {
                    "source": [
                        {
                            "vmware": {
                                "api_type": "vmware",
                                "authority": [
                                    {
                                        "scope": [
                                            {
                                                "physical_device": {
                                                    "category": [
                                                        {
                                                            "hardware_inventory": {
                                                                "tier": "supplemental",
                                                                "confidence": "high",
                                                                "mode": "replace",
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                ],
                            }
                        }
                    ]
                }
            )

    def test_parse_hcl_document_rejects_non_list_sections(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "source blocks must be a list"):
            parse_hcl_document({"source": {}})

    def test_parse_hcl_document_rejects_empty_block_name(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "source block names must be non-empty strings"):
            parse_hcl_document({"source": [{"": {"api_type": "vmware"}}]})

    def test_parse_hcl_text_rejects_empty_text(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "HCL text input must be non-empty"):
            parse_hcl_text("")


if __name__ == "__main__":
    unittest.main()
