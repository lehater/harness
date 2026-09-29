# Verification-oracle partial-loss audit v0

Status: completed; real verification-oracle omissions identified and class-specific live evaluator behavior measured.

## Question

Can semantic derivation testing expose a verification artifact that is
structurally traceable to an accepted requirement but whose observable oracle
does not actually verify all mandatory semantics of that requirement?

This follows the real-project corpus v4 result, where the live evaluator
consistently detected explicit constraint drift but missed a subtler semantic
omission.

The audit uses the pinned NAPMS snapshot:

`lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

## Canonical boundary

`docs/plans/first-mvp-test-intent.yaml` declares:

- its purpose is to define minimum executable verification proving
  implementation realizes every accepted first-MVP requirement;
- tests do not create design truth;
- every accepted `REQ-*` must appear in a scenario `verifies` list or use an
  explicit non-test verification method.

Therefore a scenario that declares `verifies: [REQ-X]` but whose `expect`
oracle cannot observe a mandatory semantic atom from `REQ-X` is a real
downstream semantic partial loss.

This distinguishes structural and semantic coverage:

```text
structural trace:
REQ-X -> scenario.verifies includes REQ-X              PASS

semantic trace:
mandatory atom from REQ-X -> observable scenario oracle
                                                      PASS or LOSS
```

Listing a requirement id is not sufficient semantic evidence.

## Four observed omissions

### 1. Initial ACTIVE state

Requirement `REQ-RULE-002`:

First successful materialization of Allowed access makes the resulting
authoritative current access operationally Active.

`MVP-REQ-PERMISSION` declares that it verifies `REQ-RULE-002`, but its
oracle checks only:

- DENIED creates no Rule;
- ALLOWED creates or resolves one exact-subject Rule;
- repeated Allowed requests converge.

It never checks the mandatory initial ACTIVE state.

Defect group:
`NAPMS-VERIFICATION-INITIAL-ACTIVE-LOSS`.

### 2. Current-address cardinality and representation

Requirement `REQ-RES-003`:

Each logical Resource endpoint has at most one current address realization,
represented as either one host address or one network prefix.

`MVP-REQ-RESOURCE` declares that it verifies `REQ-RES-003`, but its oracle
checks identity preservation, AuthorityScopeRef independence, absence of
automatic endpoint grouping and responsibility history. It does not test the
at-most-one current address constraint or host/prefix representation.

Defect group:
`NAPMS-VERIFICATION-CURRENT-ADDRESS-CARDINALITY-LOSS`.

### 3. Organizational responsibility is not authority

Requirement `REQ-BUS-008`:

Business Process organizational responsibility must not become an
authorization scope.

`MVP-REQ-BUSINESS` declares that it verifies `REQ-BUS-008`, but its oracle
checks Need independence, duplicate-Rule behavior, retirement/history,
zero-current-Need behavior and criticality metadata. It does not verify the
organization/authorization separation.

Defect group:
`NAPMS-VERIFICATION-BUSINESS-ORG-AUTHORITY-SEPARATION-LOSS`.

### 4. Effective conditions are evaluated, not state-rewritten

Requirement `REQ-RULE-004`:

Supported declarative effective conditions determine contribution at evaluation
time without redefining access identity or periodically rewriting stored
ACTIVE/INACTIVE state.

`MVP-REQ-RULE-OPERATIONS` declares that it verifies `REQ-RULE-004`, but its
oracle checks reversible ACTIVE/INACTIVE state, EffectiveWindow identity
preservation and realization-independent identity. It does not check
evaluation-time contribution or the prohibition on periodic stored-state
rewrites.

Defect group:
`NAPMS-VERIFICATION-EFFECTIVE-WINDOW-EVALUATION-LOSS`.

## Positive controls

Four requirement atoms explicitly preserved by the same verification artifact
were added as controls:

- source-only request authority;
- DENIED creates no Rule;
- no mandatory numeric quality targets;
- no heavy asynchronous first-MVP runtime requirement and explicit reopen
  conditions.

These cases make the calibration discriminate semantic omission rather than
merely treating Verification Design as suspicious by default.

## Full real-project corpus v5

`spec/semantic-derivation/real-project-corpus-v5.yaml` expands the accumulated
real-project benchmark to 24 cases:

- 16 ACCEPTED real derivations;
- 8 REJECTED edge defects;
- 6 unique known root-defect groups;
- 0 synthetic negative mutations.

The normal deterministic Scenario Suite passes the expert baseline and exposes
an evaluator that accepts all eight known bad edges as eight false negatives.

The four new omissions are all independent root defects in Verification Design;
they are not extra manifestations of the earlier Security Architecture or
materialization defects.

## Full v5 live execution

Workflow `36516143538` attempted the full 24-case corpus three times without
changing the corpus or expert labels.

No attempt produced a semantic score:

- attempt 1: malformed provider envelope, missing/invalid `version: 1`;
- attempt 2: same envelope failure;
- attempt 3: valid transport envelope but unknown request-bound case id,
  rejected as `INVALID`.

Evidence artifacts:

- `11011071197`,
  `sha256:2aad5d0e90b168c757c90493b4bcce73790d1212e53855b98837533086b50f60`;
- `11010987364`,
  `sha256:2d014e2d1014bbc9e2a66ab142423a2282821c3441eb510ea0df438b35896b66`;
- `11010703501`,
  `sha256:8c87107597358a844f30962feaf8d181ed3a0ed0338aca782c4afc5abd6f4372`.

Harness failed closed in every case. No score or stability claim is derived
from those attempts.

## Focused omission probe

To measure omission sensitivity separately from the accumulated 24-case
benchmark, the same four defects and four positive controls were extracted into:

`spec/semantic-derivation/verification-oracle-partial-loss-v1.yaml`.

This is not a different oracle. It is a class-focused view of the same canonical
facts.

The deterministic focused scenario passes with four true positives and four
true negatives under the expert labels.

### Live execution

Workflow: `36516544966`.

Corpus fingerprint:

`LCCORPUS-6b5c8c72116266e7c30ae64896efcf27f23f61ae08cb9595e9f0fed993c4301c`.

Attempt 1 failed before semantic scoring because the provider violated the
required versioned envelope.

Artifact `11011442213`,
digest
`sha256:64624e9759756f295c5b8fdbda1f0b985e9251492ad69f5c2db7e8a723cf0ed6`.

Attempt 2 produced two complete request-bound runs.

Both resolved to `mai-code-1.1-flash`.

Run 1:

- TP=2, TN=4, FN=2, FP=0;
- accuracy=`0.75`;
- detection recall=`0.5`;
- false-positive rate=`0.0`;
- missed `current-address-cardinality-loss`;
- missed `effective-window-evaluation-loss`.

Run 2:

- TP=2, TN=4, FN=2, FP=0;
- accuracy=`0.75`;
- detection recall=`0.5`;
- false-positive rate=`0.0`;
- missed `initial-active-loss`;
- missed `effective-window-evaluation-loss`.

Artifact `11011007957`,
digest
`sha256:952322f7c71ef4ff7805de96a5592dc32b7e5fe1cba7576dc1a2f650aa1abff3`.

### Per-case behavior

Across the two same-model runs:

- `business-org-not-authority-loss`: REJECTED in both; stable detection;
- `effective-window-evaluation-loss`: ACCEPTED in both; stable false negative;
- `current-address-cardinality-loss`: verdict changed between runs;
- `initial-active-loss`: verdict changed between runs;
- all four positive controls: ACCEPTED in both.

Stability evaluation:

```yaml
status: UNSTABLE
unstable_cases:
  - current-address-cardinality-loss
  - initial-active-loss
```

## Interpretation

This experiment adds two important findings.

First, evaluator quality is strongly defect-class dependent. On this focused
real-project set the evaluator accepted every valid verification derivation but
detected only half of the semantic omissions per run.

Second, evaluator instability is not explained only by Copilot `model:auto`
routing to different models. Both complete focused runs resolved to the same
observed model, `mai-code-1.1-flash`, yet two fixed omission cases changed
verdict across fresh sessions.

Therefore:

```text
same model identity
    does not imply
same semantic judgement
```

The task itself matters. Explicit contradictions are comparatively easy for the
current evaluator; omission detection requires proving that a mandatory source
atom has no sufficient counterpart in a target that may otherwise be mostly
correct.

The observed profile is:

```text
valid explicit preservation       -> 4/4 accepted in both runs
verification semantic omission    -> 2/4 detected per run
stable detected omission          -> 1
stable missed omission            -> 1
session-sensitive omissions       -> 2
```

No majority vote or consensus result is formed. Expert-reviewed canonical
knowledge remains the oracle; stability and per-class recall are measurements
of the evaluator.

## Consequence for Harness

The result strengthens the case for semantic derivation testing alongside
structural traceability:

- `verifies: [REQ-X]` proves declared trace, not semantic coverage;
- downstream verification oracles themselves need semantic derivation tests;
- evaluator calibration should be reported by defect class, not only aggregate
  accuracy;
- repeated fresh-session evidence matters even when observed model identity is
  unchanged.

No Core entity, scorer change, provider registry, consensus mechanism or new
orchestration framework is required.
