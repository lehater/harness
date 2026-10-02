# Model Completeness Ownership v0

Status: canonical.

## Purpose

Define one owner for each meaning involved in project-model completeness without
promoting the Reference Engineering Model into project truth or adding a new Core
entity.

This contract answers three different questions that must not be collapsed:

1. **What engineering topology has this project accepted?**
2. **Is the selected Consumer/scope sufficiently covered?**
3. **Which reusable templates could help realize missing knowledge?**

## Ownership

### Project Model

The Project Model owns the concrete accepted Engineering Graph for the project:
Authority instances, CapabilityIds, production prerequisites and Consumers.

The graph may be declared directly or projected from project-native truth. A
proposal emitted by another context does not become project truth until the
project-owned integration/acceptance boundary adopts it.

Project Model structural `COMPLETE` means only that every declared expectation
in the selected graph has an unblocked provider. It is not a proof that the graph
contains every concern or subject obligation that should exist.

### Engineering Coverage

Engineering Coverage is the sole Harness owner of the selected-scope
completeness/applicability verdict.

Coverage owns:

- Concern activation and applicability;
- subject/scope obligations;
- proof requirements and coverage states;
- `completion_ready` for the selected Consumer/scope.

Silence is never positive completeness evidence. A concern may be
`NOT_APPLICABLE` only through the accepted applicability/coverage contract, not
because the Project Model or Reference Model omitted it.

Coverage may expose missing work or obligations, but it does not mutate or
replace the accepted Engineering Graph.

A `harness-production-contract-overlay` is therefore a planning aid only. It may
describe a candidate production contract so Coverage can route the missing work,
but an overlay-only Capability cannot count as an accepted provider or satisfy a
Coverage proof. Even if the Core realization already contains a matching
`provides` entry, that entry remains non-authoritative until the project-owned
Engineering Graph adopts the Capability.

### Reference Engineering Model

The Reference Engineering Model is a supporting mapping from accepted project
facts/concerns to reusable Authority/Capability templates and materialization
proposals.

Reference materialization may propose a candidate Engineering Graph or additions
to one. It does not:

- own the project's accepted Engineering Graph;
- prove selected-scope completeness;
- turn an absent template into `NOT_APPLICABLE`;
- make a proposal canonical merely because materialization is internally stable.

The current Reference Engineering Model remains a research surface. This
ownership contract is independent of whether that research surface is later
promoted.

### Application Layer

The Application Layer may coordinate the loop between these contexts, but owns
none of their durable truth.

## Canonical loop

```text
accepted Project Model
        ↓
Engineering Coverage
        ↓
missing concern / subject / proof obligation?
        │
       yes
        ↓
Application coordination
        ↓
optional Reference Model materialization
        ↓
project-owned proposal review / graph change
        ↓
accepted Project Model
        ↓
Engineering Coverage re-evaluation
```

A Reference Model proposal can therefore help close a Coverage gap, but it cannot
close the gap by itself.

## Fail-closed rules

1. Structural Project Model `COMPLETE` and Reference materialization `STABLE`
   are insufficient to claim full design/documentation closure.
2. Full closure requires Engineering Coverage for the same selected
   Consumer/scope to report `completion_ready=true` with terminal
   applicability/subject obligations.
3. Missing Reference Model knowledge is a limitation of reusable
   materialization, not evidence that a project concern is absent.
4. A Coverage gap is a completeness finding, not permission for Coverage to
   invent project Authorities, CapabilityIds or prerequisites.
5. A project-specific graph element may exist without a Reference Model template;
   the Project Model remains authoritative after project-owned acceptance.
6. A reusable Reference Model template may exist without being applicable to a
   project; Coverage/project applicability evidence decides whether the concern
   is required.

## Non-goals

This contract does not:

- promote the current Reference Engineering Model from research;
- require every project to use Reference materialization;
- create a universal concern ontology inside Project Model;
- add completeness state to Core;
- make Application orchestration a new source of engineering truth.
