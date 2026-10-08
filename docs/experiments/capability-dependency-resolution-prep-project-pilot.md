# Capability Dependency Resolution — read-only PREP project pilot

Date: 2026-10-08
State: **Ready for operator-triggered GitHub Copilot run; no real PREP model predictions yet**
Primary branch: `experiment/capability-dependency-resolution-v1`; PR #220 remains Draft.
Disposable execution branch: `experiment/cdr-live-run`.
Source project: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
(source was the `mvp-vertical-slice` head at selection time).
No changes to PREP or `harness/main`.

## Why this is materially different from CDR-01..06, HLD and ADV

Earlier evaluations used a manually bounded semantic provider catalog and
hand-authored target obligations. This pilot uses the target **Capability
selection and accepted context headings** as operator inputs, but constructs
the candidate provider catalog from the *actual pinned PREP checkout* using:

- `.harness/core.yaml` to locate canonical, registered Capability providers;
- `.harness/semantic-baseline.yaml` to require a recorded semantic review
  revision for each selected Core Capability;
- `.harness/engineering-graph.yaml` to identify all valid production contracts
  and their owning Authorities (NOT to expose target `requires`);
- the accepted registered source files themselves for public semantic claims.

The generator `evals/project_discovery_snapshot.py` enforces a clean tracked
checkout and exact 40-character commit identity. An unregistered document, an
Engineering Graph-only future producer, or an unrevised Core provider is **not**
misrepresented as accepted provider knowledge.

### PREP target selection and semantic scope

From the accepted `MODEL-CONTEXT-MAP`:

1. `prep.preparation-information-model` (TACTICAL-DOMAIN-DESIGN),
   target scope `MC-01 Preparation Information`;
2. `prep.recorded-activity-history-model` (TACTICAL-DOMAIN-DESIGN),
   target scope `MC-02 Recorded Activity History` plus
   `TR-01 Preparation Information and Recorded Activity History`.

Both are real Engineering Graph productions, but neither has a canonical
accepted domain-model provider artifact registered in PREP Core yet. The
accepted candidates are the six registered, semantically reviewed capabilities
for Problem Evidence, User Needs, Product Intent, Product Capabilities,
Domain Strategy, and Model Context Strategy. Unlike historical PREP pilot
fixtures, their semantic surfaces are extracted from the pinned actual files.
A source may be relevant and yet **not** justify a direct edge.

## Execution separation

**Phase A, no oracle:** `evals.project_discovery_snapshot` generates
`generated-prep-discovery.yaml`; Scenario Suite invokes external Copilot
using `dependency.discovery.execute_process`. The evaluated model does not
receive the target graph's current `requires`, an expert baseline, expected
answer, or a canonical adoption authority. Result is labeled
`DISCOVERY_REQUIRES_REVIEW`, with `calibration_claim=NOT_APPLICABLE_NO_ORACLE`.

**Phase B, after the model is finished:** `evals.project_discovery_reconcile`
reads the same exact pinned Engineering Graph and compares the model's
`proposed_requires` to each target's existing `requires`. Its report shows
`KEEP`, `ADD` and `REMOVE_CANDIDATE`. Each difference is explicitly
`REVIEW_REQUIRED`, even if the source-reference preflight succeeds.

The Phase B tool independently rechecks source-reference assessments, binds
inputs/evaluation to the same Git commit, and rejects malformed or inconsistent
case identities. It does not mutate Core, Engineering Graph, accepted source
artifacts, Lifecycle, Project Publication, or Prep. Graph writeback remains
permanently disabled in this version.

**Important epistemic boundary:** `source-grounded-v1` verifies source
claim indices, statuses, and rationale presence. It does not prove semantic
entailment. The accepted source extraction is bounded to the configured
scopes and registered reviewed Core providers. Discovery cannot claim that
these constitute every imaginable upstream producer or future contract.

## Checks and execution

- Pure deterministic fake-provider/snapshot test:
  `python tests/test_dependency_resolution_project_snapshot.py`;
  included in the canonical Harness full gate.
- CI policy and full Harness gate passed at
  [GitHub Actions 37760224657](https://github.com/lehater/harness/actions/runs/37760224657)
  and [37760224648](https://github.com/lehater/harness/actions/runs/37760224648).
- A real project Copilot run must be triggered manually via the *existing*
  `live-calibration-copilot.yml` workflow on temporary
  `experiment/cdr-live-run`. Harness CI forbids PR-triggered external
  evaluator jobs; the connector cannot invoke `workflow_dispatch`.
- Outputs: `dependency-resolution-evidence.json`,
  `dependency-resolution-summary.json`,
  `dependency-resolution-reconciliation.json` and
  `generated-prep-discovery.yaml` in the Actions artifact
  `dependency-resolution-live-evidence`.

## Adoption decision

Do not merge the disposable execution branch, and do not change PREP graph
edges based on a model's proposal without semantic owner review. Independent
expert review of CDR-06 and project-level topology/publication consistency
remains necessary before enabling automatic graph writeback.
