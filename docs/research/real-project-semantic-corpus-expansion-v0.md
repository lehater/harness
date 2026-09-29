# Real-project semantic corpus expansion v0

Status: completed; corpus expanded to 16 real Capability-edge cases.

## Purpose

Scale the first real-project semantic-derivation audit without adding synthetic
negative mutations or new Harness framework machinery.

The expansion keeps the same pinned project snapshots:

- Prep: `lehater/prep@b3ec3b0fec0d8ba29f2ca66867737e8838332592`;
- NAPMS: `lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

## Corpus v4

`spec/semantic-derivation/real-project-corpus-v4.yaml` contains 16 cases:

- 12 accepted real derivations;
- 4 rejected real edge contradictions;
- 2 unique underlying NAPMS root defects;
- 0 synthetic negative mutations.

New Prep coverage exercises:

- Machine Interface -> Screen/View search semantics;
- Frontend Performance/Capacity -> Component Design semantic-preserving degradation;
- Frontend Verification -> Test Design selection/focus semantics;
- Frontend Performance/Capacity -> Test Design profile invariants.

All four new Prep transitions are accepted canonical derivations.

## Case count is not defect count

Multiple rejected direct edges can expose the same canonical defect.

v4 therefore records optional `defect_group` metadata on known rejected
real-project cases. This is benchmark metadata only; it does not change the
generic scorer or Core model.

Current defect groups:

- `NAPMS-MATERIALIZATION-NONDEPLOYABLE-LOSS`;
- `NAPMS-REQUEST-AUTHORITY-SCOPE-DRIFT`.

The 4 rejected cases therefore represent only 2 known root defects.

Case-level recall remains useful for measuring whether an evaluator detects each
observable contradiction. It must not be reported as a count or estimate of
independent project defects.

## Request-authority localization triangle

The NAPMS authority defect was expanded into a local consistency network.

Accepted truth:

```text
Product Requirement
  access.request authority = source scope only
          |
          +--------------------------+
          |                          |
          v                          v
System Rules                    HTTP Contract
  source only                     source only
          \                        /
           \                      /
            X Security Architecture
              source + destination
```

The direct cases are:

1. Product Requirement -> Security Architecture: REJECTED.
2. System Rules -> Security Architecture: REJECTED.
3. Security Architecture -> HTTP Contract: REJECTED.
4. Product Requirement -> HTTP Contract: ACCEPTED.
5. System Rules -> HTTP Contract: ACCEPTED.

This is stronger evidence than one isolated mismatch. The consistent Requirement,
System Rules and HTTP surfaces triangulate the inconsistent canonical artifact
to Security Architecture.

The experiment does not add a generic graph-based root-cause engine. The corpus
records enough direct evidence to support human/expert localization; automation
would require repeated evidence of a reusable need.

## Deterministic result

The expanded deterministic scenario passes:

- expert baseline: TP=4, TN=12, FN=0, FP=0;
- an evaluator that accepts every canonical drift is exposed with FN=4.

This proves the Scenario Suite can score the expanded real-project benchmark
without changing scorer semantics.

## Live evaluator evidence

Workflow run: `36514615427`.

Corpus fingerprint:

`LCCORPUS-a37e0ff9a4fb5e1aff467f8c02eb0ca14281834ee9213798c2496cb5acc92664`.

### Attempt 1

Run 1 completed with a valid response.

Resolved model: `gpt-6-luna`.

Result:

- TP=3;
- TN=12;
- FN=1;
- FP=0;
- accuracy=`0.9375`;
- detection recall=`0.75`;
- false-positive rate=`0.0`.

Mutation-class result:

- `real-project-constraint-drift`: 3/3 correct;
- `real-project-partial-loss`: 0/1 correct;
- `real-project-valid-constraint`: 1/1 correct;
- `real-project-valid-realization`: 11/11 correct.

The sole miss remained:

`napms-missing-address-requirement-to-journey`

Expected `REJECTED`, actual `ACCEPTED`.

All three observable edges of
`NAPMS-REQUEST-AUTHORITY-SCOPE-DRIFT` were rejected correctly. Both valid
Requirement/System-Rules -> HTTP controls were accepted. The live result
therefore reproduces the manual localization pattern and identifies Security
Architecture as the inconsistent middle artifact.

Run 2 returned an unknown request-bound case id. Harness rejected it as
`INVALID`; no score was accepted.

Artifact: `11009509124`.

Digest:
`sha256:323b1f40b9e07df50ea2e042f60914e7272804b10987c67d2785813d1039a582`.

### Attempts 2 and 3

Unchanged reruns did not reach semantic scoring:

- attempt 2: provider envelope omitted/violated required `version: 1`;
- attempt 3: provider output was not strict JSON.

Harness returned `INCOMPLETE` in both cases.

Artifacts:

- attempt 2: `11010444096`,
  `sha256:da43313abf5838186f7fd68bb707b5f6b15882ece428056c163ada97555abaf4`;
- attempt 3: `11010860490`,
  `sha256:9dc2846041642e09d4763d508521989c904fef567d1857a7f1ed759e62f4e84e`.

No v4 repeat-stability claim is made because only one attempt produced a
scorable run.

## Interpretation

Scaling the corpus strengthened the earlier result.

The evaluator now shows a clear error profile on the audited real-project set:

- explicit contradiction/constraint drift: detected;
- valid consumed-atom realization: accepted;
- subtle partial semantic omission inside an otherwise strong realization:
  missed.

This is more informative than a single aggregate accuracy number.

The expanded NAPMS triangle also demonstrates that Capability-edge tests can
support root-cause localization by comparing several independently owned
canonical surfaces. The semantic authority still comes from expert-reviewed
canonical knowledge; the evaluator remains a calibrated detector.

Provider output reliability remains a separate operational limitation. Two of
three v4 attempts failed before semantic scoring, reinforcing the existing
decision not to use the live provider path as a deterministic CI gate.

## Consequence

No Core, scorer, provider registry, orchestration framework or root-cause engine
is justified by this expansion.

The next omission-focused step was executed in
`docs/research/verification-oracle-partial-loss-audit-v0.md`.

It found four independent NAPMS Verification Design defects where a scenario
declares a requirement in `verifies` but its observable `expect` oracle loses
a mandatory semantic atom. A focused live probe showed 50% omission detection
recall per run, zero false positives on four positive controls, and unstable
verdicts on two omission cases even though both runs resolved to the same model.

This establishes that structural requirement traceability is not semantic
verification coverage and that evaluator performance must be interpreted by
defect class.
