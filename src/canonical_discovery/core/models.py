"""Core dataclass models for canonical graph artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from canonical_discovery.core.enums import (
    AuthorityMode,
    AuthorityTier,
    Category,
    EdgeType,
    NodeScope,
)


@dataclass(frozen=True, slots=True)
class Node:
    """Canonical graph node."""

    key: str
    scope: NodeScope


@dataclass(frozen=True, slots=True)
class Edge:
    """Canonical graph edge."""

    key: str
    edge_type: EdgeType
    source_key: str
    target_key: str


@dataclass(frozen=True, slots=True)
class NodeClaim:
    """Source-contributed assertion about a canonical node field."""

    node_key: str
    scope: NodeScope
    category: Category
    field_name: str
    value: Any
    source_name: str
    provenance: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None
    authority_tier: AuthorityTier = AuthorityTier.SUPPLEMENTAL
    confidence: float = 0.0
    mode: AuthorityMode = AuthorityMode.REPLACE


@dataclass(frozen=True, slots=True)
class EdgeClaim:
    """Source-contributed assertion about a canonical edge field."""

    edge_key: str
    edge_type: EdgeType
    category: Category
    field_name: str
    value: Any
    source_name: str
    provenance: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None
    authority_tier: AuthorityTier = AuthorityTier.SUPPLEMENTAL
    confidence: float = 0.0
    mode: AuthorityMode = AuthorityMode.REPLACE


type Claim = NodeClaim | EdgeClaim


@dataclass(frozen=True, slots=True)
class GraphArtifact:
    """Canonical graph artifact emitted by adapters or carried through ingest."""

    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()
    claims: tuple[Claim, ...] = ()
