# Real PREP project Dependency Resolution — first oracle-free run

Date: 2026-10-08
Harness execution branch: `experiment/cdr-live-run@96242099c9d236ca7d83c0ee411465a706282225`
Immutable PREP source: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Workflow: [GitHub Actions #37787728364](https://github.com/lehater/harness/actions/runs/37787728364)
Workflow status: **PASS**
Semantic status: `DISCOVERY_REQUIRES_REVIEW`, with **no oracle and no accuracy scoring**.
External evaluator: GitHub Copilot CLI 1.0.86, requested `auto`, reported `gpt-6-luna`.
Session: one invocation, no schema retries.
Agent independence: `UNVERIFIED`.
Graph writeback: **disabled**.

## Inputs and evaluation boundary

The source generator successfully checked out the exact PREP commit and
constructed two target cases with six Core-registered, baseline-reviewed
provider Capabilities each and three output obligations total.

- `SNAP-01`: `prep.preparation-information-model`, scoped from accepted MC-01.
- `SNAP-02`: `prep.recorded-activity-history-model`, scoped from accepted
  MC-02 and cross-context TR-01.

The input to the model excluded existing target `requires`; these were
read **only after** the model response for reconciliation. Provider claims
were source-extracted from real project artifacts.

Critically, the target **output-obligation scope was selected only from
MODEL-CONTEXT-STRATEGY headings**. The model also saw the same Strategy
document in the provider catalog, making that candidate particularly easy
to identify. Relevant accepted Product Capabilities were available as
candidate supplier claims, **but their obligation-level contribution was
not reconstructed in the target contract**. This is a restricted-scope
demonstration, not a complete capability dependency audit.

## Raw agent proposals and initial Phase B comparison

| Target | Proposed direct sources | Previously declared direct sources |
| --- | --- | --- |
| prep.preparation-information-model | prep.model-context-strategy | prep.model-context-strategy, prep.product-capabilities |
| prep.recorded-activity-history-model | prep.model-context-strategy | prep.model-context-strategy, prep.product-capabilities |

Both predictions:
- `status=RESOLVED`;
- cite many accepted `model-context-strategy` claims with valid
  `claim_index` and individual rationales;
- have `unresolved_obligations=[]`;
- pass structural grounding checks with
  `semantic_entailment_verified=false` and no graph writeback.

The **initial** run's Phase B output listed `prep.product-capabilities`
in `REMOVE_CANDIDATE` for both targets, along with a mandatory
`REVIEW_REQUIRED` decision. **Do not interpret this as an established
redundant edge.** Given the incomplete target obligations, the model's
failure to select a provider is non-evidence of that provider's
unnecessariness.

## Safety correction after the real run

The Harness experimental generator now marks actual project discovery
with `target_obligation_coverage.status=PARTIAL_BY_CONSTRUCTION`, explicitly
not asserting complete upstream obligation coverage.

The post-run Phase B reconciler now:
- blocks all removal-candidate conclusions under this partial-source
  discovery mode;
- returns `REMOVE_CANDIDATE=[]`;
- places omitted already-declared edges under
  `UNASSESSED_EXISTING_EDGES`;
- supplies `removal_assessment=BLOCKED_INCOMPLETE_TARGET_OBLIGATIONS`;
- requires exact commit identity and rechecks the model's citation
  validity, as before.

The corrected expected interpretation of this first PREP run is therefore:

| Target | KEEP | ADD | UNASSESSED_EXISTING_EDGES | REMOVE_CANDIDATE |
| --- | --- | --- | --- | --- |
| prep.preparation-information-model | prep.model-context-strategy | none | prep.product-capabilities | **none** |
| prep.recorded-activity-history-model | prep.model-context-strategy | none | prep.product-capabilities | **none** |

The corrected report is an **interpretation under the new safeguard**, not
a claim that the already-completed GitHub Actions run contained the new
field; that original evidence is immutable.

## Architectural findings

1. The pipeline can read a pinned real project, construct source-backed
   provider candidates, perform a blind agent request, and reconcile
   after the response without editing the project.
2. Selecting only one upstream source for target obligations biases
   discovery toward that source. Do not claim full upstream discovery.
3. The Product Requirements source contributes meaningful constraints to
   tactical domain models. Whether each is a direct prerequisite requires
   an independent source-aware derivation, not a superficial graph
   reduction algorithm.
4. The strong claim that all dependencies have been found, or that omitted
   `requires` are redundant, remains unsupported.
5. Source references, request binding and provider-status checks are
   structural evidence, not semantic entailment verification.

## Next gate

Design an obligation-coverage audit that sources target production
constraints from **all relevant accepted upstream authorities**, not only
selected Model Context headings. An explicit completeness decision must
precede any removal classification. Retain the existing PREP
`prep.product-capabilities` edges pending that work.

Do not merge the execution branch, enable autonomous routing or mutate
PREP. This is a read-only research artifact.
