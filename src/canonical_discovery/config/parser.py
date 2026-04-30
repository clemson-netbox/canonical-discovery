"""Minimal parser contract for the typed HCL configuration models."""

from __future__ import annotations

from io import StringIO
from typing import Any

import hcl2

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


def parse_hcl_text(text: str) -> HclDocument:
    """Parse raw HCL text using python-hcl2 and map it to typed contracts."""

    if text == "":
        raise HclConfigError("HCL text input must be non-empty")

    try:
        loaded = hcl2.load(StringIO(text))
    except Exception as exc:  # pragma: no cover
        raise HclConfigError(f"failed to parse HCL text: {exc}") from exc

    return parse_hcl_document(loaded)


def parse_hcl_document(data: dict[str, Any]) -> HclDocument:
    """Parse python-hcl2 output into typed configuration contracts."""

    if not isinstance(data, dict):
        raise HclConfigError("HCL document input must be a mapping")

    return HclDocument(
        sources=tuple(
            parse_source_block(name, body) for name, body in require_labeled_blocks(data, "source")
        ),
        policies=tuple(
            parse_policy_block(name, body) for name, body in require_labeled_blocks(data, "policy")
        ),
        projections=tuple(
            parse_projection_block(name, body)
            for name, body in require_labeled_blocks(data, "projection")
        ),
    )


def parse_source_block(name: str, data: Any) -> SourceBlock:
    block = require_mapping(data, "source block")
    authority_value = block.get("authority")
    return SourceBlock(
        name=name,
        api_type=require_string(block, "api_type"),
        authority=parse_authority_block(authority_value) if authority_value is not None else None,
        options={
            key: value for key, value in block.items() if key not in {"api_type", "authority"}
        },
    )


def parse_authority_block(data: Any) -> AuthorityBlock:
    blocks = require_block_list(data, "authority block")
    scopes: list[AuthorityScope] = []

    for block in blocks:
        scopes.extend(
            parse_authority_scope(name, body)
            for name, body in require_labeled_blocks(block, "scope")
        )

    return AuthorityBlock(scopes=tuple(scopes))


def parse_authority_scope(name: str, data: Any) -> AuthorityScope:
    block = require_mapping(data, "authority scope")
    return AuthorityScope(
        scope=parse_node_scope(name),
        categories=tuple(
            parse_authority_category(category_name, category_body)
            for category_name, category_body in require_labeled_blocks(block, "category")
        ),
        fields=tuple(
            parse_authority_field(field_name, field_body)
            for field_name, field_body in require_labeled_blocks(block, "field")
        ),
    )


def parse_authority_category(name: str, data: Any) -> AuthorityCategory:
    block = require_mapping(data, "authority category")
    return AuthorityCategory(
        category=parse_category(name),
        rule=parse_authority_rule(block),
    )


def parse_authority_field(name: str, data: Any) -> AuthorityField:
    block = require_mapping(data, "authority field")
    return AuthorityField(
        name=name,
        rule=parse_authority_rule(block),
    )


def parse_authority_rule(data: Any) -> AuthorityRule:
    block = require_mapping(data, "authority rule")
    return AuthorityRule(
        tier=parse_authority_tier(require_string(block, "tier")),
        mode=parse_authority_mode(require_string(block, "mode")),
        confidence=parse_optional_number(block.get("confidence"), "confidence"),
    )


def parse_policy_block(name: str, data: Any) -> PolicyBlock:
    block = require_mapping(data, "policy block")
    return PolicyBlock(
        name=name,
        classifications=tuple(
            parse_policy_classify(target, classify_body)
            for target, classify_body in require_labeled_blocks(block, "classify")
        ),
    )


def parse_policy_classify(name: str, data: Any) -> PolicyClassify:
    block = require_mapping(data, "policy classify")
    return PolicyClassify(
        target=parse_node_scope(name),
        attributes=dict(block),
    )


def parse_projection_block(name: str, data: Any) -> ProjectionBlock:
    block = require_mapping(data, "projection block")
    return ProjectionBlock(
        name=name,
        include_scopes=tuple(
            parse_node_scope(value)
            for value in require_string_list(block.get("include_scopes", []), "include_scopes")
        ),
        scopes=tuple(
            parse_projection_scope(scope_name, scope_body)
            for scope_name, scope_body in require_labeled_blocks(block, "scope")
        ),
    )


def parse_projection_scope(name: str, data: Any) -> ProjectionScope:
    block = require_mapping(data, "projection scope")
    return ProjectionScope(
        scope=parse_node_scope(name),
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


def require_block_list(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise HclConfigError(f"{label} must be a list")
    return [require_mapping(item, label) for item in value]


def require_labeled_blocks(mapping: dict[str, Any], key: str) -> list[tuple[str, Any]]:
    value = mapping.get(key, [])
    if not isinstance(value, list):
        raise HclConfigError(f"{key} blocks must be a list")

    parsed: list[tuple[str, Any]] = []
    for item in value:
        block = require_mapping(item, f"{key} block")
        if len(block) != 1:
            raise HclConfigError(f"{key} blocks must contain exactly one labeled entry")
        name, body = next(iter(block.items()))
        if not isinstance(name, str) or name == "":
            raise HclConfigError(f"{key} block names must be non-empty strings")
        parsed.append((name, body))
    return parsed


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
