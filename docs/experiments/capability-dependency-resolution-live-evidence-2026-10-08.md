# Capability Dependency Resolution — first real Copilot evaluation

Date: 2026-10-08
Repository: `lehater/harness`
Implementation: `experiment/capability-dependency-resolution-v1` (draft PR #220)
Execution branch: `experiment/cdr-live-run`
Source of PREP case hypotheses: `lehater/prep@mvp-vertical-slice`
Status: **provider execution demonstrated; semantic calibration NOT established**

## Evidence

Workflow: `.github/workflows/live-calibration-copilot.yml` (manual dispatch, execution branch only).
Provider: GitHub Copilot CLI 1.0.86, requested model `auto`; observed resolved model on both successful attempts: `gpt-6-luna`.
Evaluation environment reported fresh Copilot home, no custom instructions, disabled built-in MCPs, and no available tools. Independence is explicitly `UNVERIFIED`.

- [Run 37754939856, attempt 1](https://github.com/lehater/harness/actions/runs/37754939856/attempts/1): workflow PASS, evaluation `DIFFERS_OR_INCOMPLETE`.
- [Run 37754939856, attempt 2](https://github.com/lehater/harness/actions/runs/37754939856/attempts/2): same results at dependency-edge level; workflow PASS, evaluation `DIFFERS_OR_INCOMPLETE`.
- The baseline deterministic Harness full gate passed after the provider adapter fixes at [run 37754637486](https://github.com/lehater/harness/actions/runs/37754637486).

These were real provider executions, not hand-authored prediction fixtures. The independent truth of the labels is not established; the oracle is AUTHOR_DRAFT or PROJECT_HYPOTHESIS throughout.

## Calibration comparison against the draft oracle

| Case | Run 1 | Run 2 | Structural interpretation |
| --- | --- | --- | --- |
| CDR-01 | exact match | exact match | Missing direct edge proposed |
| CDR-02 | exact match | exact match | Unneeded baseline edge excluded |
| CDR-03 | exact match | exact match | Direct edge retained despite a transitive path |
| CDR-04 | exact match | exact match | Missing owner/provider classified UNRESOLVED |
| CDR-05 | exact match | exact match | PREP Preparation Information: expected suppliers |
| CDR-06 | differing direct-need pairs | differing direct-need pairs | PREP Recorded Activity History: expected suppliers |

Both attempts produced 11/11 matching required direct dependency edges, with 0 extra and 0 missing edges relative to the draft oracle (precision=1.0, recall=1.0 **on this particular draft corpus only**). All six statuses and unresolved-obligation sets matched. Five of six cases exactly matched all draft direct-need pairs.

CDR-06 additional direct-need pairs:

- Run 1: `preserve-temporal-context -> prep.model-context-strategy` and `preserve-historical-meaning -> prep.model-context-strategy`.
- Run 2: `preserve-temporal-context -> prep.model-context-strategy` only.

Neither run proposed a third direct provider, so these differences are **justification-granularity differences**, not proposed topology differences.

## Source-content audit of CDR-06

The accepted PREP Model Context Strategy, `docs/architecture/model-context-map.md`, explicitly states under MC-02:
- temporal context belongs to Recorded Activity History;
- historical context must suffice to keep records understandable after related information changes or is removed.

The same document's TR-01 contract further requires sufficient historical context when current referenced information changes or is removed.

PREP Product Capabilities independently expresses time and preservation obligations in `REQ-CAP-PRESERVE-TIME` and `REQ-CAP-PRESERVE-HISTORY-CONTEXT`.

Therefore, both source authorities can plausibly contribute directly to these *different dimensions* of a tactical output obligation. The existing draft oracle's one-provider-per-obligation mapping may be too restrictive; **do not change the oracle merely to match the model**. Ask an independent subject expert to assess whether both mappings are semantically necessary direct consumption, and whether the output obligations should be decomposed further.

The current CDR-06 provider_catalog's public semantic surface summarizes MC-02 and TR-01 without exposing all relevant accepted statements about temporal and historical-context ownership. A future fixture should use an explicitly versioned, traceable public contract, not a selectively compressed paraphrase. Also bind PREP to an immutable commit SHA rather than a mutable branch ref.

## Limits of the evidence

- Six seeded cases are insufficient to claim generic semantic dependency resolution quality.
- CDR-04's `known_uncertainties` hints at the absence of an accepted consent provider; test how the model handles unhinted uncertainty in a hold-out corpus.
- The two initial provider runs report scoring differences and provenance but did not persist complete unmodified model prediction rows. A subsequent process-driver change records model result rows and their validated case-bound projection for future runs; it does not retroactively recover the two initial responses. If the model supplies a rationale, the new field retains it without inventing one.
- Copilot automatic model routing and `UNVERIFIED` independence limit reproducibility claims.
- A successful Scenario Suite run means transport and structural assertions succeeded, **not** that semantic labels were independently verified.
- No canonical graph mutation or PREP repository change occurred.

## Follow-up acceptance gates

1. Expert review of expected direct-need pairs and whether a single obligation can materially consume knowledge from more than one provider.
2. A hold-out set featuring unseen domains, incomplete public contracts, wrong owner, overbroad/narrow semantic claims, and unhinted missing knowledge.
3. Persist redacted raw prediction rows plus provenance, fingerprints, and stable source SHA for audit.
4. Only after those steps consider enabling an agent route. Graph topology mutation remains explicitly out of scope until project snapshot consistency is solved.
