# Research — Repository / Codebase Structure & Engineering Tooling Design v1

Status: validated research candidate.

## Question

What must be decided before coding so that an implementation agent can realize accepted architecture without inventing repository structure, dependency enforcement, developer tooling or delivery gates, while avoiding a universal folder layout or tool list?

## Evidence distilled

Primary guidance converges on constraints rather than one physical tree:

- language packaging guidance treats layout as a trade-off (for example Python src vs flat layout), not universal architecture;
- clean/hexagonal/DDD styles require dependency and ownership boundaries, while concrete package names remain language/project choices;
- monorepo tooling such as Nx, Bazel and Pants encodes dependency graphs and boundaries mechanically;
- hermetic/locked environments exist to make dependency/build inputs reproducible;
- NIST SSDF, GitHub security controls, OpenSSF/SLSA and OWASP supply-chain guidance define security obligations independently of a particular scanner;
- CI systems turn selected obligations into required status checks; local hooks are latency optimizations, not the final trust boundary;
- architecture fitness functions support continuous mechanical enforcement of structural decisions.

Therefore Harness should canonicalize semantic obligations and selected realization, not prescribe a universal repository template.

## Taxonomy

The pre-code realization surface consists of these facets:

1. repository topology — mono/poly repository, deployable/package boundaries, ownership roots;
2. source/package topology — physical homes for semantic modules and public/private package boundaries;
3. architecture realization — mapping accepted components/bounded contexts to source units, composition root, dependency direction and mechanically checked forbidden edges;
4. shared-code policy — allowed shared kernels/utilities, ownership and dependency constraints;
5. test topology — location by level/scope, fixtures/test-data ownership, architecture tests;
6. persistence/migration topology — migration stream ownership, schema assets and execution boundary;
7. generated-artifact topology — source vs generated distinction, generator authority, regeneration/check policy;
8. configuration topology — build/runtime/tool configuration ownership and precedence;
9. scripts/tooling topology — project automation entry points and generated/manual status;
10. dependency/environment realization — manifests, lock/resolution data, tool/runtime version selection and reproducibility;
11. static-quality toolchain — formatting, linting, typing, dead-code/static analysis and architecture/dependency enforcement as applicable;
12. secure-development toolchain — secret, dependency/vulnerability/license and code-security checks as applicable;
13. build/package validation — clean-environment build/package/install verification where the product has a build/package artifact;
14. CI quality gates — authoritative blocking/advisory checks and their trigger scopes;
15. local developer workflow — fast deterministic subset, optional pre-commit integration, single canonical commands where useful;
16. ownership/review routing — repository ownership metadata where multiple owners/review boundaries exist;
17. release evidence — SBOM/provenance/attestation only where distribution/risk/obligation makes it applicable.

## Decision classes

### Universal invariant

- accepted semantic/component boundaries must have an unambiguous physical realization before coding;
- forbidden dependency directions that matter architecturally must have a mechanical enforcement path;
- generated and human-authored sources must be distinguishable;
- the authoritative CI gate set must be deterministic and reproducible from versioned project inputs;
- generated configs/projections must not become a second semantic source of truth.

### Conditional invariant

A concern becomes required only when its trigger exists. Examples:
- persistence => migration/schema topology;
- generated artifacts => generator/check contract;
- typed language or selected type policy => type checking;
- third-party dependencies => lock/update/vulnerability/license policy according to risk/obligation;
- distributable artifact => clean build/package validation and potentially SBOM/provenance;
- security-sensitive/public service => stronger SAST/secret/dependency gates;
- multiple independently built packages => explicit package/workspace graph;
- multiple ownership boundaries => code ownership/review routing.

### Project decision

Project design selects physical module roots, repository topology, chosen tools, exact CI jobs, blocking thresholds, generated outputs and the local command surface.

### Implementation freedom

Private file names, helper modules, minor test-helper layout, formatter-compatible line wrapping, local script decomposition and similar choices remain free unless they affect an accepted boundary, ownership, reproducibility or gate.

### Generated projection

Repository tree, bootstrap skeleton, CI/pre-commit/tool config and developer guide may be rendered from accepted realization decisions. They are replaceable outputs.

### Concrete tool choice

A concrete product is selected only after an obligation is applicable. Selection criteria: language/ecosystem fit, semantic coverage, deterministic exit status, machine-readable configuration, CI/editor integration, maintenance health, speed proportional to invocation frequency, false-positive control and ability to pin/reproduce the version.

## Authority model

No new Authority or knowledge kind is justified.

- SYSTEM-ARCHITECTURE owns system/runtime decomposition.
- COMPONENT-DESIGN owns implementation-facing component responsibilities, ports, dependency direction and composition boundaries.
- ENGINEERING-POLICY owns project-wide normative engineering obligations when they have an independent lifecycle.
- SECURITY/QUALITY/VERIFICATION own their respective required properties/evidence.
- IMPLEMENTATION-DESIGN owns the selected **repository realization**: physical mapping, concrete toolchain, reproducible environment and gate wiring.
- coding realizes that accepted contract and retains explicitly listed freedoms.

Repository realization is therefore a facet of `implementation-design`, not a new Core entity.

## Dependency graph

```text
Requirements / Quality / Security / Operability
                    ↓
Architecture → Component Design → Engineering Policy (when applicable)
                    \           /
                     \         /
                    Implementation Design
                    ├─ implementation slicing
                    ├─ repository realization
                    ├─ concrete toolchain selection
                    └─ authoritative quality-gate wiring
                              ↓
                         Implementation
                              ↓
                    generated repo/config projections
```

Verification/Test Design defines what must be proven. Implementation Design chooses how selected static/build checks are wired; CI is enforcement machinery, not semantic authority.

## Completeness model

Do not use a universal checklist. For every selected implementation scope, evaluate applicability-driven obligations:

1. every semantic/component module that must be coded has a physical realization or explicit implementation freedom;
2. every architecturally significant dependency restriction has an enforcement mechanism;
3. every applicable quality/security/supply-chain obligation is bound to a checker/gate or has explicit NOT_APPLICABLE/DEFERRED rationale;
4. source/generated/config/migration/test ownership boundaries are decided when applicable;
5. dependency/environment resolution is reproducible for the selected ecosystem;
6. authoritative CI gates and their trigger/blocking semantics are defined;
7. concrete tools are pinned/configured where reproducibility requires it.

A tool name never closes an obligation by itself; it must state which obligation it enforces.

## Structured canonical representation

Use a project-native structured artifact when automatic generation/validation is useful. Harness defines semantic fields, not a filesystem DSL.

Recommended shape:
- `module_realizations[]`;
- `dependency_rules[]`;
- `obligations[]` with applicability and enforcement;
- `generated_artifacts[]`;
- `environment`;
- `quality_gates[]`;
- `implementation_freedoms[]`.

Derived repository trees and tool configs are projections.

## Quality-gate placement

- editor/local command: fastest feedback, optional convenience;
- pre-commit: only fast deterministic checks where team value exceeds hook friction;
- PR CI: authoritative changed-code tests, format/lint/type/architecture/security/dependency checks applicable to merge;
- main: integration/full validation when not safely equivalent to PR;
- release: clean build/package/install, migration/release evidence, SBOM/provenance/attestation where applicable.

Avoid duplicated semantics: the same canonical command/config should back local and CI invocation when possible.

## Nutrition pilot

Inputs: Python 3.14, uv, SQLite, SQLAlchemy/Alembic, PySCIPOpt, CLI + server-rendered frontend, modular monolith, four bounded contexts.

Required pre-code decisions:
- one repository and one uv project is sufficient; no workspace split is justified;
- Python importable code should use a packaging-safe source root; context-aligned packages preserve semantic cohesion;
- four bounded contexts map to owned package subtrees; domain/application/infrastructure distinctions are local to each context rather than global layer buckets;
- one explicit composition root is the only cross-context concrete wiring location;
- infrastructure/framework/SQLAlchemy/PySCIPOpt dependencies are forbidden from leaking into inner contracts and checked mechanically;
- Alembic has one migration stream with explicit context/table ownership;
- generated human docs and other generated files remain projections with regeneration checks;
- uv lock is committed and CI uses locked/frozen semantics;
- formatting/linting/type/architecture/test/security/dependency checks are obligations; Ruff + Pyright (or Mypy) + pytest + a dependency-rule checker are appropriate concrete choices, but only the accepted project artifact should select one;
- PR CI is the authoritative merge gate; local/pre-commit runs a fast subset;
- package/install validation is required; SBOM/provenance is conditional and not required for the current local-only MVP absent a distribution/organizational obligation.

The model fits without adding a Python-specific Harness primitive.

## NAPMS pilot

Inputs: backend + frontend, PostgreSQL, HTTP, OIDC/security and richer CI/design tooling.

Differences that validate portability:
- repository topology may contain multiple build/package roots if frontend and backend toolchains require them, while bounded-context/module rules remain semantic;
- HTTP/OIDC/security introduce stronger SAST, dependency, secret and architecture checks;
- database migrations and serve/migrate modes require explicit topology and release gates;
- frontend lint/type/build checks can be different concrete tools from backend checks while satisfying the same generic obligations;
- dependency/security review should be blocking on PR for newly introduced vulnerable dependencies according to accepted threshold;
- release provenance/SBOM becomes more plausible when deployable artifacts are published, but remains applicability-driven.

No generic model change was required between pilots.

## Result

The gap is real but it is not a missing architecture layer or universal repository framework. It is a missing **repository-realization facet of Implementation Design**, with conditional obligations routed from existing Architecture, Component, Engineering Policy, Security, Quality, Verification and Delivery knowledge.
