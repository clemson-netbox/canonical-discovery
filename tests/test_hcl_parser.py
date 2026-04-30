"""Tests for the minimal HCL parser contract."""

from __future__ import annotations

import unittest

from canonical_discovery.config import HclConfigError, parse_hcl_document
from canonical_discovery.core import AuthorityMode, AuthorityTier, Category, NodeScope


class HclParserTests(unittest.TestCase):
    def test_parse_hcl_document_supports_minimal_valid_shape(self) -> None:
        document = parse_hcl_document(
            {
                "source": {
                    "vmware": {
                        "api_type": "vmware",
                        "authority": {
                            "scope": {
                                "physical_device": {
                                    "category": {
                                        "hardware_inventory": {
                                            "tier": "supplemental",
                                            "confidence": 20,
                                            "mode": "fill_if_missing",
                                        }
                                    },
                                    "field": {
                                        "serial": {
                                            "tier": "observe_only",
                                            "mode": "observe_only",
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
                "policy": {
                    "campus-defaults": {
                        "classify": {
                            "location": {
                                "site_map": "regex/site_map",
                            }
                        }
                    }
                },
                "projection": {
                    "netbox": {
                        "include_scopes": ["physical_device", "port"],
                        "scope": {
                            "physical_device": {"resource": "dcim.devices"},
                            "port": {"resource": "dcim.interfaces"},
                        },
                    }
                },
            }
        )

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

    def test_parse_hcl_document_rejects_invalid_scope_name(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "invalid node scope"):
            parse_hcl_document(
                {
                    "source": {
                        "vmware": {
                            "api_type": "vmware",
                            "authority": {"scope": {"not_a_scope": {}}},
                        }
                    }
                }
            )

    def test_parse_hcl_document_rejects_invalid_authority_tier(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "invalid authority tier"):
            parse_hcl_document(
                {
                    "source": {
                        "vmware": {
                            "api_type": "vmware",
                            "authority": {
                                "scope": {
                                    "physical_device": {
                                        "category": {
                                            "hardware_inventory": {
                                                "tier": "wrong",
                                                "mode": "replace",
                                            }
                                        }
                                    }
                                }
                            },
                        }
                    }
                }
            )

    def test_parse_hcl_document_rejects_non_numeric_confidence(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "confidence must be a number"):
            parse_hcl_document(
                {
                    "source": {
                        "vmware": {
                            "api_type": "vmware",
                            "authority": {
                                "scope": {
                                    "physical_device": {
                                        "category": {
                                            "hardware_inventory": {
                                                "tier": "supplemental",
                                                "confidence": "high",
                                                "mode": "replace",
                                            }
                                        }
                                    }
                                }
                            },
                        }
                    }
                }
            )

    def test_parse_hcl_document_rejects_non_list_sections(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "source blocks must be a mapping"):
            parse_hcl_document({"source": []})

    def test_parse_hcl_document_rejects_empty_block_name(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "source block names must be non-empty strings"):
            parse_hcl_document({"source": {"": {"api_type": "vmware"}}})

    def test_parse_hcl_document_rejects_non_mapping_document(self) -> None:
        with self.assertRaisesRegex(HclConfigError, "HCL document input must be a mapping"):
            parse_hcl_document([])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
