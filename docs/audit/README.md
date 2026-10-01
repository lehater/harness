# Harness Audit and Evolution Capture Policy

Status: canonical repository working policy for audit/evolution capture.

This directory separates three different kinds of knowledge. Do not merge them
into one backlog.

## Routing rule

```text
Is current Harness behavior demonstrably wrong?
    |
    +-- YES --> HARN-* in harness-audit-backlog.md
    |
    +-- NO --> Is this an optional direction, recommendation or question?
                    |
                    +-- YES --> EVO-* in harness-evolution-radar.md
                    |
                    +-- NO --> Has the direction been explicitly accepted?
                                    |
                                    +-- YES --> owning canonical spec / ADR
                                                (+ mark related EVO ADOPTED)
```

### 1. Defect / design gap -> Audit Backlog

Use `docs/audit/harness-audit-backlog.md` when there is evidence that current
Harness behavior violates an invariant, contract or reproducible expected
behavior.

Examples:

- false `COMPLETE` / `CURRENT`;
- contradictory state semantics;
- wrong next action;
- missing state that makes documented behavior impossible;
- dependency/currentness behavior that contradicts the accepted model.

A useful defect entry contains evidence and consequence, not merely a preferred
design.

Identifier: `HARN-*`.

Before creating one:

1. search existing `HARN-*` entries by root cause and invariant;
2. add evidence to an existing item when it is the same defect;
3. create a new ID only for a distinct root cause.

### 2. Recommendation / research / idea -> Evolution Radar

Use `docs/audit/harness-evolution-radar.md` when current behavior may be
acceptable, but a direction could improve simplicity, assurance, architecture,
portability, agent behavior or future capability.

Identifier: `EVO-*`.

Classify it as:

- `RECOMMENDATION` — evidence already suggests the direction is useful;
- `RESEARCH` — a question/experiment is needed before deciding;
- `IDEA` — promising but weakly supported hypothesis.

A Radar item is not technical debt and does not imply an implementation
commitment.

Before creating one:

1. search existing `EVO-*` by underlying direction, not wording;
2. reuse the existing item if the idea is materially the same;
3. state expected value and, for uncertain ideas, what evidence would validate
   or reject it;
4. state why the item is not currently a defect when that distinction may be
   ambiguous.

### 3. Accepted decision -> Canonical spec / ADR

The Radar is not an architecture source of truth.

When a direction is explicitly accepted:

1. write the normative decision in the owning canonical design/specification or
   ADR;
2. update the related `EVO-*` to `ADOPTED`;
3. keep only a short pointer/rationale in the Radar.

If an adopted decision later proves incorrect behavior in the implementation,
that implementation failure may separately become a `HARN-*`.

## Promotion and cross-linking

Allowed transitions:

```text
EVO CAPTURED
  -> INVESTIGATING
  -> VALIDATED
  -> ADOPTED -> canonical spec / ADR

EVO
  -> PARKED
  -> REJECTED

EVO investigation proves current behavior wrong
  -> create/reuse HARN-* and cross-link

HARN investigation shows no defect
  -> mark HARN REJECTED
  -> optionally capture the remaining improvement idea as EVO-*
```

Do not silently convert one identifier family into the other; preserve history
with cross-links.

## Ambiguous cases

When evidence is insufficient to prove a defect, prefer:

```text
EVO type: RESEARCH
status: CAPTURED
```

and record the falsifiable question/evidence needed.

This prevents optional architecture preferences from acquiring defect severity
without proof.

## New-chat / new-agent procedure

An agent with no conversation history should be able to persist a finding using
only repository state.

For any request to capture a Harness observation:

1. read the root `AGENTS.md`;
2. read this file;
3. search both ledgers;
4. classify using the routing rule above;
5. update the appropriate existing entry or allocate the next identifier;
6. preserve links to code/spec/scenario evidence;
7. do not change `main` directly; follow the repository branch/PR discipline.

Conversation history is never required to decide where the record belongs.
