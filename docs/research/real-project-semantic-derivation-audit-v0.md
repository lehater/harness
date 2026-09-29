# Real-project semantic derivation audit v0

Status: completed experiment; real canonical derivation defects found and live evaluator limits measured.

## Question

Can Harness semantic-derivation testing move beyond synthetic mutations and
detect design-quality defects that already exist between accepted upstream and
downstream engineering knowledge in real projects?

The experiment uses the same pinned external project snapshots already used by
Harness derivation-coverage validation:

- Prep: `lehater/prep@b3ec3b0fec0d8ba29f2ca66867737e8838332592`;
- NAPMS: `lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

No external project was modified.

## Real-project oracle rule

The first live attempt exposed a test-construction error in the experiment
itself.

A downstream Capability is not required to repeat the complete upstream
artifact. Semantic judgement must compare only the upstream semantic atoms that
the concrete downstream ProductionContract consumes, plus enough downstream
atoms to evaluate their realization.

Therefore the real-project judgement unit is:

```text
upstream Capability
  -> consumed semantic atom(s)
  -> concrete downstream ProductionContract
  -> linked downstream semantic atom(s)
  -> semantic relation
  -> judgement
```

Unrelated upstream semantics are excluded or dispositioned. Treating an entire
upstream paragraph as a required downstream restatement produces false
positives and violates the existing Capability Derivation Testing model.

## Corpus evolution

### v1 — coarse excerpts

`real-project-corpus-v1.yaml` used eight real project transitions but bundled
some semantics not owned by the selected downstream capability.

Live workflow run `36512811263` exposed this immediately:

- the real NAPMS request-authority contradiction was REJECTED in both runs;
- several valid Prep/NAPMS transitions were also REJECTED;
- one Prep import case changed verdict between runs.

The failures were useful evidence that real-project cases need ProductionContract-relative
semantic slicing rather than whole-artifact comparison.

Artifact: `11010241621`,
digest `sha256:4212fb73dc92f2e8d4009002865f5a0a2122ac3509099fc7d5a0ac4bb4f589fc`.

### v2 — consumed semantic atoms

`real-project-corpus-v2.yaml` narrowed every case to semantics actually
consumed by the downstream responsibility.

Live workflow run `36513060371` produced two complete `gpt-6-luna` runs.
Both had the same verdict vector:

- TP=1, TN=6, FN=0, FP=1;
- accuracy `0.875`;
- detection recall `1.0`;
- false-positive rate `1/7`;
- stability: `STABLE`, no unstable cases.

Every Prep case was accepted and the NAPMS request-authority contradiction was
rejected. The remaining disagreement was
`napms-missing-address-requirement-to-journey`.

Artifact: `11009252320`,
digest `sha256:a0ec70b01f3a29e76f4bd5bd3ba94a0346ed8d67e346f7b02eadc030ea769134`.

## Canonical audit of the remaining disagreement

The remaining v2 mismatch was audited against canonical NAPMS ownership rather
than relabelled to match the evaluator.

Product requirement `REQ-EXP-005` requires a missing-address policy row to:

- remain represented;
- retain Resource identity/name and traffic semantics;
- expose the missing address;
- remain technically INCOMPLETE;
- not be represented as a deployable permit;
- not make the whole export globally UNRESOLVED.

`FIRST-MVP-JOURNEY` is the canonical provider of both
`engineering.application.journey` and
`engineering.application.materialization-semantics`. It preserves the row,
Resource identity/name, null address, non-UNRESOLVED behavior and exact traffic
semantics, but it does not state the required non-deployable meaning of an
INCOMPLETE row.

The semantic is not generally absent from NAPMS. Neighboring canonical
artifacts explicitly retain it:

- policy-export task model: an INCOMPLETE row is not a deployable firewall permit;
- policy-export human journey: INCOMPLETE rows do not pretend to be deployable permits;
- quality requirements: an INCOMPLETE row cannot be represented as a deployable tuple.

Because `FIRST-MVP-JOURNEY` owns the application materialization semantic
surface, this omission is classified as real semantic partial loss rather than
an evaluator false positive.

## Two observed NAPMS derivation defects

### 1. Product requirement -> application materialization

Source requirement:

> missing-address materialization is INCOMPLETE and not a deployable permit.

Downstream canonical application materialization preserves INCOMPLETE row
visibility but drops the non-deployable constraint.

Classification: `real-project-partial-loss`.

### 2. System architecture rules -> security architecture

System Rules require `access.request` authority only for the source Resource
scope and explicitly state that destination authority is not request-admission
authority.

Security Architecture derives access-request scopes from both source and
destination Resource AuthorityScopeRefs and requires a matching grant for every
required scope.

Classification: `real-project-constraint-drift`.

This changes observable admission behavior and is a direct contradiction, not a
synthetic mutation.

## v3 — audited real-project oracle

`real-project-corpus-v3.yaml` contains eight real canonical transitions:

- six accepted derivations;
- two observed NAPMS defects;
- no synthetic negative mutation.

The deterministic Scenario Suite treats both drifts as defects and proves that
an evaluator which accepts them produces two explicit false negatives.

Two initial live attempts of v3 failed before semantic scoring because Copilot
returned malformed structured output. Harness produced `INCOMPLETE` and no
score, preserving fail-closed behavior.

A subsequent unchanged rerun, workflow `36513360751` attempt 3, produced two
complete runs:

Run 1:

- run id: `GH-36513360751-3-1`;
- resolved model: `gpt-6-luna`;
- TP=1, TN=6, FN=1, FP=0;
- accuracy `0.875`;
- detection recall `0.5`;
- false-positive rate `0.0`.

Run 2:

- run id: `GH-36513360751-3-2`;
- resolved model: `mai-code-1.1-flash`;
- TP=1, TN=6, FN=1, FP=0;
- accuracy `0.875`;
- detection recall `0.5`;
- false-positive rate `0.0`.

Stability:

```yaml
status: STABLE
unstable_cases: []
```

Artifact: `11010198158`,
digest `sha256:695796367ce713c0f201ec810dbaad78a5b8f7b1cbc23bb557f0ac8b683ea7ac`.

Both model routes detected the source-vs-destination authority contradiction.
Both consistently missed the application-materialization partial loss and
accepted that case.

## Interpretation

The experiment answers the main research question positively, with an important
limit.

Harness can apply semantic derivation testing to real Capability transitions and
can expose real design defects already present in accepted project knowledge.
The NAPMS request-authority contradiction is a concrete example detected by the
blinded live evaluator.

At the same time, the live evaluator is not a complete semantic oracle. Two
different resolved model routes consistently missed the subtler omission of the
non-deployable meaning from application materialization. Stable agreement is
therefore not equivalent to semantic correctness.

The useful assurance model is:

```text
canonical upstream knowledge
        |
        v
select consumed semantic atoms
        |
        v
downstream ProductionContract-relative target atoms
        |
        v
blinded semantic judgement
        |
        +-- disagreement with expert oracle
        |      -> audit case boundary / ownership / wording first
        |
        +-- evaluator detects canonical drift
        |      -> real defect evidence
        |
        +-- evaluator misses audited canonical drift
               -> evaluator false negative / calibration evidence
```

This preserves three independent truths:

1. project canonical knowledge determines the design semantics;
2. expert-reviewed real-project cases calibrate what counts as known-good or
   known-bad derivation;
3. the live evaluator is a measured detector, not the authority that defines
   correctness.

## Consequence for Harness

No new Core entity, scorer, orchestration framework or provider abstraction is
required.

The next scale step, if pursued, is corpus work rather than framework work:
extract more expert-reviewed consumed-atom pairs from real Capability edges and
include naturally occurring defects when found. The real-project corpus should
remain a benchmark/evidence set, not an estimate of universal production error
rates.
