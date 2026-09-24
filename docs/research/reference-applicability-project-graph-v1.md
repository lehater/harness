# Reference knowledge → applicability → Project Engineering Graph v1

Status: experimental research. This does not change Core semantics.

## Hypothesis

Harness should separate two models:

1. **Reference Engineering Knowledge** — reusable knowledge about decision kinds, candidate Authority/Capability kinds, applicability/dependency rules, assessment procedures, skills, acceptance rules, validators and evals.
2. **Project Engineering Graph** — project-specific instantiated Authorities, required Capabilities, actual requires edges, accepted NOT_APPLICABLE evidence and unresolved Questions/obligations.

Reference presence is not project applicability. The reference catalog is a discovery/routing system, not a mandatory graph template.

```text
Reference Engineering Knowledge + Project Evidence
                    |
             applicability assessment
                    |
           Project Engineering Graph
```

## Existing Core coverage

The experiment found that most runtime semantics already exist:

- **Authority** represents an instantiated project decision-ownership boundary.
- **CapabilityId** represents accepted transferable engineering knowledge.
- **CanonicalArtifact** materializes accepted project knowledge.
- **Question** represents an unresolved semantic gap and can block a future Capability.
- **Engineering Graph production contracts** represent actual project `requires` dependencies.
- **knowledge_kind + skill registry** already provide selective execution routing.

Therefore Decision Obligation and Applicability Assessment are not justified as new Core entities.

They belong first in the **reference/assessment layer** that decides whether a project graph node should exist.

## Missing contract

The missing concept is not a new project entity. It is a mechanically checkable **assessment result** for a candidate decision obligation:

- `REQUIRED` — material project evidence proves that accepted knowledge must be produced;
- `NOT_APPLICABLE` — evidence proves that the decision problem is absent for the current project state;
- `UNRESOLVED` — available evidence cannot yet prove either result.

Every result records:

- the reference obligation being assessed;
- project evidence;
- rationale;
- upstream evidence dependencies;
- reopening conditions.

`REQUIRED` additionally identifies the capability/decision knowledge that must enter the project graph.

`UNRESOLVED` identifies a Question/obligation that prevents silent omission.

`NOT_APPLICABLE` is accepted assessment knowledge, not missing work. It does not create a fake project Capability merely to say "N/A".

## Invalidation

Applicability is derived from evidence and therefore must be reopened when an upstream fact used by the assessment changes.

The research model uses explicit `depends_on_evidence` plus `reopen_when`. This is sufficient for invalidation without introducing a Core lifecycle state machine.

Example:

```text
evidence: single process, no concurrent writers
  -> distributed-topology = NOT_APPLICABLE

later evidence: multiple workers + retrying external delivery
  -> upstream evidence changed
  -> reopen assessment
  -> REQUIRED or UNRESOLVED
```

## Cross-domain result

The model was applied to DDD, concurrency, consistency/distributed systems, security, persistence, performance/quality, operability, change transition/migrations and verification/test design.

Across these domains the same structure held:

```text
candidate decision obligation
  -> inspect project evidence
  -> REQUIRED | NOT_APPLICABLE | UNRESOLVED
  -> if REQUIRED, instantiate accepted knowledge production
  -> prove concrete consumers/requires
  -> group producers into Authority boundaries
```

No domain required a new Core primitive for the assessment itself.

### DDD

A model-context obligation becomes REQUIRED when independently valid model/language boundaries or translation relationships are material. Product capabilities or subdomains alone do not prove Bounded Contexts.

### Concurrency / consistency / distributed systems

Parallel execution, retries, multiple writers, remote partial failure, replicated state or cross-boundary ordering can activate decisions. Their absence may support N/A. Project size cannot.

### Security

Trust/admission/protection decisions may be REQUIRED even in a small codebase. A local trusted runtime may make some threat classes N/A while still requiring explicit security analysis for other attack surfaces.

### Data / persistence

Durable representation, schema constraints, recovery or independent storage semantics activate data decisions. In-memory ephemeral state can support N/A for physical persistence design when evidence and reopening conditions are explicit.

### Performance / quality

Measurable SLO/capacity/cost/latency constraints activate quality decisions. "Fast enough" without a material consumer is not a Capability.

### Operability

Independent runtime diagnosis/health/correlation evidence activates operability knowledge. Logging as a mechanism does not.

### Change transition / migration

Material coexistence, irreversible transformation, ordering, gates or retirement activates transition knowledge. Atomic replacement with no material intermediate state can prove N/A.

### Verification / test design

Verification evidence is baseline for accepted realization. Independent Test Design is conditional: it activates when executable oracle/state-transition decisions would otherwise be invented downstream.

## Authority discovery result

The knowledge-flow-first method generalizes beyond DDD:

1. discover material decisions;
2. identify accepted knowledge outputs;
3. identify concrete consumers;
4. prove necessity of each dependency;
5. build the knowledge-flow graph;
6. group producer decisions;
7. apply cohesion, encapsulation and independent-evolution tests.

This reverses the failure-prone sequence of naming an Authority first and supplying plausible prose afterward.

Reference Authority catalog entries should therefore be treated as **candidate reusable boundaries**, not project instances.

## "Simple project" prohibition

Size, repository count, deployment shape or subjective simplicity is never an applicability proof.

Valid omission has the form:

```text
material decision conditions absent
  -> evidence-backed assessment
  -> NOT_APPLICABLE
  -> explicit reopening conditions
```

Likewise Authority merge/split decisions are justified by knowledge interfaces, consumers, lifecycle and ownership cohesion—not by calling a project simple.

## Selective context

The reference layer must act as a map.

For one current decision problem the agent should receive only:

- the candidate obligation and applicability rule;
- relevant project evidence;
- upstream accepted capabilities/evidence;
- the semantic acceptance contract;
- the skill needed to assess or produce the knowledge;
- directly relevant regression cases.

The full methodology/catalog should not be injected into every execution context.

## Self-hosting

Harness evolution and project engineering are distinct flows:

```text
Harness N
  -> research candidate N+1
  -> falsification + project/eval evidence
  -> explicit canonicalization
  -> Harness N+1

canonical Harness + project evidence
  -> applicability
  -> Project Engineering Graph
  -> accepted project knowledge
```

A candidate rule cannot use its own candidate output as its sole validating evidence.

## Research conclusion

The architecture is viable without adding DecisionObligation or ApplicabilityAssessment to Core v0.

The smallest justified extension is a **reference assessment contract** outside Core plus regression evals that prove:

- every candidate obligation is assessed rather than silently omitted;
- N/A requires evidence and reopening conditions;
- unresolved assessment becomes an explicit blocker/question;
- REQUIRED knowledge enters the project graph only with a real consumer/terminal reason;
- project graph dependencies are actual knowledge necessities;
- routing selects only relevant reference context.

See `spec/research/reference-applicability-project-graph-v1.yaml` and `spec/research/project-behavior-evals-v1.yaml`.
