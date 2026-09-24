---
name: component-design
description: "Use for actionable CREATE work requiring implementation-facing component, class/interface, port and dependency design after application/data/interface/stack constraints are accepted. Produce code-design boundaries without implementing code or inventing upstream semantics."
---

# Component Design

## Trigger

Use when actionable CREATE work has `knowledge_kind: component-design`.

## Inputs

- actionable Component Design capability;
- accepted architecture, application, data, machine-interface and human-interface design as applicable;\n- accepted concurrency/consistency design when component correctness depends on interacting executions;
- accepted implementation stack where technology affects boundary design;
- accepted project Engineering Policy/design constraints when present;
- existing code only as evidence of current realization, never as authority over accepted design.

## Read boundary

Read the accepted upstream architecture/application/interface/data/policy knowledge required by the selected component scope plus existing code structure needed to avoid contradicting already-realized contracts. Existing code is evidence of current representation, not authority to redefine accepted semantics.

## Procedure

1. Confirm upstream capabilities are accepted and identify all project-owned engineering-policy obligations.
2. Trace each implementation-facing use case through required collaborators.
3. Inventory public components by architecture/module boundary.
4. Give each public component one coherent responsibility/change reason.
5. Define narrow ports/interfaces only where an accepted boundary, external technology, substitution need or known variation requires a seam.
6. Shape ports from the consuming use case: expose only operations that consumer needs. A single concrete provider may satisfy several narrow consumer-owned contracts; do not introduce wrappers merely to obtain one runtime object per port.
8. Specify responsibility, ownership, dependency and behavioral/failure contracts before choosing language representation. Preserve an existing simple callable/value representation when it satisfies the contract; require a class only when construction, lifetime, state or substitutability makes that representation semantically relevant.
8. State which side owns every abstraction and ensure dependency direction satisfies accepted architecture/policy.
9. Define important input/output value types and failure semantics without leaking framework/infrastructure types inward.
10. Define representation/mapping boundaries and composition/construction relationships.
11. Apply applicable project principles (for example SRP/DIP/ISP/KISS/YAGNI/LoD) as concrete obligations, not acronym claims.
12. Identify forbidden dependencies and structural verification that can enforce them.
13. Explicitly list implementation freedoms left to coding so the artifact does not prescribe private helpers or line-by-line algorithms.
14. If decomposition requires a new product/domain/application/architecture decision, create/route a Question to its owning Authority.
15. Produce project-native Component Design, semantically accept/register, then reevaluate.

## Frontend presentation-provider specialization

When accepted frontend Screen/View Design selects provider-neutral presentation patterns and the implementation stack selects a concrete UI provider:

1. keep Screen/View semantics as the authority for data, actions, states, navigation and allowed/excluded capabilities;
2. define only the smallest provider adapter seam required to realize those accepted patterns;
3. pin the provider major/version or immutable baseline used for realization;
4. make optional provider/template features deny-by-default;
5. map each required presentation pattern to a project adapter and concrete provider primitives;
6. keep vendor theme, component props and template composition inside the provider implementation;
7. do not reproduce the vendor component API behind project wrappers;
8. verify that replacing the provider changes adapters/theme/rendered evidence, not product semantics or HTTP contracts.

A copied vendor template is implementation source/reference, not product authority. If the template exposes a search, sort, pagination, destructive action, route or field absent from accepted Screen/View semantics, the adapter omits/disables it.

When the accepted Presentation System defines the default entity catalogue drill-down, do not remove its table/query/detail behavior merely because the current HTTP/query contract is weaker. Route the missing search/filter/sort/paging semantics as an upstream Interface/Application question or implementation prerequisite. Provider capability never authorizes those semantics by itself, but a missing backend/query contract also does not silently cancel an accepted presentation default.

## Applicability discipline

Do not introduce a pattern merely because it is common.

Examples:

- CQRS requires a real accepted reason to separate command/query models or infrastructure.
- generic repositories are not a default abstraction; prefer use-case/consumer-shaped contracts when persistence needs differ;
- event bus/mediator/DI frameworks require a current need;
- REST/HATEOAS rules do not apply to non-REST interfaces;
- inheritance requires substitutability, otherwise prefer composition;
- OCP does not justify speculative extension points.

Project Engineering Policy is authoritative when it selects or rejects these patterns.

## Stop conditions

Stop and route a Question when:

- two accepted upstream contracts require incompatible component responsibilities;
- a public port cannot be specified without inventing domain/application semantics;
- required dependency direction conflicts with an accepted architecture decision;
- a technology constraint makes an accepted contract unrealizable.

## Output contract

A useful Component Design normally includes:

- component inventory grouped by module/layer;
- responsibility of each public component;
- public ports/interfaces and important value contracts;
- abstraction ownership;
- dependency graph/direction;
- composition/construction rules;
- representation/mapping boundaries;
- use-case collaboration trace;
- forbidden dependencies;
- structural verification obligations;
- intentionally unconstrained implementation details.

A class diagram is optional. Classes are not mandatory when a function/value module better satisfies the accepted responsibility. Likewise, do not mandate a language-specific interface construct: Protocols, interfaces, small Go interfaces, function contracts or equivalent forms may realize the same semantic boundary.

## Acceptance checks

- coding can begin without choosing major structural dependencies;
- every public component has a justified responsibility;
- every abstraction has a current reason to exist;
- source dependencies obey accepted architecture/policy;
- infrastructure/framework types do not leak into inner contracts;
- cross-context dependencies use provider-owned contracts;
- no speculative abstraction is introduced for hypothetical future requirements;
- artifact leaves private implementation details free;
- unresolved semantic gaps are Questions rather than hidden code-design choices.

## Registration

Register the accepted project-native artifact under Component Design and provide the requested component-design capability. Dependencies include the canonical engineering policy and upstream design actually consumed.


## Human projection

Prefer a project-native component design document or structured design artifact that is directly reviewable by implementation agents and humans.
