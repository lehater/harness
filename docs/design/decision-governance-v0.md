# Decision Governance v0

Status: experimental.

## Purpose

Decision Governance prevents an artifact-producing agent from treating the first
satisfactory solution as if it were the only solution. It sits above Harness
Core and is composed into strict semantic admission.

It answers two independent questions:

1. **Exploration** — how diligently must the producer search for materially
   different ways to satisfy its responsibility?
2. **Autonomy** — after exploration, may the producer choose among several viable
   same-Authority alternatives without creating a Question?

Authority ownership remains an absolute boundary. Autonomy never permits a
producer to decide semantics owned by another Authority.

## Production loop

```text
actionable CREATE
        ↓
knowledge-kind decision contract
        ↓
blind Decision Exploration
        ↓
discovered alternative space
        ↓
artifact producer forms candidate + viability disposition
        ↓
Decision Governance
        ↓
DETERMINED / DELEGATED / ESCALATED
        ↓
semantic admission
```

Decision Exploration and Decision Governance are separate acceptance-evidence
responsibilities. The explorer is intentionally pre-choice: its evidence may not
contain preferred/selected/chosen/disposition fields.

Decision Governance is acceptance evidence, not an Engineering Graph Capability
and not a Core entity.

## Explorer execution boundary

Before exploration, Harness derives a `harness-decision-explorer-request` from
the current Authority context, decision contract, effective exploration policy
and accepted prerequisite lifecycle baseline.

The request intentionally excludes candidate/write-target content. Its
deterministic `request_id` binds exploration evidence to the exact authorized
pre-choice input manifest. A policy or accepted-prerequisite identity change
therefore invalidates stale exploration evidence.

This is a **context contract**, not proof of physical LLM isolation. A runtime
that secretly leaks candidate/preferred-solution context can still violate the
contract without the schema being able to observe it. Physical isolation, when
required, belongs to the agent/orchestration runtime rather than Core.

## Decision surface

When a target project supplies a `harness-decision-policy`, each participating `knowledge_kind` declares a finite set of decision axes. The
artifact skill must explicitly inspect every required axis for the selected
scope. Exploration classifies axis applicability as:

- `APPLICABLE` — the axis is challenged and must expose discovered decision points;
- `NOT_APPLICABLE` — accepted canonical evidence proves the axis does not apply;
- `UNRESOLVED` — applicability cannot yet be established and admission stops.

There is deliberately no `NO_MATERIAL_DECISION` status. For an applicable axis,
absence of a discovered decision point is a failed exploration, not an agent
assertion that no choice exists.

Each axis declares material-difference dimensions and challenge strategies.
At `EXPLORE` or deeper, multiple distinct probes must produce at least two
alternatives whose material effects differ on those dimensions. The contract
does not claim exhaustive enumeration; it proves execution of the required
falsification/search procedure.

## Exploration depth

Four ordered levels are supported:

- `LOCAL` — accepted project knowledge and local reasoning;
- `EXPLORE` — materially different alternatives plus a counterfactual challenge;
- `RESEARCH` — `EXPLORE` plus external authoritative evidence;
- `DEEP_RESEARCH` — `RESEARCH` plus multiple, diverse external evidence sources.

A project policy may raise exploration depth globally, per `knowledge_kind`, or
per decision axis. The knowledge-kind contract defines the minimum and project
policy cannot weaken it.

## Autonomy

Four ordered autonomy levels are supported: `NONE`, `CONSERVATIVE`, `BROAD`,
and `MAXIMUM`.

Each decision axis declares the minimum autonomy required for the producer to
choose among multiple viable alternatives. Project policy selects the active
autonomy level. `MAXIMUM` still cannot cross an Authority boundary.

**Autonomy governs choice, not diligence.** A high-autonomy project still performs
the same required exploration before the producer chooses.

## Decision dispositions

For each material decision point:

- `DETERMINED` — exactly one viable alternative remains and no alternative is unresolved;
- `DELEGATED` — several viable alternatives remain, the current Authority owns
  the choice, and policy delegates it to the producer;
- `ESCALATED` — the choice is unresolved or not delegated. An unresolved Core
  `Question` addressed to the deciding Authority must block the affected
  artifact or capability.

Missing information and un-delegated choice therefore converge on the existing
Core feedback mechanism.

## Project policy

A target project may provide a `harness-decision-policy` document:

```yaml
version: 1
kind: harness-decision-policy
defaults:
  exploration: EXPLORE
  autonomy: CONSERVATIVE
knowledge_kinds:
  - knowledge_kind: system-architecture
    exploration: RESEARCH
    autonomy: BROAD
    axes:
      - axis: state-placement
        exploration: DEEP_RESEARCH
        autonomy: NONE
```

A project policy activates the experiment. Without one, strict admission retains existing behavior. The initial experiment covers `domain-model`, `application-design`,
`system-architecture`, and `implementation-design`. Other routed knowledge
kinds remain unchanged until project evidence justifies extending the contract.

## Admission integration

`semantic_admission.py` evaluates Decision Governance after normal semantic
acceptance for participating knowledge kinds. A rejected governance evaluation
rejects admission and clears accepted semantic claims for that candidate.

Strict admission first evaluates the separate pre-choice exploration evidence:
applicability, probe diversity, material dimensions, alternative classes and
research depth. Governance then requires the candidate to classify exactly that
explored alternative set; it may not silently add or drop alternatives.

This separation prevents the artifact producer from certifying its own claim
that no choice existed merely by writing a rationale after selecting a candidate.

It cannot prove the intellectual quality or global completeness of generated
alternatives. That limitation is explicit rather than hidden behind an agent
assertion that review was completed.

## Core boundary

Core remains unchanged. It receives only real unresolved semantic escalations as
Questions. Candidate decision points, rejected alternatives, research notes, and
producer choices remain generated admission evidence.


## Execution assurance

Decision Exploration has a third independent control dimension in addition to
exploration depth and decision autonomy: execution assurance.

- `REQUEST_BOUND` proves that exploration is bound to the exact candidate-free
  Explorer Request derived by Harness.
- `ATTESTED_ISOLATED` requires an external trusted control plane to prove that
  the explorer actually ran in an isolated context restricted to that request.

Harness currently verifies only `REQUEST_BOUND`. If project policy requires
`ATTESTED_ISOLATED`, admission fails closed until a trusted executor/verifier
adapter exists. A producer-authored receipt or field such as `isolated: true`
does not upgrade assurance.

See `docs/design/decision-explorer-execution-assurance-v0.md`.
