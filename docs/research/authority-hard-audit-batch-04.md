# Authority hard audit — batch 4

## OBLIGATION-ANALYSIS — KEEP

Decision identity: identify governed normative sources, decide scoped applicability/interpretation, trace routed constraints and coverage.

Knowledge output: obligation/applicability coverage plus routed constraints and Questions.

Consumers: semantic owner Authorities and Verification. Source provenance/lifecycle changes independently from constrained design.

Applicability atomicity: law/contract/license/policy are source classes, not separate decision ownership families.

Verdict: KEEP.

## CHANGE-TRANSITION-DESIGN — KEEP

Decision identity: validity of movement between accepted source and target states when intermediate/coexistence states matter.

Knowledge output: transition contract: ordering, compatibility window, irreversible points, progression/recovery/retirement constraints.

Consumers: Implementation, Verification/Test, Operability.

Endpoint owners do not determine transition validity; consumers can use accepted transition knowledge without co-owning endpoints.

Applicability is crisp: atomic replacement with no material intermediate state is N/A.

Verdict: KEEP.

## OPERABILITY-DESIGN — KEEP

Decision identity: what runtime evidence must exist for diagnosis/correlation/health/dependency visibility.

Knowledge output: runtime evidence/diagnosability contract.

Consumers: Component, Verification/Test, Implementation and operations-facing terminal use.

Logging/metrics/tracing are realization mechanisms, not separate Authorities. Health/correlation/dependency visibility jointly answer diagnosability and currently share consumers/lifecycle.

Verdict: KEEP.

## ENGINEERING-POLICY — WATCH

Decision identity claimed: project-selected cross-cutting engineering obligations/anti-pattern constraints.

Knowledge output: normative engineering obligations.

Consumers: multiple design and implementation Authorities.

Hard risk: this can become a miscellaneous bucket for preferences already owned by Architecture, Security, Data, Quality or organizational policy. Applicability phrase “project selects principles” does not itself prove independent project knowledge.

To KEEP, require fixtures where a policy:
- constrains multiple Authorities;
- has independent provenance/lifecycle;
- remains normative while semantic owners change;
- can be consumed without ENGINEERING-POLICY co-owning their decisions.

Verdict: WATCH. Strong anti-bucket acceptance tests required.

## Batch result

- OBLIGATION-ANALYSIS: KEEP
- CHANGE-TRANSITION-DESIGN: KEEP
- OPERABILITY-DESIGN: KEEP
- ENGINEERING-POLICY: WATCH

P1: ENGINEERING-POLICY is insufficiently falsified against becoming a generic policy bucket.
