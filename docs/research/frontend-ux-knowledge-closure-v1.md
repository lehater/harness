# Research experiment — granular frontend UX knowledge closure

Status: experimental branch evidence; not canonical until evaluated on a real project.

## Hypothesis

HUMAN-INTERFACE-DESIGN is still the correct Authority, but one broad human-interface capability hides independently useful knowledge needed to prove frontend completeness.

The experiment adds four knowledge kinds under the same Authority:

1. conceptual-interface-model
2. information-architecture-design
3. interaction-design
4. interface-topology-design

No Core entity and no new Authority is added.

## Harness-native interpretation

The experiment models knowledge, not document formats.

- Task Model proves intended USER work.
- Conceptual Interface Model proves the vocabulary/modes the UI exposes.
- Information Architecture proves organization/findability.
- Interaction Design proves actions/responses/states independent of screens.
- Interface Topology proves the complete set of views/contexts and navigation relationships.
- Screen/View Design proves local composition for every topology-required view.
- Site maps, wireframes, prototypes and Figma remain projections/evidence.

## Completeness invariant

```text
USER task
  -> interaction context or no-ui disposition
      -> topology view or non-view disposition
          -> expected Screen/View subject
```

A missing link rejects semantic closure instead of allowing implementation to invent it.

## Verification

Early interface verification may consume IA/Interaction/Topology before Screen/View realization. Findings route to owning Authorities through Questions; static production dependencies remain a DAG.

## Evaluation plan

1. synthetic fixture proves production frontiers and semantic closure;
2. apply the same topology to Prep without changing Prep product semantics;
3. observe real omissions, duplicated knowledge and ceremony;
4. only then decide whether to canonicalize, simplify or reject the model.
