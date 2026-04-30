"""Minimal parser contract for the typed HCL configuration models."""

from __future__ import annotations

from typing import Any

from canonical_discovery.config.hcl_models import (
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


class HclConfigError(ValueError):
    """Raised when a minimal HCL document shape is invalid."""


def parse_hcl_document(data: dict[str, Any]) -> HclDocument:
    """Parse a minimal HCL-like mapping into typed configuration contracts."""

    if not isinstance(data, dict):
        raise HclConfigError("HCL document input must be a mapping")

    return HclDocument(
        sources=tuple(parse_source_block(item) for item in require_list(data, "sources")),
        policies=tuple(parse_policy_block(item) for item in require_list(data, "policies")),
        projections=tuple(
            parse_projection_block(item) for item in require_list(data, "projections")
        ),
    )


def parse_source_block(data: Any) -> SourceBlock:
    block = require_mapping(data, "source block")
    return SourceBlock(
        name=require_string(block, "name"),
        api_type=require_string(block, "api_type"),
        authority=parse_authority_block(block["authority"]) if "authority" in block else None,
        options=require_mapping(block.get("options", {}), "source options"),
    )


def parse_authority_block(data: Any) -> AuthorityBlock:
    block = require_mapping(data, "authority block")
    return AuthorityBlock(
        scopes=tuple(parse_authority_scope(item) for item in require_list(block, "scopes")),
    )


def parse_authority_scope(data: Any) -> AuthorityScope:
    block = require_mapping(data, "authority scope")
    return AuthorityScope(
        scope=parse_node_scope(require_string(block, "scope")),
        categories=tuple(
            parse_authority_category(item) for item in require_list(block, "categories")
        ),
        fields=tuple(parse_authority_field(item) for item in require_list(block, "fields")),
    )


def parse_authority_category(data: Any) -> AuthorityCategory:
    block = require_mapping(data, "authority category")
    return AuthorityCategory(
        category=parse_category(require_string(block, "category")),
        rule=parse_authority_rule(block),
    )


def parse_authority_field(data: Any) -> AuthorityField:
    block = require_mapping(data, "authority field")
    return AuthorityField(
        name=require_string(block, "name"),
        rule=parse_authority_rule(block),
    )


def parse_authority_rule(data: Any) -> AuthorityRule:
    block = require_mapping(data, "authority rule")
    return AuthorityRule(
        tier=parse_authority_tier(require_string(block, "tier")),
        mode=parse_authority_mode(require_string(block, "mode")),
        confidence=parse_optional_number(block.get("confidence"), "confidence"),
    )


def parse_policy_block(data: Any) -> PolicyBlock:
    block = require_mapping(data, "policy block")
    return PolicyBlock(
        name=require_string(block, "name"),
        classifications=tuple(
            parse_policy_classify(item) for item in require_list(block, "classifications")
        ),
    )


def parse_policy_classify(data: Any) -> PolicyClassify:
    block = require_mapping(data, "policy classify")
    return PolicyClassify(
        target=parse_node_scope(require_string(block, "target")),
        attributes=require_mapping(block.get("attributes", {}), "policy classify attributes"),
    )


def parse_projection_block(data: Any) -> ProjectionBlock:
    block = require_mapping(data, "projection block")
    return ProjectionBlock(
        name=require_string(block, "name"),
        include_scopes=tuple(
            parse_node_scope(value)
            for value in require_string_list(block.get("include_scopes", []), "include_scopes")
        ),
        scopes=tuple(parse_projection_scope(item) for item in require_list(block, "scopes")),
    )


def parse_projection_scope(data: Any) -> ProjectionScope:
    block = require_mapping(data, "projection scope")
    return ProjectionScope(
        scope=parse_node_scope(require_string(block, "scope")),
        resource=block.get("resource")
        if block.get("resource") is None
        else require_string(block, "resource"),
    )


def parse_node_scope(value: str) -> NodeScope:
    return parse_enum(value, NodeScope, "node scope")


def parse_category(value: str) -> Category:
    return parse_enum(value, Category, "category")


def parse_authority_tier(value: str) -> AuthorityTier:
    return parse_enum(value, AuthorityTier, "authority tier")


def parse_authority_mode(value: str) -> AuthorityMode:
    return parse_enum(value, AuthorityMode, "authority mode")


def parse_enum(value: str, enum_type: type, label: str):
    try:
        return enum_type(value)
    except ValueError as exc:
        raise HclConfigError(f"invalid {label}: '{value}'") from exc


def parse_optional_number(value: Any, label: str) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise HclConfigError(f"{label} must be a number")
    return value


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HclConfigError(f"{label} must be a mapping")
    return value


def require_list(mapping: dict[str, Any], key: str) -> list[Any]:
    value = mapping.get(key, [])
    if not isinstance(value, list):
        raise HclConfigError(f"{key} must be a list")
    return value


def require_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or value == "":
        raise HclConfigError(f"{key} must be a non-empty string")
    return value


def require_string_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list):
        raise HclConfigError(f"{key} must be a list")

    parsed: list[str] = []
    for item in value:
        if not isinstance(item, str) or item == "":
            raise HclConfigError(f"{key} entries must be non-empty strings")
        parsed.append(item)
    return parsed
