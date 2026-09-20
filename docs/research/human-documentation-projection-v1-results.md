# Human Documentation Projection v1 — prototype results

Status: research evidence only.

## Branches and prototypes

Harness:
- research contract: `research/human-documentation-projection-v1`;
- compiler experiment: `experiment/human-projection-compiler-v1`;
- draft PRs: #49 and #50.

Nutrition Management:
- research branch: `research/human-documentation-projection-v1`;
- draft PR: #37.

NAPMS:
- research branch: `research/human-documentation-projection-v1`;
- draft PR: #161.

No result from this experiment is merged to any project main branch.

## Prototype implemented in Harness

The experimental `human_projection.py` now proves these layers can be kept separate:

1. **scope compiler**
   - selected Engineering Graph Consumer;
   - recursive Capability closure;
   - resolved canonical provider artifacts;
   - Core artifact dependency closure;
   - target state;
   - unresolved capabilities;
   - blocking Questions;
   - Harness/project baseline metadata;
   - stable manifest digest.

2. **presentation recipe**
   - project-owned document and section grouping;
   - source selectors by CanonicalArtifact, CapabilityId or Authority;
   - validation that selected sources are within explicit projection scope.

3. **projection IR**
   - document/section structure;
   - narrative claims;
   - explicit source artifact references per claim;
   - manifest-digest binding;
   - rejection of claims that cite artifacts outside the section's allowed source set.

4. **package materialization**
   - REVIEW mode: README + manifest + plan + projection IR + human documents;
   - HANDOFF mode: REVIEW plus exact canonical source snapshot.

Harness acceptance validates:
- complete target;
- incomplete target;
- invalid recipe source;
- invalid narrative source reference;
- missing planned section;
- explicit composite scope;
- REVIEW package;
- HANDOFF source snapshot.

The dedicated Human Projection research workflow is green.

## NAPMS result

NAPMS is a strong assembly/handoff validation case because it has:
- a project canonical graph;
- a Harness projection;
- a canonical Engineering Graph;
- mixed source representations including YAML, OpenAPI and Structurizr.

Research result: PASS.

The generic Harness prototype can:
- derive the exact BACKEND-IMPLEMENTATION closure;
- validate a project-owned topic recipe;
- materialize REVIEW and HANDOFF packages;
- copy only manifest-selected canonical source artifacts;
- leave `docs/canonical-graph.yaml` itself outside the semantic source snapshot because it is routing metadata rather than a CanonicalArtifact provider;
- evaluate FRONTEND-IMPLEMENTATION independently.

The frontend result remains correctly incomplete:
- target state: READY;
- first CREATE frontier includes `engineering.frontend.human-interface`.

Human Projection does not fill that gap.

### Consequence

The NAPMS-local `generate_human_context_package.py` algorithm is no longer needed as a unique design.

Its valuable behavior can be generalized into Harness:
- exact Consumer closure;
- manifest;
- optional source snapshot;
- package output.

NAPMS-specific presentation grouping can remain a small recipe.

## Nutrition result

Nutrition is a strong narrative/information-architecture validation case because its existing generated docs are already substantially more readable than the NAPMS raw-source wrapper package.

Research result: PASS after research-only graph corrections.

The prototype can express the current human-document information architecture as:
- System Overview;
- Domain and Data;
- Implementation Guide;
- Verification and Readiness;
- separate Frontend Design Guide for FRONTEND-IMPLEMENTATION.

The existing generated documents remain quality benchmarks only; they are not inputs to the projection compiler.

## Nutrition falsification findings

The prototype found three issues that ordinary human-document generation had hidden.

### 1. Two dead public capabilities

The current project graph exposes:
- `nutrition-management.food-knowledge.bls-v4.source-structure`;
- `nutrition-management.food-knowledge.bls-v4.normalization-order`.

Neither has a downstream consumer and neither is declared terminal.

Search found no use outside the Core/Engineering Graph declarations.

Research interpretation:
these are internal semantics of their owning accepted artifacts, not justified public CapabilityIds.

They were removed only in the Nutrition research branch so the project could be evaluated under the current unified Harness liveness rule.

This is not yet a main-branch migration decision.

### 2. Stale canonical artifact path / duplicate ownership

The Core graph registered:
- `COMPONENT-DESIGN` -> `docs/implementation/component-design.md`, but that file no longer exists;
- `REDESIGN-REVALIDATION` -> `docs/redesign/component-design.md` under PRODUCT, even though that file is the current accepted Component Design.

Repository documentation identifies `docs/redesign/component-design.md` as the current backend pre-code baseline.

The research branch therefore:
- removes the stale `REDESIGN-REVALIDATION` registration;
- maps COMPONENT-DESIGN to the existing accepted file.

This was discovered specifically because HANDOFF mode requires every selected canonical source path to exist.

### 3. Existing human docs exceed IMPLEMENTATION closure

Nutrition's existing `domain-and-data.md` cites `NUTRIENT-EVIDENCE-SEMANTICS`.

That artifact is accepted project knowledge but is not inside the current `IMPLEMENTATION` Consumer closure.

The old manually assembled human docs therefore mix:
- exact implementation handoff;
- broader project overview/context.

The projection recipe correctly rejected the out-of-scope source instead of silently including it.

## Refined scope model

One projection scope is not enough for all documentation use cases.

### Exact handoff

For coding/implementation handoff:

```
scope = selected Consumer closure
```

No extra canonical knowledge is silently included.

This makes the package useful as an exact contract for what implementation may rely on.

### Project overview / architecture review

A broader human overview may use:

```
scope = selected Consumer closure
      + explicitly named additional CapabilityIds
```

The prototype now supports explicit extra capabilities.

Rules:
- extras must be real Engineering Graph capabilities;
- normal provider/ownership resolution applies;
- extras are recorded in the manifest;
- extras do not change Consumer target state/readiness;
- presentation recipe still cannot escape the resulting explicit scope.

Nutrition research uses this mechanism to include nutrient-evidence semantics in the broader backend human overview without pretending it is an IMPLEMENTATION prerequisite.

## Stronger conclusion about package purpose

The experiments show that the phrase "documentation package" hides at least two materially different products:

1. **contract package / handoff**
   - exact;
   - Consumer-scoped;
   - source snapshot useful;
   - completeness/readiness visible;
   - intended to constrain downstream work.

2. **explanatory documentation / overview**
   - may intentionally include additional accepted context;
   - topic-oriented;
   - optimized for human understanding;
   - still source-bounded and explicit.

A single implicit "all relevant docs" algorithm is rejected.

## Source snapshot finding

HANDOFF source snapshot is more valuable than originally expected.

It is not only an export convenience. It also validates that:
- every selected provider path still exists;
- Core has no stale file registrations;
- the handoff can be reviewed independently of repository navigation;
- generated human prose can always be checked against the exact source baseline.

Source snapshots should remain optional for REVIEW mode and required/recommended for HANDOFF mode.

## Narrative IR finding

A free-form generated Markdown file is too weak as the only projection evidence.

The prototype projection IR gives a useful intermediate contract:

```
document
  section
    claim
      text
      sources: [CanonicalArtifact ids]
```

Validation can prove:
- claim sources are in section scope;
- section sources are in projection scope;
- projection scope comes from accepted Harness providers;
- IR matches the exact manifest digest.

This does not prove the prose is a perfect paraphrase. Semantic faithfulness remains an agent-review/verification problem.

However it prevents several structural failures:
- invented source paths;
- accidental use of unrelated canonical knowledge;
- silent scope widening;
- stale projection reuse after manifest changes.

## Determinism result

The experiments support the research distinction:

### Must be deterministic
- Consumer/capability projection scope;
- provider resolution;
- canonical source closure;
- manifest;
- recipe-to-section source plan;
- source snapshot;
- generated file structure;
- typed/source-native renderer output where such a renderer exists.

### Need not be byte-identical
- high-quality source-bounded narrative prose.

A regenerated narrative may use different wording while remaining a valid projection if:
- it satisfies the same section contract;
- all substantive claims cite allowed sources;
- no Question/conflict is silently resolved;
- semantic review finds no unsupported claim.

## Remaining research gap

The infrastructure/contract hypothesis has passed both project pilots.

The major untested part is now **narrative quality and semantic faithfulness**.

The next experiment should:

1. take Nutrition's current high-quality generated documents as a benchmark;
2. give an agent only the compiled manifest, section plan and allowed canonical sources;
3. have the agent produce projection IR + Markdown without reading the old generated document;
4. compare coverage, readability and unsupported-claim rate against the existing benchmark;
5. repeat on NAPMS, where no equivalent high-quality narrative package currently exists;
6. test regeneration after one controlled canonical-source change;
7. verify that stale manifest/IR is rejected and regenerated narrative reflects only accepted changes.

Only after this should the narrative skill/contract be considered ready for canonicalization.

## Current recommendation

Continue the experiment.

The evidence is now strong enough to keep the following design:

```
Engineering Graph + Core/project projection
          ↓
explicit projection scope
          ↓
deterministic manifest
          ↓
project presentation recipe
          ↓
section source plan
          ↓
source-bounded projection IR
          ↓
REVIEW or HANDOFF package
```

Do not yet canonicalize it.

The next decision gate is narrative generation quality, not another Core/schema redesign.

## Follow-up: source-bound freshness

The first prototype manifest bound scope/topology but not canonical file contents.

That was insufficient: a canonical source file could change while its graph/provider identity remained stable, leaving an older narrative IR structurally valid.

The compiler experiment now optionally binds every selected source to a SHA-256 digest taken from the project checkout.

The manifest digest therefore covers:
- Consumer/composite scope;
- provider/source closure;
- Harness/project baseline metadata;
- canonical source content hashes.

Validation now detects:
- missing selected source path;
- changed source content;
- stale manifest/IR after canonical source modification.

Harness acceptance includes a controlled source mutation and rejects the old manifest as stale.

Both Nutrition and NAPMS research pilots now compile manifests from real source files with content hashes and pass.

### Consequence

For repository-backed REVIEW/HANDOFF packages, source-content binding should be part of the projection manifest.

A project commit SHA is useful baseline metadata but is not by itself enough for dirty working trees or partial/exported source sets.

The canonical source hashes are the precise projection freshness boundary.

## Follow-up: narrative generation

A research-only agent skill, `human-documentation-projection`, was prototyped.

Its constraints are:
- section-specific read boundary from the compiled plan;
- projection IR before Markdown;
- every substantive claim carries one or more CanonicalArtifact IDs;
- no reading of old generated documentation as semantic input during controlled generation;
- unresolved Questions/gaps are preserved;
- unsupported or out-of-scope claims are rejected structurally.

NAPMS now contains a research-only source-bounded narrative IR for the backend documentation recipe.

It covers:
- product/discovery/application journey;
- strategic/use-case/tactical domain design;
- architecture/security/interface/data;
- quality/threat/operability;
- implementation and verification.

The IR was produced from canonical NAPMS sources and passed:
- recipe scope validation;
- claim source validation;
- real source hash binding;
- REVIEW materialization;
- HANDOFF materialization.

This demonstrates that the NAPMS package can become a genuine topic-oriented human document set rather than raw YAML wrappers without weakening source boundaries.

### What this does not prove

Claim-level provenance does not automatically prove that a paraphrase is semantically perfect.

The remaining semantic-quality gate is:
- independent review against allowed sources;
- controlled regeneration after meaningful source changes;
- comparison of omitted/strengthened/contradictory claims.

The structural architecture is no longer the uncertain part; semantic narrative review policy is.

## Updated recommendation

The research evidence now supports the following candidate architecture strongly enough for one more semantic-quality experiment:

```
Engineering Graph + Core/project projection
          ↓
Consumer closure + explicit extra capabilities
          ↓
source existence + source hashes
          ↓
deterministic projection manifest
          ↓
project presentation recipe
          ↓
section source plan
          ↓
source-bounded narrative/typed/native projection IR
          ↓
REVIEW package
          or
HANDOFF package + exact source snapshot
```

Do not canonicalize yet.

The remaining decision gate is not Core, graph topology, packaging, scope, freshness or provenance. It is whether narrative semantic review can be made reliable enough for routine regeneration without silently changing meaning.

