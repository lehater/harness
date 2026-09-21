# Research — Consumer, Scope and Subject Coverage Semantics

Status: research only. No main/canonical changes.

## Three independent dimensions

Engineering Coverage now distinguishes three boundaries:

~~~text
project
  -> consumer
       -> selected scope roots
            -> subject-scoped concern instances
~~~

### Consumer

The Consumer defines the maximum recursive engineering closure relevant to one terminal target.

Examples:
- backend implementation;
- frontend implementation;
- BLS production import.

### Scope

A named scope such as `mvp` or `later` may select one or more capability roots inside the Consumer closure.

Only those roots and their recursive prerequisites are visible to activation and proof.

~~~yaml
consumer: IMPLEMENTATION
scope: mvp
scope_roots:
  - project.mvp.implementation-design
~~~

A scope root outside the selected Consumer closure is invalid.

This means one Consumer can contain several future delivery slices without making all of them simultaneous completion obligations.

### Subject

Some concerns need independent proof for several semantic subjects.

Example:

~~~yaml
- capability: project.domain.bc-a
  semantic_claims:
    - claim: engineering.domain.model
      subject: BC-A

- capability: project.domain.bc-b
  semantic_claims:
    - claim: engineering.domain.model
      subject: BC-B
~~~

If `domain.model` is activated and both productions are in scope, Coverage requires both instances.

One realized artifact produces:

~~~text
domain.model
  BC-A  COVERED
  BC-B  MISSING
aggregate: MISSING
~~~

Only when all required subject instances are realized may the concern become COVERED.

Subjectless claims keep the previous semantics: any accepted proof claim may satisfy the concern.

## Explicit facts and applicability

Project facts and applicability decisions can now be constrained by both Consumer and named scope:

~~~yaml
- concern: quality.performance.latency
  consumers: [FRONTEND-IMPLEMENTATION]
  scopes: [mvp]
  rationale: Interactive MVP journey requires latency consideration.
~~~

This prevents later-scope or frontend-only facts from contaminating another completion gate.

## Validated scenarios

### One project, multiple Consumers

- backend sees persistence concerns but not frontend accessibility/security;
- frontend sees accessibility/security but not backend-only persistence;
- proof cannot leak between the two closures.

### One Consumer, multiple scopes

A single IMPLEMENTATION Consumer eventually requires an MVP data slice and a later UI slice.

- `scope_roots: [mvp implementation]` activates persistence, not later UI;
- `scope_roots: [later implementation]` activates UI, not MVP persistence;
- proofs from the other slice are invisible;
- a scope root outside the Consumer closure is rejected.

### Multiple subjects

A single Consumer requires domain-model capabilities for BC-A and BC-B.

- BC-A artifact alone does not close `domain.model`;
- Coverage reports BC-A covered and BC-B missing;
- both artifacts are required for aggregate COVERED.

## Target Coverage identity

The effective Coverage identity is therefore:

~~~text
Coverage(project, consumer, scope, concern, subject?)
~~~

`subject` is optional. Parent/dashboard views may aggregate these instances, but completion control must operate on the leaf instances.

## Architectural implication

A Coverage Map is a projection over these instances, not the canonical owner of them.

Canonical sources remain:

- Engineering Graph topology;
- selected Consumer;
- selected scope roots;
- production semantic claims and optional subjects;
- Core artifact realization;
- explicit project applicability facts;
- blockers and lifecycle state.

From those inputs Harness derives activation, proof state, remaining work and completion readiness.