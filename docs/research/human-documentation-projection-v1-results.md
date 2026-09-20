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

## Follow-up: claim-level evidence fragments

Artifact-level provenance is useful but still broad: a claim may cite the correct file while being weakly grounded in its actual content.

The experiment therefore added optional claim evidence:

```yaml
claims:
  - text: <human assertion>
    sources: [SYSTEM-RULES]
    evidence:
      - source: SYSTEM-RULES
        locator: consistency.export
        excerpt: "One shared read snapshot covers selection authority evaluation effectiveness provenance and technical realization."
```

The validator can now require evidence and prove:

- every evidence source is already cited by the claim;
- every cited claim source has evidence;
- evidence source belongs to the section scope and manifest;
- the canonical source file exists;
- the exact evidence excerpt exists in that canonical source;
- optional locators are non-empty presentation metadata.

Harness acceptance covers:
- valid evidence;
- missing evidence;
- evidence for an uncited/out-of-scope source;
- excerpt not present in the canonical source.

NAPMS research adds a real evidence sample over:
- SYSTEM-RULES;
- SECURITY-ARCHITECTURE;
- QUALITY-REQUIREMENTS.

The sample passed against the real project files.

### Interpretation

Claim-level evidence is a useful middle ground:

```
claim text
   ↓
source CanonicalArtifact
   ↓
verifiable source excerpt / optional locator
```

It does not mathematically prove that the paraphrase follows from the excerpt, but it makes review local and auditable rather than requiring a reviewer to rediscover the relevant fact in an entire file.

For structured sources, future adapters may replace or complement excerpts with stable field locators/JSONPath/YAML-path/native identifiers. A universal locator syntax is not required for v1.

### Candidate narrative acceptance levels

The experiments suggest three useful levels:

1. **SOURCE-BOUND**
   - every claim cites allowed CanonicalArtifacts.

2. **EVIDENCE-BOUND**
   - every cited source also supplies a verifiable excerpt/locator.
   - recommended default for generated REVIEW/HANDOFF narrative.

3. **TYPED**
   - claim is rendered deterministically from a typed/native structured field.
   - strongest when the source representation naturally supports it.

These are projection-validation strengths, not Core target states.

## Current research position

The package architecture is now validated across:
- exact Consumer scope;
- explicit overview scope widening;
- source existence;
- source content freshness;
- topic recipes;
- narrative IR;
- REVIEW/HANDOFF materialization;
- real project narrative claims;
- claim-level evidence fragments.

Remaining work before canonicalization is primarily policy/ergonomics:
- decide whether EVIDENCE-BOUND should be mandatory for narrative REVIEW/HANDOFF;
- test a meaningful canonical source change and narrative regeneration workflow;
- decide how generated projection IR/package is stored or published by default;
- decide whether reusable software documentation recipes belong in Harness as optional starter profiles.

No Core change is indicated.

## Follow-up: reusable documentation profile experiment

A tempting next step is to ship one generic software-document recipe that automatically selects sources by `knowledge_kind`.

Cross-project inspection rejects that as a reliable automatic mechanism.

Current production-contract coverage:

- NAPMS: 31/31 productions declare `knowledge_kind` (100%);
- Nutrition Management: 19/86 productions declare `knowledge_kind` (about 22%).

Nutrition legitimately has many project/domain-specific capabilities that are consumed by engineering agents but were never meant to participate in generic artifact-skill routing.

Authority IDs are also not a stable universal document taxonomy:
- NAPMS largely uses reusable engineering Authority names;
- Nutrition has several project/domain Authorities such as NUTRITION-TARGETING, FOOD-KNOWLEDGE, MARKET-CATALOG and PURCHASE-PLANNING.

### Decision

Do not make a generic software documentation profile an automatic source selector.

Harness may provide an optional **information-architecture starter** such as:

- Overview / Product Boundary;
- Domain & Application;
- Architecture & Interfaces;
- Security / Quality / Operability when applicable;
- Implementation Guide;
- Verification / Test / Readiness;
- Human Interface / Frontend Guide when applicable.

But every project must map those sections to explicit CapabilityIds, Authorities or CanonicalArtifact IDs in its own presentation recipe.

The starter owns headings/purpose suggestions only. It does not infer semantic applicability or source selection.

## Follow-up: persistence and publication policy

The pilots also demonstrate two valid publication styles:

- Nutrition keeps generated human documentation in-repository for convenient browsing/review;
- NAPMS has used generated implementation packages as CI artifacts/handoff output.

These should remain project policy.

Recommended defaults:

### Persist
- presentation recipe, when the project wants stable navigation/document organization;
- no generated document as a Capability provider;
- optionally generated REVIEW Markdown when repository review/browsing value justifies keeping it.

### Generate by default
- manifest;
- projection plan;
- projection IR;
- HANDOFF source snapshot;
- package metadata/freshness state.

### Prefer CI/on-demand artifact
- HANDOFF package, because committing a source snapshot duplicates canonical files;
- non-deterministic narrative output when the project does not want generated prose churn in Git;
- PDF/site/export formats.

### Commit generated narrative only when
- the project deliberately wants human documentation diff/review in Git;
- CI validates source hashes and projection scope;
- stale package detection is enforced;
- generated files are visibly non-canonical.

No single repository-storage policy belongs in Core or the projection contract.

## Controlled regeneration result

NAPMS research now includes a controlled semantic source mutation performed only in a temporary source copy.

The experiment changes the canonical quality statement from numeric targets being NOT_REQUIRED to a deliberately different REQUIRED statement.

Observed behavior:

1. old IR + new manifest/plan -> rejected because manifest digest changed;
2. old IR with only the new digest substituted -> rejected because its evidence excerpt no longer exists;
3. regenerated claim + regenerated evidence excerpt -> accepted.

This proves the intended regeneration fence:

```
canonical source changes
      ↓
source hash changes
      ↓
manifest digest changes
      ↓
old IR is stale
      ↓
digest-only rebinding is insufficient when evidence is required
      ↓
affected narrative claim/evidence must be regenerated or deliberately reviewed
```

This is substantially stronger than a timestamp or "generated from commit X" notice alone.

## Follow-up: visual projections inside documentation packages

The earlier Engineering Knowledge Projection research identified visual projection as a separate class. NAPMS provides a concrete second-stage validation because its canonical graph already declares deterministic project-owned projections:

- CONTEXT-MAP;
- Resource Catalogue views;
- Application Communication / Deployment / Business Connectivity / Access Policy domain views;
- first-MVP journey view;
- persistence ERD.

Each declaration already contains:
- canonical `source_ids`;
- a project-owned generation command;
- disposable output paths.

The Harness prototype now supports scoped visual assets without taking ownership of their generation.

### Eligibility rule

A declared visual projection may be included in a Human Documentation package only when **all** declared canonical `source_ids` are already inside the explicit human-projection manifest scope.

Therefore a diagram cannot become a back door for reading knowledge outside the selected Consumer/composite documentation scope.

### Execution boundary

Harness does not execute the project declaration's arbitrary `command`.

NAPMS research CI explicitly runs its own project generators before packaging, then passes the resulting assets to Harness for:
- output existence validation;
- output hashing;
- package copying;
- visual metadata materialization.

This preserves the boundary:

```
project canonical sources
      ↓
project-owned deterministic generator/check
      ↓
disposable visual projection
      ↓
Harness scope validation + package assembly
```

The NAPMS research workflow generated all declared architecture/domain/journey/ERD PlantUML projections and the Human Projection test passed.

### Repository-storage result

The declared NAPMS visual outputs are not committed to main. This is valid.

Human Documentation Projection therefore must not require visual assets to exist in Git. They may be:
- generated immediately before package assembly;
- verified by a project-owned `--check`/freshness command;
- published only inside REVIEW/HANDOFF/CI artifacts.

### Visual freshness limit

Hashing a generated visual file proves the packaged bytes are stable after selection. It does **not by itself** prove that the file was generated from the current source versions.

A stale diagram could theoretically be rebound to new source hashes if a caller skipped the project generator/check step.

Therefore visual projection acceptance requires external generation/freshness evidence from the project adapter/orchestration.

Recommended v1 rule:

- Harness validates visual **scope**, path safety and packaged-output hashes.
- The project owns visual **generation correctness/freshness** through its deterministic generator/check command.
- A package that claims visual freshness must be assembled only after that project-owned step succeeds.
- Harness must not silently execute arbitrary repository commands merely because they appear in projection metadata.

Future tooling may accept an explicit verified-generation receipt, but no new Core concept is justified.

### Nutrition contrast

Nutrition currently has no equivalent machine-declared visual projection set.

Human Projection must therefore emit no invented diagrams for Nutrition merely because a generic software documentation profile would look nicer with them.

This is positive evidence for the renderer-neutral rule: visual assets are included only when accepted project-native structure/generators already support them.

## Follow-up: Nutrition narrative quality benchmark

Nutrition's existing `docs/generated/overview.md` was used as a quality/information-architecture benchmark, but not as a semantic input to the research narrative.

A new evidence-bound research overview was produced from only:
- Product Requirements;
- Target Architecture;
- Strategic Domain / Context Map;
- Application Design;
- CLI Contract.

It covers the same reader-facing dimensions:
- product boundary;
- modular-monolith/system shape;
- primary planning flow;
- technical failure boundary;
- deterministic first external interface;
- explicit no-HTTP/browser/authentication first-slice boundary.

Every generated claim is evidence-bound to exact canonical source excerpts.

The generated wording is intentionally not identical to the existing benchmark.

### Acceptance correction

An initial experiment compared literal markers across generated and benchmark prose and failed because the benchmark describes the primary planning flow without naming `GeneratePurchasePlan`.

This is evidence that byte/lexical similarity is not a valid narrative-quality criterion.

The corrected comparison uses **semantic coverage dimensions**, allowing different wording for the same accepted concept.

Recommended narrative acceptance therefore combines:

1. structural source-scope validation;
2. source-content freshness;
3. claim-level evidence;
4. semantic coverage checklist appropriate to the presentation recipe;
5. human/agent review for unsupported strengthening, omission or contradiction.

Do not use exact generated-text snapshots as the primary acceptance oracle for narrative projection.

Typed/source-native deterministic renderers may still use exact snapshots.

## Research-stage conclusion

The current research has now validated the proposed architecture against both materially different projects across:

- exact Consumer-scoped handoff;
- explicit broader overview scope;
- deterministic source closure;
- source existence and content hashes;
- project presentation recipes;
- source-bounded narrative IR;
- evidence-bound claims;
- REVIEW and HANDOFF packages;
- stale-source and stale-narrative rejection;
- controlled semantic regeneration;
- project-native visual projections;
- high-quality Nutrition narrative coverage;
- incomplete NAPMS frontend scope without invented documentation.

No new Core entity, Documentation Authority, fixed document catalogue or universal artifact schema was required.

The remaining work is no longer fundamental model research. Before any canonicalization, the next phase should be a **candidate-contract cleanup**:
- simplify the experimental API/schema;
- define which fields are mandatory vs optional;
- decide EVIDENCE-BOUND defaults by package mode;
- turn the research skill into a clean reusable skill candidate;
- produce compact acceptance fixtures;
- re-run both project pilots from the cleaned candidate.

This cleanup must remain on research/candidate branches until explicitly approved for main.

