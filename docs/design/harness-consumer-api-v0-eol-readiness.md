# Consumer API v0 EOL readiness evidence

Status: canonical evidence contract; no lifecycle transition authorized.

## Ownership and decision boundary

`spec/distribution/consumer-api-v0-eol-readiness-v0.yaml` owns repository-local
readiness evidence, unresolved gates and future obligation classification.
`spec/distribution/consumer-api-lifecycle-v0.yaml` continues to own lifecycle
states, transitions and support obligations. This document introduces no Core
state or project workflow. V0 remains **DEPRECATED**, v1 remains **SUPPORTED**.

A passing readiness validator means the evidence report is consistent, not that
EOL is permitted. Current aggregate is **NOT_READY**: G1–G8 PASS, G9
NOT_ESTABLISHED, G10 NOT_MET. The readiness contract is a bounded snapshot of
this tranche. Completing external assessment or making an EOL decision requires
reviewed changes to the contract and its validator; this tranche's validator
intentionally rejects promotion to READY or EOL.

Readiness does not duplicate lifecycle policy. `blocks_transition: EOL` on an
obligation means its policy must be settled in an EOL tranche; it does not mean
its files must disappear before EOL. Current unmet evidence blockers are exactly
G9 and G10. `REMOVED` means physical cleanup requires a subsequent removal
decision. `SEPARATE` denotes an independent architecture/public-API decision;
`NEITHER` denotes retained tooling.

## Evidence gates

| Gate | Evidence | Current result |
|---|---|---|
| G1 | Lifecycle validator checks v1 SUPPORTED | PASS |
| G2 | Lifecycle validator checks v0 DEPRECATED | PASS |
| G3 | Lifecycle validator checks bounded owned onboarding surfaces and v1 binding | PASS |
| G4 | AST imports, current usage inventory and context boundaries | PASS: zero canonical runtime legacy dependencies |
| G5 | Pack validator imports/executes canonical source and Pack after physical facade removal; negative control fails | PASS |
| G6 | Same-target wrapper migration with isolated interpreter and immutable pins | PASS |
| G7 | Direct AST inspection plus reviewed literal/embedded execution references | PASS: zero active non-compatibility dependencies |
| G8 | Complete registry-derived facade inventory and policy obligations | PASS |
| G9 | Repository-local inventory does not establish an independent consumer population assessment | NOT_ESTABLISHED |
| G10 | No explicit EOL distribution decision; lifecycle still references deprecation decision | NOT_MET |

These are heterogeneous proofs, not a score. G5/G6 execute the existing authored
Consumer scenarios deterministically; they do not claim agent judgement or
independent external adoption evidence.

## Existing-target migration v0 -> v1

Starting point: a target commits `.harness/harnessw.py` and
`.harness/harness-binding.json` selecting v0. Keep the same wrapper. Review and
pin a Harness **40-hex commit** supporting v1, then change only the binding's
`consumer_api` to v1 and `source.revision` to that reviewed commit. The repository
URL normally stays the same. An existing target using an older bootstrap
protocol must first verify that its wrapper supports canonical v1 dispatch;
the deterministic proof covers the current standalone wrapper protocol.

From the target repository:

```sh
python .harness/harnessw.py sync
```

From the printed Pack directory:

```sh
python -m harness.application.skill_router operation --surface consumer --operation project-engineering-status
```

Use the canonical router for subsequent operation/method/artifact discovery.
Do not copy legacy root facades into a v1 Pack. Consumer API selection changes
physical distribution and entrypoint identities; it does not require migrating
source, canonical project knowledge, semantic acceptances or product artifacts.
Target-owned bootstrap guidance that still invokes root facades should use the
canonical router command above.

`tests/test_consumer_wrapper.py::test_v0_to_v1_migration` reuses the
wrapper snapshot/commit helpers and runs one clean target through both APIs.
Its private interpreter has only PyYAML, no installed Harness, no inherited
PYTHONPATH and no global/user site fallback. Both source revisions are immutable;
the second test-only source lacks every registered root/dotted v0 facade.
The wrapper bytes and target-owned source/knowledge bytes remain unchanged.
Both manifests validate, canonical v1 routing runs, operation/artifact route
results and complete traces of `create-work-routing`,
`structural-provider-removal` and `semantic-gap-question` are equal. Scenario
assertions supply authored O1 oracles; equality supplements those assertions.
The existing Pack acceptance also covers method routing and the broader
source/Pack stripped-facade ratchet. Test-only deletion is not source deletion
authorization.

## First-party dependency evidence

Ordinary semantic validators and the lifecycle experiment now import existing
canonical modules. The readiness validator rejects any direct legacy import in
active non-facade Python files, including validators/tests; a validator filename
is never sufficient to exempt a dependency.

The current lifecycle usage inventory is regenerated from direct repository
inspection. Its textual references remain heterogeneous: historical documents,
canonical owner descriptions, compatibility probes and active execution are
not interchangeable. The readiness contract separately lists every remaining
bounded execution candidate, its exact reference set and reviewed reason.
V0 wrapper dispatch, Pack/wrapper probes, registry-driven structural/negative
probes and Core export/CLI compatibility probes are intentional subjects.
Bootstrap wording assertions and canonical main's `argv[0]` are reference-only.

The static oracle covers absolute imports, embedded import snippets and literal
facade filename arguments, plus bounded shell/workflow commands. It cannot prove
absence of arbitrary computed imports or command strings. Direct inspection and
G5/G6's physical absence executions supplement that limit. Historical/declarative
content does not count as an active execution dependency. Canonical runtime is
not classified as removal debt.

## EOL and removal obligations

The machine contract inventories each registered root or dotted facade
individually, without copying its canonical mapping from repository-layout.
Every obligation records owner, rationale, EOL action, REMOVED action and which
transition requires handling it. It also covers distribution definitions,
wrapper dispatch, implicit defaults, compatibility registries/checks and v0
examples/documentation.

At EOL an explicit distribution decision must settle latest-source v0
materialization/dispatch, compatibility assertions, documentation and omitted-API
behavior. Options for the unchanged implicit v0 default include requiring an
explicit API, defaulting to v1 with an acknowledged break, or a temporary
compatibility shim. **No option is selected here.** Immutable historical
revisions and their wrappers remain artifacts; current-source support claims
must be distinguished from physical file presence.

Root and dotted facade deletion, v0 Pack removal and registry simplification
belong to a later, separately authorized REMOVED tranche. Facades may remain
physically present immediately after EOL. No deletion is pre-authorized.

The non-installed execution bridge remains required by canonical v1. Core alias
and initializer exports need an independent public export decision. The provider
agent is an implementation exception, not a facade; its distribution/relocation
is a separate decision. Scenario Suite/drivers are retained Consumer tooling
in both APIs. None is automatically coupled to v0 EOL/removal.

## External consumer evidence and next decision

Repository-local scans and synthetic migration establish no external consumer
assessment. No independent consumer acknowledgements are recorded. Even a
GitHub search returning zero hits would not prove absence: indexing may lag,
private/inaccessible/unindexed consumers may exist. The machine contract keeps
search absence explicitly non-conclusive and G9 NOT_ESTABLISHED.

Before proposing DEPRECATED -> EOL, record a reviewed independent consumer
assessment with scope, method, evidence, limitations and migration disposition;
then make a separate explicit EOL distribution ADR settling the EOL policy
obligations above. Local tests alone cannot close either gate.

## Assurance and CI

This tranche reuses HA-A18/A18-F03/F05/F06 and TD-DIST-001/002: TL0/TL1
structural/mutation checks and TL2 wrapper/materialization composition with O1
oracles. HA-A19/TD-CI-001 covers registration. No Core/domain or runtime
architecture boundary changes; no new ADR authorizes EOL or removal.

Readiness validation is registered in the deterministic full gate; migration
runs inside the existing wrapper check. Provider rerun selection compares the
complete changed-file set with every frozen evidence `execution_bindings.files`.
Zero intersection requires no rerun. Frozen historical evidence is never
rewritten. Final PR evidence reports actual timings, checks and GitHub Actions.
