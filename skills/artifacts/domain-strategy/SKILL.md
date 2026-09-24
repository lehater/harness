---
name: domain-strategy
description: "Use for actionable CREATE work that decides strategic domain decomposition, subdomain classification or investment intent."
---
# Domain Strategy

## Trigger
Use for `knowledge_kind: domain-strategy` when strategic classification of domain responsibilities is materially required.

## Inputs
Accepted Product Requirements and relevant Discovery evidence.

## Read boundary
Read only accepted problem evidence, product behavior and existing domain strategy needed to classify problem-space responsibilities. Do not use technical decomposition as evidence of domain boundaries.

## Procedure
1. Identify problem-space domain responsibilities from accepted behavior/evidence.
2. Classify only where classification changes investment, isolation or downstream design attention.
3. Record subdomain landscape, strategic classification and rationale.
4. Do not decide model-language applicability, tactical structures, APIs, storage or deployment.
5. Route unresolved product meaning as Questions.
6. Produce the target repository's canonical domain-strategy artifact and apply semantic acceptance.

## Stop conditions
Stop when material product meaning is unresolved, a proposed distinction has no accepted evidence, or the decision actually belongs to model-context, tactical, application or technical design.

## Output contract
Prefer project-native artifacts. Accepted output must state the subdomain/responsibility landscape, strategic classifications that have engineering consequences, evidence/rationale, consumers or terminal reason, and reopening conditions.

## Acceptance checks
- every strategic distinction traces to accepted evidence;
- every classification has a concrete consumer or terminal strategic reason;
- technical/service/package boundaries are not treated as domain evidence;
- model-context and tactical decisions are not re-owned.

## Registration
Register accepted capabilities under `DOMAIN-STRATEGY`.

## Human projection
Project-native strategic-domain documentation is sufficient; generated summaries are disposable projections.
