---
name: problem-evidence
description: "Use for actionable CREATE work requiring accepted problem/discovery evidence. Capture the problem, affected actors, desired outcome, evidence, boundaries and unresolved downstream decisions without inventing requirements, domain semantics or solution design."
---

# Problem Evidence

## Trigger

Use when Engineering Graph / target state exposes actionable `CREATE` work whose
`knowledge_kind` is `problem-evidence`, or when the owning Discovery Authority
must establish the accepted problem/evidence baseline needed by downstream product
design.

## Inputs

- actionable grouped artifact work and owning Discovery Authority;
- explicit user/stakeholder problem statement;
- accepted observations, incidents, research or existing project evidence;
- current project scope when already established.

## Read boundary

Read only sources needed to establish:

- the observed problem or unmet need;
- affected actor(s);
- desired outcome;
- evidence/provenance relevant to the problem;
- explicit scope/non-goal boundaries.

Implementation code, architecture and domain models are secondary evidence only.
Do not reverse-engineer desired product behavior from existing code.

## Procedure

1. Confirm the work is actionable `CREATE`, not WAIT/PENDING.
2. State the observed problem/need independently of a proposed solution.
3. Identify the affected actor or system context when known.
4. State the desired outcome in problem-space language.
5. Record concrete evidence/provenance that justifies the problem statement.
6. State scope and non-goal boundaries needed to prevent solution drift.
7. Separate unresolved downstream decisions explicitly:
   - product behavior/acceptance -> Product Requirements;
   - semantic ownership/invariants -> Domain Design;
   - system/interface/data realization -> downstream technical Authorities.
8. If accepted evidence conflicts on a fact needed even to state the problem,
   create a Question to the Discovery Authority rather than selecting a convenient
   interpretation.
9. Produce the smallest project-native canonical artifact that fits the target
   repository.
10. Apply common semantic acceptance, register the artifact and re-evaluate the
    target Consumer.

## Stop conditions

Do not accept Problem Evidence when:

- the problem statement is merely a preferred implementation;
- affected need/outcome is unsupported by accepted evidence or explicit user input;
- conflicting evidence changes whether the problem exists or who is affected;
- completing the artifact would require choosing product behavior, domain
  semantics or architecture.

Unknown downstream design choices are not a reason to block accepted Discovery
evidence; record them as downstream unknowns instead.

## Output contract

Prefer a project-native canonical artifact. No universal Harness schema is
required in v0.

The artifact should contain, where material:

- problem/need;
- affected actor/context;
- desired outcome;
- evidence/provenance;
- scope boundary;
- non-goals;
- unresolved downstream decisions.

Do not add sections with no semantic value merely to match a template.

## Acceptance checks

- describes the problem rather than a solution design;
- evidence is traceable to accepted input or explicit user/stakeholder statement;
- desired outcome is understandable without technical realization choices;
- no product requirement is silently accepted here;
- no Domain/Architecture/Interface ownership is stolen;
- unresolved downstream decisions remain explicit.

## Registration

Register the accepted project-native artifact as a Core `CanonicalArtifact`
owned by the Discovery Authority.

It provides every problem-evidence CapabilityId in the grouped artifact work that
the accepted artifact actually satisfies.

Dependencies include only accepted canonical evidence artifacts semantically
relied upon by this artifact.

## Human projection

Normally the canonical artifact is already human-readable. No generated
projection is required.
