"""Minimal HCL contract dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from canonical_discovery.core import AuthorityMode, AuthorityTier, Category, NodeScope


@dataclass(frozen=True, slots=True)
class AuthorityRule:
    tier: AuthorityTier
    confidence: int | float
    mode: AuthorityMode


@dataclass(frozen=True, slots=True)
class AuthorityField:
    name: str
    rule: AuthorityRule


@dataclass(frozen=True, slots=True)
class AuthorityCategory:
    category: Category
    rule: AuthorityRule
    fields: tuple[AuthorityField, ...] = ()


@dataclass(frozen=True, slots=True)
class AuthorityScope:
    scope: NodeScope
    categories: tuple[AuthorityCategory, ...] = ()


@dataclass(frozen=True, slots=True)
class AuthorityBlock:
    scopes: tuple[AuthorityScope, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceBlock:
    name: str
    api_type: str
    authority: AuthorityBlock | None = None
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PolicyClassify:
    target: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PolicyBlock:
    name: str
    classifications: tuple[PolicyClassify, ...] = ()


@dataclass(frozen=True, slots=True)
class ProjectionScope:
    scope: NodeScope
    resource: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectionBlock:
    name: str
    include_scopes: tuple[NodeScope, ...] = ()
    scopes: tuple[ProjectionScope, ...] = ()


@dataclass(frozen=True, slots=True)
class HclDocument:
    sources: tuple[SourceBlock, ...] = ()
    policies: tuple[PolicyBlock, ...] = ()
    projections: tuple[ProjectionBlock, ...] = ()
