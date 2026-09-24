# Authority Boundary Discovery v1 — research method

Status: experimental. This document does not change Core or canonical Engineering Graph semantics.

## Problem

The existing atomicity test (semantic cohesion, independent change, public contract) can accept a plausible prose boundary before any producer/consumer knowledge flow has been demonstrated. Engineering Graph is stricter: a dependency exists only when a produced Capability is required to form another production output, and every public Capability must be live through a consumer or an explicit terminal reason.

The research hypothesis is that Authority discovery must therefore begin from engineering decisions and knowledge flow, then group producers into ownership boundaries. Authority names must not be invented first and supplied with outputs afterward.

## Discovery order

1. Identify a material engineering decision without naming a new Authority.
2. Identify the accepted engineering knowledge produced by that decision.
3. Identify a concrete consumer decision or terminal reason for that knowledge.
4. For a producer/consumer edge, state the consumer output and prove that the upstream knowledge is required to form it without the consumer inventing the producer's decision.
5. Test encapsulation: the consumer should be able to consume accepted output knowledge rather than co-own the producer's internal reasoning.
6. Build the knowledge-flow DAG.
7. Group decision/production nodes into Authority candidates.
8. Apply semantic cohesion and independent-change tests to the grouping.

## Evidence contract

An Authority-boundary claim is supported by a ledger entry containing:

- decision: the owned engineering decision;
- output: the accepted knowledge product/capability kind created by that decision;
- consumers: one or more concrete downstream decision/output pairs, or an explicit terminal reason;
- requires: for every dependency edge, why the consumer cannot correctly form its output without the upstream knowledge;
- encapsulation: why the accepted output is sufficient for the consumer without sharing ownership of the producer's internal decision process.

A topic, activity, document name, concern, or useful analysis is not by itself an Authority.

## Interpretation rules

- Different prerequisite sets do not force an Authority split. One Authority may own several related outputs.
- Absence of a direct edge between two Authorities does not imply they must merge. Independent Authorities may feed a common consumer.
- A physical document is not required at an Authority edge. The transferable unit is accepted knowledge (Capability); CanonicalArtifact materializes that knowledge.
- A useful analysis artifact does not become a public Capability unless a concrete consumer requires accepted coverage/evidence or it has an explicit terminal reason.
- Feedback does not justify a static production cycle. Questions plus canonical repair remain the feedback mechanism.
- If two candidate producers require continuous joint ownership of the same decision rather than exchanging accepted knowledge, the proposed boundary is suspect.

## Boundary tests

A candidate Authority is supported when all applicable tests pass:

1. **decision identity** — a coherent owned class of engineering decisions exists;
2. **knowledge output** — those decisions produce identifiable accepted engineering knowledge;
3. **consumer evidence** — output knowledge is live through a concrete consumer or terminal reason;
4. **dependency necessity** — each claimed edge names knowledge actually required to form the consumer output;
5. **encapsulation** — consumers depend on accepted outputs rather than producer internals;
6. **semantic cohesion** — grouped decisions form one coherent ownership class;
7. **independent evolution** — producer internals and consumer decisions can evolve without re-owning each other's decisions while the knowledge contract remains valid.

## Falsification targets

The method must reject:
- semantic labels with no knowledge output/consumer;
- dependencies justified only by conceptual relatedness or temporal ordering;
- public capabilities with no consumer/terminal reason;
- splits whose supposed consumers must co-own the same internal decision.

The method must accept:
- ordinary producer/consumer chains;
- parallel independent Authorities with no edge between them;
- multiple outputs with different prerequisites under one coherent Authority;
- explicit terminal knowledge;
- analysis that remains private/non-capability until a consumer requires accepted evidence.

The executable research fixture is `spec/research/authority-boundary-knowledge-flow-v1.yaml`.
