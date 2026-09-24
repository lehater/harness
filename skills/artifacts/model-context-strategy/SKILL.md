---
name: model-context-strategy
description: "Use for actionable CREATE work that decides model-language applicability, context relationships or translation contracts."
---
# Model Context Strategy

## Trigger
Use for `knowledge_kind: model-context-strategy` when independently modeled semantic contexts or languages require explicit boundaries or translation.

## Inputs
Accepted Product Requirements, relevant Domain Strategy when applicable, and existing accepted model-language evidence.

## Read boundary
Read only accepted semantics needed to decide where models apply and how they relate. Do not infer contexts from services, packages, schemas, repositories or teams.

## Procedure
1. Identify where distinct models/languages are materially required.
2. Define model applicability boundaries and semantic relationships.
3. Define translation contracts only where consumers require them.
4. Do not infer contexts from technical decomposition.
5. Do not re-own strategic investment classification or tactical internals.
6. Route unresolved upstream meaning as Questions and produce the canonical project-native artifact only when prerequisites are accepted.

## Stop conditions
Stop when a boundary depends on unresolved product/domain meaning, when no independent model-language distinction is evidenced, or when the decision belongs to tactical or technical design.

## Output contract
Prefer project-native artifacts. Accepted output must state model-language applicability, context relationships, required translations, evidence, consumers and reopening conditions.

## Acceptance checks
- each context boundary has independent semantic evidence and consumer value;
- one coherent model is not split artificially;
- technical topology is not used as a proxy for model boundaries;
- strategic classification and tactical internals remain with their owners.

## Registration
Register accepted capabilities under `MODEL-CONTEXT-STRATEGY`.

## Human projection
Project-native model/context documentation is sufficient; generated maps are disposable projections.
