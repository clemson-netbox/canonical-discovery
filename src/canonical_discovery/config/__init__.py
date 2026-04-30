"""Configuration contracts for canonical-discovery."""

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
from canonical_discovery.config.parser import HclConfigError, parse_hcl_document

__all__ = [
    "AuthorityBlock",
    "AuthorityCategory",
    "AuthorityField",
    "AuthorityRule",
    "AuthorityScope",
    "HclConfigError",
    "HclDocument",
    "parse_hcl_document",
    "PolicyBlock",
    "PolicyClassify",
    "ProjectionBlock",
    "ProjectionScope",
    "SourceBlock",
]
