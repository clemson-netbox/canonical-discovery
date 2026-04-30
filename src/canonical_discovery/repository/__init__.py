"""Repository abstractions and implementations."""

from canonical_discovery.repository.control_plane import ControlPlaneRepository
from canonical_discovery.repository.sqlite_control_plane import SQLiteControlPlaneRepository

__all__ = ["ControlPlaneRepository", "SQLiteControlPlaneRepository"]
