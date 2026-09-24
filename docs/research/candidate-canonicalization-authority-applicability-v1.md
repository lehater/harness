# Candidate canonicalization: authority discovery and applicability v1

Status: candidate proposal only. Do not merge/canonicalize without explicit approval.

## Proposed architecture

```text
HARNESS
├── Reference Engineering Knowledge
│   ├── decision obligations / applicability rules
│   ├── candidate Authority + Capability kinds
│   ├── dependency rules
│   └── semantic acceptance contracts
├── Routing / selective context
├── Skills
├── Project state
├── Enforcement / validators
├── Evals
└── Canonicalization rules
        |
       Agent
        |
Project Evidence -> Applicability Assessment -> Project Engineering Graph
```

## Core changes

**No new Core entity.**

Keep Authority, CanonicalArtifact, CapabilityId and Question.

Decision Obligation and Applicability Assessment remain reference/derivation concepts until a concrete consumer failure proves they need persistent Core identity.

## Engineering Graph changes

Clarify its role as **project-specific instantiated topology**.

Add normative wording:

- reference catalog membership never implies project instantiation;
- every included production contract must be justified by project applicability plus consumer/terminal liveness;
- omission of a candidate obligation must be backed by an assessment result, not subjective project simplicity;
- actual `requires` edges are project knowledge necessities, not reference-topic relatedness.

Do not add a universal N/A node/state to Engineering Graph.

## Reference catalog changes

Evolve catalog entries from prose-only `applies_when` toward reusable assessment contracts:

- decision obligation;
- activation evidence;
- disconfirming/N/A evidence;
- evidence dependencies;
- reopening conditions;
- candidate produced knowledge;
- expected consumer classes.

Authority entries remain candidate ownership boundaries. They are not mandatory project instances.

Replace merge guidance based on "simple" or "trivial" projects with evidence about knowledge-interface independence, consumers and lifecycle.

## Authority discovery

Canonicalize knowledge-flow-first discovery:

material decisions -> accepted knowledge -> consumers -> necessity -> knowledge-flow graph -> grouping -> cohesion/encapsulation/independent evolution.

Extend the current atomicity test with consumer evidence, dependency necessity, encapsulation and liveness.

## DDD

Keep domain strategy and model-context strategy as distinct capability/decision families.

Do not yet force two Authorities. Split ownership only when concrete knowledge interfaces and independent lifecycles justify it.

Prohibit Product Capability -> Bounded Context and Subdomain -> Bounded Context inference without model/language-boundary evidence.

## Skills

Add one assessment-oriented agent skill only if needed by implementation:

`assess-engineering-obligation`

Input:
- one reference obligation;
- relevant project evidence/upstream accepted knowledge.

Output:
- REQUIRED / NOT_APPLICABLE / UNRESOLVED;
- evidence/rationale;
- reopening conditions;
- required capability or blocking Question.

Keep production skills separate from assessment.

## Semantic acceptance

Add an acceptance contract for applicability evidence:

- evidence is project-grounded and addressable;
- rationale proves the state rather than restating it;
- N/A includes reopening conditions;
- REQUIRED names transferable accepted knowledge;
- UNRESOLVED exposes the missing fact/decision;
- assessment dependencies permit invalidation.

## Validators

Add mechanical checks for assessment shape and regression fixtures. Validators should enforce invariants, not decide semantic applicability from prose.

## Evals

Retain schema fixtures, but add project behavior regressions covering:

- single-process CRUD/CLI;
- payments + concurrency/retries/reconciliation;
- multi-model domain;
- security-heavy service;
- legacy/migration transition.

Expected behavior includes selective context topics, forbidden invented complexity and explicit N/A/unresolved outcomes.

A later agent-level eval may run an actual model against these fixtures and compare structured assessment output. The repository fixtures define the oracle independently of the candidate model.

## Migration / compatibility

Existing project Core and Engineering Graph documents remain valid.

No migration is required for Core v0.

Reference catalog enrichment can be additive. Existing `applies_when` remains readable during migration.

Projects are not required to persist N/A nodes in their Engineering Graph. Assessment evidence may live in project policy/coverage state or a future dedicated projection.

## Canonicalization gate

Before canonicalization:

1. all repository checks green;
2. research validators green;
3. no remaining "simple project/domain" wording used as an applicability/merge proof in candidate guidance;
4. PR remains draft until explicit approval;
5. main remains untouched.

The current research supports this candidate architecture. It does not justify a larger workflow/state-machine model.
