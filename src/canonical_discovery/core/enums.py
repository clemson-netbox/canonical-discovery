"""Core enum definitions fixed by the architecture RFCs."""

from enum import StrEnum


class NodeScope(StrEnum):
    """Canonical node scopes defined by RFC 0001."""

    PHYSICAL_DEVICE = "physical_device"
    DEVICE_COMPONENT = "device_component"
    PORT = "port"
    LINK = "link"
    IP_ADDRESS = "ip_address"
    NETWORK_SEGMENT = "network_segment"
    VIRTUAL_MACHINE = "virtual_machine"
    OS_INSTANCE = "os_instance"
    LOCATION = "location"


class EdgeType(StrEnum):
    """Canonical edge types defined by RFC 0001."""

    CONTAINS = "contains"
    HOSTS = "hosts"
    CONNECTED_TO = "connected_to"
    MEMBER_OF = "member_of"
    ASSIGNED_TO = "assigned_to"
    LOCATED_IN = "located_in"
    BACKS = "backs"
    OBSERVED_BY = "observed_by"


class Category(StrEnum):
    """Canonical categories used for authority policy in RFC 0001."""

    IDENTITY = "identity"
    HARDWARE_INVENTORY = "hardware_inventory"
    MODULE_INVENTORY = "module_inventory"
    VIRTUALIZATION = "virtualization"
    OPERATING_SYSTEM = "operating_system"
    NETWORK_L1_L2 = "network_l1_l2"
    NETWORK_L3 = "network_l3"
    TOPOLOGY = "topology"
    PLACEMENT = "placement"
    OWNERSHIP_CONTEXT = "ownership_context"
    TELEMETRY = "telemetry"


class AuthorityTier(StrEnum):
    """Authority tiers defined by RFC 0001."""

    AUTHORITATIVE = "authoritative"
    PREFERRED = "preferred"
    SUPPLEMENTAL = "supplemental"
    OBSERVE_ONLY = "observe_only"


class AuthorityMode(StrEnum):
    """Authority modes defined by RFC 0001."""

    REPLACE = "replace"
    FILL_IF_MISSING = "fill_if_missing"
    MERGE = "merge"
    OBSERVE_ONLY = "observe_only"
