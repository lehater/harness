# Research — Real-project semantic acceptance pilots

Status: research only. Not canonical. No main changes.

This document closes the requested real-project validation for the semantic
completeness/correctness research.

## Scope

Two current project baselines were inspected directly from their canonical
repositories:

- Nutrition Management;
- NAPMS.

The pilots intentionally do not modify either project. They consume their current
canonical artifacts and Harness integration metadata as research input.

Executable pilot:
`validators/validate_semantic_acceptance_real_project_pilots.py`.

## Pilot 1 — Nutrition Management

### Selected real artifact

Canonical artifact:

`docs/redesign/test-design.md`

Registered by current project Harness state as:

- artifact: `REDESIGN-TEST-DESIGN`;
- Authority: `TEST-DESIGN`;
- capability: `nutrition-management.redesign.test-design`;
- prerequisite includes `REDESIGN-VERIFICATION-DESIGN`.

The artifact contains a real executable test-contract catalogue, including:

- `TD-NT-01` deterministic target derivation;
- `TD-FK-01` nutrient evidence-state preservation;
- `TD-MC-01` explicit market `as_of`;
- `TD-PP-03` hard infeasibility versus technical failure;
- `TD-ARCH-01` dependency ownership;
- `TD-PERSIST-01` semantic persistence round-trip;
- `TD-CLI-03` technical failure versus domain outcome.

Upstream semantic source used:

`docs/redesign/verification-design.md`.

### Current project Coverage semantics

Nutrition currently intentionally does **not** bind the broad
`nutrition-management.redesign.test-design` capability to reusable Engineering
Coverage semantic claims.

The project's canonical semantic-claim binding file explicitly states that broad
design/test capabilities are not expanded unless their producer contract is made
explicit.

This is an important control result.

### Baseline result

The selected real Test Design subset satisfies the derived semantic obligations:

```text
REDESIGN-TEST-DESIGN -> semantic ACCEPTED
```

The acceptance result exposes no Coverage claims because the project does not
currently authorize such a binding.

Therefore:

```text
semantic ACCEPTED
+ no canonical semantic-claim binding
=> no Coverage proof manufactured
```

This is the expected safe result.

### Injected defect

The pilot removes `TD-CLI-03` while retaining the corresponding obligation.

Result:

```text
REJECTED
MISSING_OBLIGATION
```

The incomplete candidate is not accepted.

### Nutrition conclusion

The semantic acceptance mechanism fits a real project-native Markdown Test Design
without requiring conversion of the whole artifact into a universal Harness DSL.

It also preserves the current project's deliberate policy that Test Design does
not automatically prove generic Engineering Concerns.

This confirms the intended separation:

```text
artifact semantic acceptance
!=
Coverage claim authorization
```

## Pilot 2 — NAPMS

### Selected real artifact

Canonical artifact:

`docs/contracts/http/napms.openapi.yaml`

Registered as:

- artifact: `OPENAPI`;
- Authority: `INTERFACE-DESIGN`;
- capability: `engineering.interface.http-contract`;
- upstream contract requirements:
  `docs/contracts/http/napms-api-requirements.yaml`.

The current NAPMS semantic-claim bindings authorize this capability to prove:

- `engineering.interface.machine.contract`;
- `engineering.interface.machine.errors`;
- `engineering.interface.machine.compatibility`.

This makes NAPMS suitable for testing the complete semantic-acceptance-to-Coverage
bridge.

### Real interface subjects sampled

The pilot uses real OpenAPI operations and semantics, including:

- `materializeCurrentPolicy`;
- `submitAccessRequest`;
- request representation;
- result representation;
- explicit error responses.

### Baseline result

The real contract sample satisfies its obligations:

```text
OPENAPI -> semantic ACCEPTED
```

All three currently authorized semantic claims become usable proof in the pilot.

### Injected defect

The pilot changes the accepted upstream meaning of
`materializeCurrentPolicy` from supported to an incompatible value.

Result:

```text
REJECTED
SOURCE_FIDELITY_VIOLATION
```

After rejection:

- `engineering.interface.machine.contract` is not usable proof;
- `engineering.interface.machine.errors` is not usable proof;
- `engineering.interface.machine.compatibility` is not usable proof.

Therefore the experiment demonstrates the intended gate on a real project
capability that currently participates in Engineering Coverage.

## Combined executable result

The real-project pilot validator covers both repositories and reports:

```text
PASS 12 real-project pilot assertions across Nutrition and NAPMS
```

Together with the earlier generic defect-injection suite:

```text
PASS 33 assertions across 3 artifact kinds
```

the research now has both controlled and real-project evidence.

## Cross-project findings

### P0 — the mechanism must not equate acceptance with claim authorization

Nutrition proves this boundary.

An artifact may be semantically acceptable while its capability remains
intentionally unbound to reusable Coverage claims.

The semantic acceptance layer validates a realization; the production/claim
contract decides which Engineering Concerns that realization may prove.

### P0 — Coverage must consume only accepted claims

NAPMS proves the opposite direction.

A capability already authorized to prove reusable concerns must lose usable proof
when its artifact semantic acceptance fails.

### P1 — project-native artifacts are compatible with the model

Neither pilot requires the canonical artifact itself to become a generic Harness
knowledge document.

The minimal integration surface is:

- derive/extract material semantic assertions;
- derive artifact-specific obligations;
- evaluate against bounded canonical sources;
- emit generated acceptance evidence.

### P1 — assertion extraction is the next engineering problem

The pilot fixtures extract a bounded subset of semantic assertions from real
project artifacts.

For canonical implementation, this extraction should be:

- native for structured Harness artifacts;
- deterministic where project-native formats expose structure, such as OpenAPI;
- artifact-skill-driven for Markdown or other prose-heavy canonical sources;
- reviewed where semantic interpretation cannot be deterministic.

The research does not justify parsing arbitrary prose globally.

## Final research assessment

The original research question has now been tested at three levels:

1. conceptual architecture;
2. synthetic defect-injection across three artifact families;
3. real-project pilots on Nutrition Management and NAPMS.

No blocking architectural question remains.

The evidence supports a canonicalization proposal with these invariants:

```text
semantic claim authorization
AND current artifact realization
AND successful semantic acceptance
AND no blocking Question/lifecycle invalidation
=> usable Engineering Coverage proof
```

and:

```text
semantic acceptance
WITHOUT claim authorization
=> accepted artifact, but no generic Coverage proof
```

No Core expansion is demonstrated.

Do not merge this research branch into `main` automatically. Canonicalization
should be a separate deliberate change based on these results.
