# RFC 0001: Canonical Graph, Layered Enrichment, Authority Resolution, and HCL Role for 2.0

## 1. Abstract

This RFC defines the core architecture for `2.0` as a clean-slate rewrite.

`2.0` is built around a projection-neutral, graph-first canonical model.
Source adapters assemble raw source observations internally, then emit shared
canonical nodes, edges, and claims directly. Multiple sources may contribute
claims to the same canonical objects. Authority is resolved declaratively
through source HCL, not hardcoded in adapter code. Projections such as NetBox,
Nautobot, ServiceNow, and artifact export consume resolved canonical truth
downstream.

This RFC also narrows and clarifies the role of HCL in `2.0`. Unlike `1.x`,
HCL is not the primary language for core normalization or target write
orchestration. In `2.0`, HCL is primarily a declarative surface for source
participation, authority policy, deployment policy, and projection
configuration.

## 2. Motivation

`1.x` proved several important things:

- multi-source discovery and synchronization are useful
- reusable collectors are preferable to source-specific scripts
- thin adapters plus shared logic is the right direction
- declarative configuration has value

However, `1.x` did not fully realize the intended architecture.

Observed architectural problems include:

- source adapters accumulated normalization and precedence logic
- the engine accumulated source-specific behavior
- the internal model drifted toward a NetBox-shaped object model
- enrichment happened in multiple incompatible forms
- HCL often acted as a target-mapping language rather than a clean policy layer
- multi-source truth resolution was implicit rather than explicit

`2.0` should treat `1.x` as a proof of concept, not as a structure to
preserve.

## 3. Goals

The goals of `2.0` are:

- thin source adapters
- direct emission of shared canonical graph data from adapters
- explicit layered enrichment
- explicit, source-configured authority resolution
- a projection-neutral internal model
- support for multiple downstream targets
- HCL retained as a mostly declarative configuration surface
- strong separation between core sync logic and control-plane/runtime concerns

## 4. Non-Goals

This RFC does not attempt to:

- preserve `1.x` HCL semantics
- preserve `1.x` engine structure
- define UI, scheduler, or job persistence architecture
- define every target projection in detail
- create a large per-field rules DSL
- introduce probabilistic or ML-based truth resolution
- define freshness-based scoring for `v0`
- define manual target-side override behavior for `v0`

## 5. Definitions

### 5.1 Observation

A raw or lightly normalized fact fetched from a source system.

### 5.2 Source-local assembly

Private adapter logic that combines fragmented observations from the same
source into a coherent internal view before canonical emission.

### 5.3 Canonical graph

The shared projection-neutral representation of discovered infrastructure,
modeled as typed nodes and typed edges.

### 5.4 Claim

A source-contributed assertion about a field or relationship on a canonical
object.

### 5.5 Resolved truth

The winning canonical value after authority rules have been applied across
competing claims.

### 5.6 Projection

A downstream target-specific rendering of resolved canonical truth, such as
NetBox, Nautobot, ServiceNow, or JSON artifact output.

## 6. Design Principles

1. Adapters may perform source-local assembly, but they must emit shared
   canonical graph data directly.
2. Adapters do not hardcode source precedence or target-specific truth rules.
3. Canonical truth is resolved before projection.
4. HCL declares authority and policy; it does not own core normalization logic.
5. The canonical model must not be shaped around a single target system.
6. Cross-source enrichment operates on canonical graph data only.
7. Losing claims are preserved as provenance.

## 7. Canonical Graph Model

### 7.1 Graph-first model

The canonical model in `2.0` is graph-first. Every source adapter emits:

- canonical nodes
- canonical edges
- claims against nodes and edges

The graph is strongly typed at the domain level. It is not a generic untyped
property graph.

### 7.2 Canonical node scopes

The following node scopes are defined for `v0`:

- `physical_device`
- `device_component`
- `port`
- `link`
- `ip_address`
- `network_segment`
- `virtual_machine`
- `os_instance`
- `location`

### 7.3 Node scope intent

#### `physical_device`

Represents a tangible infrastructure device such as a server, switch, router,
firewall, appliance, or chassis.

Belongs here:

- stable identity
- hardware inventory
- virtualization host context
- placement context
- ownership context

Does not belong here:

- guest OS runtime facts
- explicit port-to-port topology edges
- per-component inventory details that should live on `device_component`

#### `device_component`

Represents a hardware component attached to a physical device or another
component.

Examples:

- line card
- PSU
- DIMM
- transceiver
- blade
- module

#### `port`

Represents a physical or logical attachment point for network or host
connectivity.

Examples:

- Ethernet interface
- VMkernel NIC
- virtual NIC
- port-channel
- management port

#### `link`

Represents a relationship between ports or equivalent connectivity endpoints.

A `link` is modeled as its own scope so topology claims are not forced into
port-local fields.

#### `ip_address`

Represents an addressable L3 endpoint or assigned address object.

#### `network_segment`

Represents shared network constructs such as VLANs, prefixes, VRFs, subnets,
or equivalent segment abstractions.

#### `virtual_machine`

Represents a VM as a distinct managed object.

#### `os_instance`

Represents guest or runtime operating-system-level truth for either a physical
or virtual compute object.

This is separate from `physical_device` and `virtual_machine` so OS/runtime
truth does not overwrite hardware or hypervisor truth.

#### `location`

Represents site/building/room/rack or equivalent placement structures.

### 7.4 Edge types

The following relationship types are defined conceptually for `v0`:

- `contains`
- `hosts`
- `connected_to`
- `member_of`
- `assigned_to`
- `located_in`
- `backs`
- `observed_by`

These names are illustrative but should remain finite and typed in core code.

### 7.5 Graph invariants

The canonical graph should enforce these initial invariants:

- `os_instance` attaches to exactly one hosting compute object
- `link` connects ports or equivalent endpoints, not devices directly
- `device_component` attaches to a `physical_device` or another
  `device_component`
- `ip_address` is attached by explicit relationship, not implied nested fields
- `virtual_machine` is not a subtype of `physical_device`
- topology relationships are represented as graph edges or `link` nodes, not
  embedded target-specific fields

## 8. Canonical Categories

The following categories are defined centrally and used for authority policy:

- `identity`
- `hardware_inventory`
- `module_inventory`
- `virtualization`
- `operating_system`
- `network_l1_l2`
- `network_l3`
- `topology`
- `placement`
- `ownership_context`
- `telemetry`

These categories are fixed by core code/docs. Sources map themselves into these
categories via HCL.

## 9. Claim Model

### 9.1 Claims as first-class objects

Each source emits claims against canonical nodes and edges.

A claim conceptually includes:

- canonical object key
- scope
- category
- field
- value
- source name
- provenance metadata
- timestamp
- authority tier
- confidence
- mode

### 9.2 Claims on edges

Claims may target:

- node fields
- edge fields
- link-like relationship objects

This is required because topology, membership, and assignment truth may also be
disputed across sources.

### 9.3 Provenance

Every claim should preserve enough provenance to explain:

- where the fact came from
- what raw observation or adapter context produced it
- why it won or lost during resolution

## 10. Layered Enrichment Model

### 10.1 Overview

Enrichment in `2.0` is staged. Different concerns are allowed in different
layers.

The stages are:

1. observation
2. source-local assembly
3. canonical graph emission
4. cross-source enrichment
5. authority resolution
6. deployment policy
7. projection planning
8. projection execution

### 10.2 Observation layer

Purpose:

- collect raw or lightly normalized source observations

Allowed:

- source auth
- pagination
- endpoint fetches
- basic decoding/cleanup

Not allowed:

- authority resolution
- target-specific behavior
- cross-source merge logic

Output:

- raw observations

### 10.3 Source-local assembly layer

Purpose:

- combine fragmented observations from the same source into a coherent
  source-local internal view

Examples:

- CatC inventory + membership + interface rows
- VMware host + pNIC + vNIC + tags
- Prometheus uname + dmi + metrics for one node

Allowed:

- source-local merge/reconciliation
- source-local diagnostics
- source-local identity stitching

Not allowed:

- cross-source precedence
- target projection behavior
- exposure of a source-private schema to the rest of the system

Important:

- a source may use an internal registry-like structure here
- that structure is private implementation detail
- it is not part of the public 2.0 architecture

Output:

- canonical graph nodes, edges, and claims

### 10.4 Canonical graph emission layer

Purpose:

- define the adapter's public output contract

Adapters must emit:

- canonical nodes
- canonical edges
- claims

Adapters must not emit:

- NetBox-shaped payloads
- ServiceNow-shaped records
- target prerequisites
- target FK lookup instructions

### 10.5 Cross-source enrichment layer

Purpose:

- allow multiple sources to contribute facts to the same canonical graph

Examples:

- `xclarity` + `vmware` on a physical host
- `vmware` + `salt` on a VM
- `nexus` + `catc` on ports and topology

Rules:

- only canonical graph data is visible here
- source-private assembly state is not visible here
- cross-source enrichment does not redefine canonical scope/category semantics

### 10.6 Authority resolution layer

Purpose:

- resolve competing claims into canonical truth

Authority resolution uses:

- HCL-declared policy
- deterministic ranking
- limited merge semantics

### 10.7 Deployment policy layer

Purpose:

- apply environment-specific interpretation rules

Examples:

- site mapping
- naming normalization
- local classification
- ownership derivation
- suppression/filtering

Rules:

- may shape interpretation
- may not redefine core canonical model
- may not introduce target-specific write mechanics

### 10.8 Projection planning layer

Purpose:

- translate resolved canonical graph truth into target-specific operations

Rules:

- projection planning consumes resolved truth
- projection planning may decide target-specific compression or lossy mapping
- projection planning may not resolve source truth conflicts

### 10.9 Projection execution layer

Purpose:

- perform actual target API writes or artifact output

Rules:

- execution owns retries, batching, idempotency, error reporting
- execution does not own domain truth

## 11. Authority Model

### 11.1 Authority declared in HCL

Authority policy is defined in source HCL for consistency and visibility.

Authority is primarily expressed by:

- `scope`
- `category`

Field overrides are permitted sparingly for exceptions.

### 11.2 Tiers

The initial tiers are:

- `authoritative`
- `preferred`
- `supplemental`
- `observe_only`

### 11.3 Modes

The initial modes are:

- `replace`
- `fill_if_missing`
- `merge`
- `observe_only`

### 11.4 Confidence

Each rule may declare `confidence` as a numeric weight within the chosen tier.

This keeps the model simple:

- broad categories
- deterministic ranking
- no complex matrix required for most cases

### 11.5 Resolution order

For a given field:

1. rank by tier
2. rank by confidence
3. apply stable fallback such as source name

Freshness is not used in `v0`.

### 11.6 Mode semantics

- `replace`
  - winning claim becomes canonical truth
- `fill_if_missing`
  - claim populates only unresolved values
- `merge`
  - combine values where field type supports it
- `observe_only`
  - retain provenance only; never becomes canonical truth

### 11.7 Field overrides

Field overrides are allowed only for exceptional cases such as:

- `serial`
- `mtu`
- `primary_ip`
- `hostname`

The model should remain category-first by default.

## 12. HCL Role in 2.0

### 12.1 HCL remains, but with a different job

HCL remains the preferred declarative config surface in `2.0`.

However, its role changes substantially from `1.x`.

### 12.2 What HCL owns in 2.0

HCL should own:

- source wiring
- source options
- authority policy
- deployment policy
- filtering
- classification
- projection configuration
- projection field selection/preferences where appropriate

### 12.3 What HCL does not own in 2.0

HCL should not own:

- source-local assembly logic
- canonical normalization logic
- cross-source merge algorithms
- target write execution behavior
- dependency execution mechanics

### 12.4 HCL should be mostly declarative

`2.0` HCL should be mostly declarative.

Expression logic should be minimized because:

- source-local logic should already have happened in the adapter
- adapters emit shared canonical graph data directly
- HCL should configure policy, not act as a transformation engine

## 13. How 2.0 HCL Differs From 1.x

### 13.1 1.x HCL

`1.x` HCL primarily described:

- direct source-to-NetBox mappings
- nested target object handling
- prerequisites
- field transforms
- target-specific payload shape

Conceptually:

```text
source object -> HCL transforms -> target payload -> target write
```

### 13.2 2.0 HCL

`2.0` HCL should primarily describe:

- which sources participate
- what authority they have
- how deployment policy applies
- how canonical graph truth should be projected

Conceptually:

```text
adapter emits canonical graph -> HCL declares authority/policy/projection -> projector consumes resolved truth
```

### 13.3 Illustrative 1.x style

```hcl
object "device" {
  netbox_resource = "dcim.devices"

  field "name" {
    value = "source('hostname')"
  }

  prerequisite "site" {
    method = "ensure_site"
    args = { name = "source('site_name')" }
  }

  interface {
    source_items = "interfaces"
  }
}
```

### 13.4 Illustrative 2.0 style

```hcl
source "xclarity" {
  api_type = "xclarity"

  authority {
    scope "physical_device" {
      category "hardware_inventory" {
        tier       = "authoritative"
        confidence = 100
        mode       = "replace"
      }
    }
  }
}

policy "campus" {
  classify "location" {
    site_map = "regex/site_map"
  }
}

projection "netbox" {
  include_scopes = [
    "physical_device",
    "port",
    "virtual_machine",
    "ip_address"
  ]
}
```

## 14. Example HCL Shapes

### 14.1 Source authority

```hcl
source "vmware" {
  api_type = "vmware"

  authority {
    scope "virtual_machine" {
      category "identity" {
        tier       = "authoritative"
        confidence = 100
        mode       = "replace"
      }

      category "virtualization" {
        tier       = "authoritative"
        confidence = 100
        mode       = "replace"
      }
    }

    scope "physical_device" {
      category "hardware_inventory" {
        tier       = "supplemental"
        confidence = 20
        mode       = "fill_if_missing"
      }

      field "serial" {
        tier       = "observe_only"
        confidence = 0
        mode       = "observe_only"
      }
    }
  }
}
```

### 14.2 Policy

```hcl
policy "campus-defaults" {
  classify "location" {
    site_map = "regex/site_map"
  }

  classify "physical_device" {
    owner_group_map = "map/platform_owner"
  }
}
```

### 14.3 Projection

```hcl
projection "netbox" {
  scope "physical_device" {
    resource = "dcim.devices"
  }

  scope "port" {
    resource = "dcim.interfaces"
  }

  scope "virtual_machine" {
    resource = "virtualization.virtual_machines"
  }
}
```

## 15. Example End-to-End Walkthroughs

### 15.1 Lenovo physical host: xclarity + vmware + nexus

Observations:

- `xclarity` sees serial, model, modules, manufacturer
- `vmware` sees ESXi host, cluster, host runtime metadata
- `nexus` sees port speed, mtu, and topology

Source-local assembly:

- each adapter internally assembles its observations

Canonical graph:

- node: `physical_device`
- nodes: `device_component`
- nodes: `port`
- nodes/edges: `link`
- claims from all three sources

Authority:

- `xclarity` wins `physical_device.hardware_inventory`
- `xclarity` wins `device_component.module_inventory`
- `vmware` wins `physical_device.virtualization`
- `nexus` wins `port.network_l1_l2`
- `nexus` wins `link.topology`

Projection:

- NetBox may represent device/modules/interfaces/cables
- ServiceNow may represent host CI + component/relationship subset
- JSON artifact may keep the full graph and losing claims

### 15.2 Virtual machine: vmware + salt

Observations:

- `vmware` sees VM identity, allocation, power state
- `salt` sees OS version, packages, IPs, interface facts

Canonical graph:

- node: `virtual_machine`
- node: `os_instance`
- nodes: `ip_address`
- nodes: `port`
- edges linking them

Authority:

- `vmware` wins `virtual_machine.virtualization`
- `salt` wins `os_instance.operating_system`
- `salt` likely wins `ip_address.network_l3`

Projection:

- NetBox may represent VM + interfaces + IPs
- ServiceNow may represent CI + OS details
- artifact export preserves all claims

### 15.3 Network device: catc/nexus + supplemental source

Observations:

- `catc` and/or `nexus` provide device, ports, topology
- supplemental source may provide ownership or OS-level context

Authority:

- network source wins `network_l1_l2` and `topology`
- supplemental source may win `ownership_context` or `operating_system` if
  applicable

## 16. Projection Model

### 16.1 Projection is downstream

Projection targets consume resolved canonical graph truth.

Projection targets do not:

- decide which source wins
- define canonical semantics
- alter source authority policy

### 16.2 Projection may be lossy

Different targets may represent the same canonical truth differently.

Examples:

- NetBox/Nautobot can model ports, VLANs, topology in detail
- ServiceNow may flatten or compress some relationships
- artifact projection may preserve everything

This is acceptable as long as the canonical graph remains richer than any
single projection.

### 16.3 Initial projection pressure set

The canonical model should be designed with at least these targets in mind:

- NetBox
- ServiceNow
- artifact/JSON export

Nautobot is useful, but as a NetBox-family target it is less valuable than
ServiceNow as a pressure test against NetBox-shaped design.

## 17. Migration Philosophy

`2.0` should be treated as a new product line.

Implications:

- no assumption of `1.x` syntax parity
- no assumption of in-place architectural refactor
- no requirement to preserve old target-centric flows

`1.x` remains useful as:

- proof of concept
- test/fixture source
- operational reference
- migration input

But not as the architectural center of `2.0`.

## 18. Initial Constraints for v0

The following constraints are recommended for the initial implementation:

- fixed canonical scopes
- fixed canonical categories
- adapters emit canonical graph directly
- HCL is mostly declarative
- authority is category-first
- field overrides are minimal
- deterministic ranking only
- no freshness-based resolution
- `telemetry` is `observe_only`
- deployment policy may classify and shape, but not redefine canonical
  semantics

## 19. Open Questions

1. Exact node and edge field sets for each canonical scope
2. Final HCL syntax shape for authority, policy, and projection blocks
3. Whether field overrides should ship in `v0` or only after category-first
   rules prove insufficient
4. When manual target-entered values should participate in authority
   resolution
5. How much projection mapping should be HCL-driven versus code-driven

## 20. Recommended Decisions for v0

- strongly typed domain graph
- claims on nodes and edges
- HCL authority config nested by `scope -> category -> optional field`
- confidence optional but supported
- `placement` remains canonical, shaped by policy
- `telemetry` remains `observe_only`
- projections remain code + HCL hybrid rather than pure HCL-defined logic

## 21. Summary

`2.0` should be built around a graph-first canonical core, not a target-shaped
internal model.

Source adapters should:

- fetch
- assemble internally
- emit canonical graph data directly

HCL should:

- configure sources
- declare authority
- express deployment policy
- configure projections

Projections should:

- consume resolved truth
- adapt it to target systems
- never decide truth themselves

This model keeps the original vision intact:

- thin collectors
- shared reusable abstractions
- layered enrichment
- multiple sources strengthening the same objects
- multiple projection targets without a NetBox-shaped core
