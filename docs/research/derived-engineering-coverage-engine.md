# Research — Derived Engineering Coverage Engine

Status: research only. Not canonical.

## Decision

Engineering Coverage must be computed from canonical project knowledge plus a small project-specific applicability overlay.

The generated coverage YAML/Markdown/dashboard is disposable and must never become an input source of truth.

Pipeline:

```text
Canonical project knowledge
  + reusable Concern Catalog
  + reusable concern/evidence mappings
  + minimal project applicability/attention overlay
        ↓
Derived Coverage Engine
        ├── complete machine projection
        ├── remaining-work projection
        ├── human coverage dashboard
        └── provenance/navigation views
```

## Canonical inputs

Project truth remains in existing semantic owners:
- requirements and accepted decisions;
- Engineering Graph / project Harness graph;
- Capabilities and Authorities;
- canonical artifacts and dependency graph;
- Questions;
- lifecycle/staleness state;
- explicit applicability/deferral decisions.

The coverage overlay is canonical only for facts that cannot safely be inferred, for example:
- a concern is explicitly NOT_APPLICABLE for this scope;
- a concern is explicitly required/activated for this scope;
- a project-specific obligation interpretation;
- a deferral with owner and reopen condition.

It must not duplicate artifact paths, providers or coverage states that Harness can derive.

## Reusable Harness input

`concern-evidence-mapping-v1.yaml` maps concern ids to semantic evidence selectors:
- CapabilityId patterns;
- knowledge/artifact kinds;
- rarely, stable artifact roles/ids.

A mapping means "this knowledge is relevant evidence for this concern".

It does **not** mean:
- the concern applies to every project;
- one matching artifact proves every sub-concern;
- a file name proves coverage.

## Derived state algorithm

For each semantic leaf:

1. Apply explicit project applicability/deferral decision if present.
2. Resolve generic concern mapping against project artifacts/capabilities.
3. Resolve unresolved Questions/blockers.
4. Resolve project activation/required state.
5. Resolve lifecycle freshness when available.
6. Produce state + evidence + provenance.

Current experiment:

- matching semantic evidence -> COVERED;
- required + unresolved blocker -> BLOCKED;
- required + no evidence -> MISSING;
- explicit N/A -> NOT_APPLICABLE;
- explicit deferral -> DEFERRED;
- evidence proven stale -> STALE;
- otherwise -> UNASSESSED.

This is intentionally conservative.

## UNASSESSED versus remaining work

This distinction is essential.

The universal catalog can contain hundreds of possible concerns over time. A concern being UNASSESSED does not itself create project work.

The derived row therefore carries an orthogonal flag:

```yaml
attention_required: true|false
```

The remaining-work projection contains:
- MISSING;
- BLOCKED;
- STALE;
- UNASSESSED only when explicitly activated/required.

Therefore the catalog is a recall space, not a backlog generator.

## Example project overlay

```yaml
required:
  - reliability.recovery
  - data.classification

decisions:
  - concern: quality.performance.latency
    state: NOT_APPLICABLE
    rationale: Numeric latency target is not required for first MVP.
    evidence: [MVP-QUALITY-TARGETS]
```

No artifact paths or COVERED rows are repeated here.

## Provenance

A derived COVERED row records matched evidence:

```yaml
concern: security.threat-analysis
state: COVERED
derivation: AUTO
evidence:
  - artifact: THREAT-MODEL
    authority: SECURITY-ANALYSIS
    path: docs/architecture/mvp-threat-model.yaml
    kind: threat-model
    capabilities:
      - engineering.security.threat-analysis
```

A later graph-aware iteration should additionally derive:
- upstream causes/prerequisites;
- downstream Consumers;
- verification evidence;
- lifecycle baseline/freshness.

## Pilot overlays

NAPMS and Nutrition research branches now contain small overlays instead of using the full hand-authored refined map as future truth.

The large v1 maps remain useful **research oracle/reference fixtures** for comparing the derived engine, but they should not survive as canonical project inputs.

## Current limitation

The generic evidence registry still contains heuristic capability substring/kind mappings. These are acceptable for the experiment but are too weak for canonicalization.

Next refinement should replace string heuristics with stable semantic mapping declarations:
- exact CapabilityId;
- exact semantic claims declared by a production contract;
- declared artifact kind as candidate evidence only;
- optional project adapter mapping.

## Success criterion for the next experiment

For NAPMS and Nutrition:

1. derive the map from actual project knowledge + overlay;
2. compare against the manually reviewed v1 research map;
3. classify every mismatch:
   - missing generic mapping;
   - missing project applicability decision;
   - false-positive mapping;
   - missing canonical project knowledge;
4. measure:
   - automatic derived coverage;
   - explicit mapping dependence;
   - human applicability dependence;
5. keep only the minimal overlay required to preserve semantic correctness.

If this converges, the full project coverage-map YAML should be removed from the architecture and treated only as generated output.


## Proof versus candidate evidence

The experiment now separates two roles:

- **proof evidence** — exact semantic evidence that is sufficient to derive `COVERED`, currently represented by exact concern-specific CapabilityIds;
- **candidate evidence** — artifact kinds, paths, broad capabilities or substring matches that help navigation and human/research review but are not sufficient to close a concern.

Therefore an activated concern with candidate evidence but no proof remains `UNASSESSED`, not `COVERED`.

This exposes an architectural requirement for Harness: if a concern must be checked algorithmically, the canonical knowledge model needs a semantic claim fine-grained enough to prove that concern. A coarse capability such as `engineering.operability.observability` cannot safely prove logging, metrics, tracing and health independently.


## Semantic-claim boundary

Coverage proof must not reuse Engineering Graph `knowledge_kind`.

- `knowledge_kind` is the existing execution-layer classification used for agent/skill routing.
- `semantic_claims[]` is a proposed research-only production-contract classification used for Coverage proof.

A capability may have one broad execution kind and several fine-grained semantic claims. The claims do not state that a concern is currently COVERED; they state what accepted semantic knowledge the capability is capable of proving once its canonical realization is valid.
