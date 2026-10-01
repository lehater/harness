# Harness Assurance System Audit v0

Status: completed audit-only evidence review.

Audit run: AUD-021.

Evidence baseline:

- repository: lehater/harness;
- branch: audit/harness-corrections;
- pre-audit HEAD: e15f834d2fd218c0f92177c9c65e6f021e054ca5;
- PR #120: draft;
- current deterministic integration gate was intentionally not executed for this audit pass because the PR is in draft iteration and CI policy reserves the exhaustive gate for a coherent checkpoint/integration candidate;
- at the baseline HEAD, the cheap CI Policy workflow passed while the Harness Core and Greenfield Engineering Graph workflows were skipped as required by draft policy.

This artifact evaluates the test / validation / evaluation / assurance system. It does not change production, test, validator, Scenario Suite or CI implementation.

## 1. Executive conclusion

Harness already has substantial executable evidence for **deterministic behavior after its semantic inputs have been made explicit**.

The strongest current evidence covers:

- Core structural ownership/dependency/Question invariants;
- Engineering Graph validation, producer/consumer closure and CREATE/WAIT/PENDING/COMPLETE behavior;
- lifecycle/currentness and semantic-admission rules;
- source/derivation completeness once source units, semantic atoms and production contracts are declared;
- Decision Pipeline and Project Frontier composition;
- deterministic operation/method/artifact routing once the route key or Capability knowledge kind is known;
- Consumer Pack materialization, pinning and distribution;
- CI inventory/stage policy and deterministic full-gate composition.

Harness also has meaningful real-project evidence: NAPMS and Prep scenarios exercise real project graphs and semantic slices, and real NAPMS assurance adoption found a genuine downstream semantic-loss defect while accepting an intact control slice.

The central assurance gap is earlier in the chain:

~~~text
selected scope + unfamiliar repository
        ↓
accepted project evidence
        ↓
material decisions / applicability
        ↓
project-specific Capability discovery
        ↓
knowledge-flow dependencies
        ↓
Authority boundaries
        ↓
Project Engineering Graph
~~~

Most executable evidence begins **after** one or more of those inputs have already been authored, classified, atomized or selected.

That boundary is intentional in the current architecture: Harness Core does not infer arbitrary project semantics from prose, projects own semantic truth, and the agent owns judgement. Therefore the missing proof is not “Core should autonomously mine a repository”. The missing proof is narrower and more important:

> Given a selected scope and a previously unfamiliar project, does a fresh agent following the routed Harness bootstrap/design procedures reproducibly construct a sufficiently accurate minimal project model without omitting material obligations, inventing capabilities, or forcing the project into the Reference Model vocabulary?

Today there is no executable repeated-agent evidence for that contract.

A second systemic gap is that Scenario Suite coverage is catalog-driven but the repository has no independent **Harness Ability Model → failure modes → required evidence** registry. A scenario can prove every requirement that the catalog currently knows about while an entire Harness responsibility remains absent from the catalog. This is a self-test gap in the assurance system.

Therefore the current evidence supports the statement:

> Harness has strong deterministic evidence for many declared mechanisms and cross-layer reactions, plus partial real-project and semantic-calibration evidence.

It does **not** yet support the stronger statement:

> The agent-enabled Harness system can reliably discover and build an adequate project-specific engineering model for an unfamiliar repository, including novel project Capabilities/Authorities, and do so reproducibly across clean contexts.

No single “Harness works at N%” figure is justified. The evidence is heterogeneous and the denominator is not currently defined independently of the tests themselves.

## 2. Scope and interpretation of Harness purpose

Canonical repository contracts establish three distinct responsibility layers.

### 2.1 Project semantic ownership

Target repositories own:

- product/domain/architecture truth;
- project-specific CapabilityIds;
- applicability/coverage policy;
- semantic acceptance of canonical artifacts;
- mapping existing project truth into Harness inputs.

Harness explicitly rejects a generic parser that infers engineering ownership from arbitrary prose.

### 2.2 Harness deterministic ownership

Harness owns:

- Core and Engineering Graph structural validation;
- producer/prerequisite invariants;
- recursive Consumer closure;
- target-state computation;
- lifecycle/currentness and strict semantic-closure mechanics;
- coverage/read-model composition;
- deterministic routing once semantic routing keys exist;
- Consumer Pack distribution and CI policy.

### 2.3 Agent-enabled Harness procedure ownership

The routed Consumer skills add a higher-level operational contract:

- select/adapt a target scope;
- bootstrap/reconcile the smallest useful project realization;
- identify accepted sources without inventing project truth;
- surface unresolved ownership/semantics as Questions;
- produce missing engineering knowledge through routed skills;
- recompute closure.

The assurance audit must therefore distinguish:

~~~text
Harness mechanism correctness
!=
project-model discovery quality
!=
agent procedure compliance
!=
semantic evaluator quality
~~~

## 3. Harness Ability Model

The following ability IDs are audit-local. They do not add domain concepts to Core.

| Ability | Observable contract |
|---|---|
| AB-01 Core structural truth | Invalid ownership, dependencies, capability providers and Question references are rejected; valid state yields deterministic ownership/blocking results. |
| AB-02 Engineering Graph topology | A valid graph has unique capability production, acyclic production dependencies, live public capabilities and deterministic Consumer closure. |
| AB-03 Target-state action semantics | Given graph/profile + Core state, CREATE/WAIT/PENDING/COMPLETE is deterministic and prerequisites/blockers cannot be bypassed. |
| AB-04 Authority boundary formation | Given accepted decision/knowledge evidence, the project model groups it into semantically cohesive, independently changeable Authorities without joint-ownership leakage or arbitrary splitting/merging. |
| AB-05 Capability discovery | Required project knowledge becomes a project-specific Capability when independently provable/lifecycle-relevant, including a Capability absent from Reference Model templates; irrelevant or redundant Capabilities are not invented. |
| AB-06 Applicability and Engineering Coverage | REQUIRED/N/A/UNKNOWN/QUESTION distinctions follow explicit evidence; silence cannot become N/A; omitted concern/subject territory remains visible. |
| AB-07 Project Authority Assessment | Authority applicability is preserved/reopened/migrated conservatively; split/retired Authorities do not inherit unsupported applicability. |
| AB-08 Design target selection | For a selected scope, the resulting Design Profile/Consumer closure contains the knowledge required to proceed without downstream invention and does not promote tasks/workflow state into knowledge. |
| AB-09 Existing-project bootstrap/reconcile | A fresh agent reuses existing project-owned truth where present, constructs only the smallest required projection otherwise, preserves unknowns as Questions, and is idempotent. |
| AB-10 Greenfield bootstrap | From an explicit greenfield goal/scope, a fresh agent forms a minimal valid initial engineering model and exposes the first safe engineering frontier without relying on pre-authored graph truth. |
| AB-11 Source acquisition/completeness | Selected canonical source boundaries are lossless relative to declared source units; statements/accepted scope atoms are completely dispositioned before downstream completeness is claimed. |
| AB-12 Semantic derivation/admission | Required upstream semantics are preserved/transformed/constrained/realized without silent loss or cross-Authority invention; invalid provenance/contradiction is rejected. |
| AB-13 Questions/blockers | Genuine unresolved semantics become Questions owned by the deciding Authority; process/implementation failures do not manufacture semantic Questions. |
| AB-14 Lifecycle/currentness/migration | Accepted knowledge becomes stale when material prerequisite/policy semantics change; replay is safe; graph identity evolution has an explicit migration result instead of silent loss. |
| AB-15 Decision/frontier orchestration | Decision readiness, failed validation, semantic gaps, coverage work and blockers compose into one deterministic next-action frontier without false COMPLETE. |
| AB-16 Agent/method/artifact routing | A fresh agent selects the intended operation from task intent; the router resolves only authorized routes; CREATE work reaches the correct artifact skill; WAIT/PENDING work is not executed. |
| AB-17 Repository realization and projections | Repository realization, frontend closure, workspace and human projections remain derived from accepted truth and fail closed on missing structural/semantic prerequisites. |
| AB-18 Consumer distribution | A target repository obtains a reproducible pinned Consumer Pack with only public Consumer surfaces; incompatible or incomplete packs fail closed. |
| AB-19 CI/validation policy | Every deterministic validator/test/workflow is inventoried, staged by cost, and the final integration candidate cannot bypass the exhaustive deterministic gate. |
| AB-20 External semantic assurance | Provider-backed semantic judgements are blinded/request-bound, fail closed on malformed/incomplete runs, and are calibrated against an independent expert-labelled corpus. |
| AB-21 Real-project portability | The same Harness contracts operate on materially different project shapes without adding project-specific branches inside generic Harness evaluation. |

## 4. Evidence inventory

At the baseline commit the main evidence surfaces are:

| Evidence family | Inventory | What it actually proves | Oracle / independence |
|---|---:|---|---|
| Python unit/experiment tests | 1 file under tests | Lifecycle experiment behavior | Hand-authored expected behavior; narrow |
| Deterministic validators | 65 files | Schema, invariants, contracts, research fixtures, integration boundaries, routing, distribution and meta-policy | Mostly hand-authored fixture/assertion or implementation contract |
| Scenario Suite | 80 scenarios | Cross-layer reactions over structured fixtures/drivers; negative mutations; selected real-project slices | Mostly hand-authored invariant oracle; some real-project accepted truth |
| Acceptance/example fixtures | Core/graph/target/workspace/frontend examples | Known-good/known-bad contract shapes | Repository-authored; often designed with implementation |
| Research fixtures | applicability/coverage/reference-model/project-behavior fixtures | Specific research hypotheses and deterministic materializer behavior | Mixed; mostly hand-authored |
| Reference Model holdouts | frozen browser-extension, Stripe-webhook, Airflow, Prometheus-style cases | Known-template materialization from declared project facts across external domains | Stronger frozen/external-domain oracle, but project facts are still manually encoded |
| Reference Model regressions | Prep, NAPMS | Materializer compatibility with existing graphs | Real-project regression; not independent holdout |
| Real-project Scenario evidence | Prep and NAPMS snapshots/slices | Generic drivers and semantic derivation over real project truth | Real-project accepted truth; partially correlated with Harness evolution |
| Real-project assurance adoption | NAPMS slices | Source-to-derivation chain can reject a real semantic omission and accept an intact control | Strong real-project evidence after source/atom selection |
| Semantic calibration corpus | bootstrap + real-project labelled corpora | Deterministic FP/FN scorer behavior against expert labels | Expert oracle |
| Live calibration | provider-backed repeated runs | Request binding, fail-closed malformed output, observed evaluator agreement/stability on small corpus | Blinded predictions; evaluator independence explicitly unverified |
| Consumer Pack/wrapper validation | validators + pack fixture | Deterministic distribution/pinning/surface closure | Implementation contract + generated pack comparison |
| CI policy/meta-validation | registry + policy validator + workflows | Test/workflow inventory and stage/trigger invariants | Deterministic structural oracle |

Important interpretation rules:

1. A validator name is not evidence class by itself. Some validators execute behavior; others validate that a fixture/spec is internally well formed.
2. Different scenarios that call the same underlying deterministic oracle are not independent proofs.
3. A real-project snapshot is stronger than a synthetic fixture for portability, but it is not automatically a holdout if the project materially influenced the mechanism being tested.
4. A frozen external-domain holdout is stronger for Reference Model generalization, but it still does not test raw repository discovery when project facts were manually prepared.

### 4.1 Misleadingly strong-looking evidence

spec/research/project-behavior-evals-v1.yaml contains six useful project archetypes, but validate_project_behavior_evals.py validates the **fixture and expected classification data itself**. It does not run a discovery/materialization/agent pipeline that derives those expectations from the evidence list.

Therefore it is evidence that the benchmark specification is internally coherent, not evidence that Harness behaves correctly on those six projects.

Similarly, validate_fresh_context_routing.py invokes deterministic router functions in source/Consumer Pack environments. It proves that a supplied route key resolves consistently. It does not prove that a fresh agent infers the correct route key from an unfamiliar natural-language task.

## 5. Test/evidence taxonomy

Status vocabulary:

- PRESENT — meaningful executable evidence exists for the intended class;
- PARTIAL — a nearby mechanism exists but does not cover the full failure class;
- ABSENT — no evidence of this class was found for the relevant Harness responsibility.

| Evidence class | Needed? | Current | What it can prove | What it cannot prove |
|---|---|---|---|---|
| Structural/schema tests | Yes | PRESENT | Shape, required fields, registry alignment, invalid references | Semantic adequacy or agent judgement |
| Unit tests | Selectively | PARTIAL | Local algorithm behavior where isolation adds value | Cross-layer/project behavior |
| Contract tests | Yes | PRESENT | Stable boundaries such as Core, graph, pack, routing | Whether contracts themselves are complete |
| Invariant tests | Yes | PRESENT | Safety properties independent of literal output | Discovery completeness |
| Negative tests | Yes | PRESENT | Known invalid states are rejected | Unknown failure classes |
| Mutation tests | Yes | PRESENT | Specific omissions/changes are detected | Universal mutation resistance |
| Property-based tests | Useful for graph/state engines | PARTIAL | Generalized invariant families | Semantic judgement |
| Metamorphic tests | Yes for semantic/discovery mechanisms | PARTIAL | Stability under reorder/noise/meaning-preserving changes | Correctness on unseen semantics |
| Deterministic regression tests | Yes | PRESENT | Known defects stay fixed | New/unseen defects |
| Integration tests | Yes | PRESENT | Multiple Harness mechanisms compose | Fresh-agent discovery |
| Cross-layer Scenario Suite | Yes | PRESENT | Behavioral reactions across read models/drivers | Completeness of the Scenario catalog itself |
| Lifecycle/currentness tests | Yes | PRESENT | Stale/current/revalidation behavior | Generic graph rename/split/merge remains incomplete; see HARN-014 |
| Migration/backward compatibility | Yes | PARTIAL | Consumer Pack and Reference Model evolution cases | Generic project-graph identity migration |
| Greenfield E2E | Yes | PARTIAL | Greenfield graph/derivation behavior once graph is authored | Goal/repo -> agent-built graph |
| Existing-project bootstrap/reconcile E2E | Yes | ABSENT at live-agent level | Would prove minimal reuse/non-duplication/idempotence | Current deterministic tests do not execute the procedure |
| Real-project regressions | Yes | PRESENT | Behavior on known NAPMS/Prep slices | Generalization beyond known projects |
| Cross-domain holdouts | Yes | PARTIAL | Reference template materialization on frozen external domains | Raw project evidence discovery and novel Capability/Authority formation |
| Adversarial fixtures | Yes | PRESENT downstream | Known contradictions/omissions/provenance defects | Agent susceptibility to unknown semantic traps |
| Capability-discovery tests | Yes | PARTIAL for known templates; ABSENT for novel agent discovery | Reference materializer selects known templates from declared facts | Whether a fresh agent discovers a genuinely project-specific Capability |
| Authority-boundary discovery tests | Yes | ABSENT at agent-discovery level | Current research fixtures validate already-authored boundaries | Whether a fresh agent finds the right split/merge from project evidence |
| Applicability tests | Yes | PRESENT after facts are declared; PARTIAL end-to-end | Conservative REQUIRED/N/A/UNKNOWN handling | Whether evidence/facts were discovered correctly |
| Completeness/omission tests | Yes | PRESENT downstream; PARTIAL meta-level | Source/subject/concern omissions in declared scope | Whether the assurance catalog omitted an entire Harness ability |
| Over-generation tests | Yes | PARTIAL | Reference forbidden templates and selected negative cases | Agent-invented project Capability/Authority rate |
| Reproducibility tests | Yes | PRESENT deterministic; PARTIAL overall | Pure mechanisms replay deterministically | Agent judgement repeatability |
| Clean-context repeated-agent runs | Yes | ABSENT | Would measure semantic convergence of routed procedures | Not currently established |
| Semantic-judgement evals | Yes | PRESENT | Request-bound judgement/scoring on labelled cases | Universal semantic correctness |
| Independent calibration oracle | Yes | PARTIAL | Expert-labelled corpus and blinded live predictions | Broad representativeness and independence; EVO-031 |
| Provider/model variation | Useful before broad claims | ABSENT/very limited | Would expose model-specific dependence | Current evidence is not cross-provider generalization |
| FP/FN measurement | Yes for classifiers/evaluators | PRESENT on calibration corpora | Corpus-specific detection/error rates | Population-wide error rates |
| Stability under irrelevant input changes | Yes | PARTIAL/PRESENT in derivation/reference tests | Selected metamorphic invariants | Whole-agent stability |
| Performance/scalability | Yes | PARTIAL | CI cost and some activation scaling | Supported graph depth/volume envelope; HARN-023/EVO-032 |
| CI-policy/meta-tests | Yes | PRESENT | Inventory, ordering, draft/final gate policy | Semantic coverage adequacy |
| Self-test of testing system | Yes | PARTIAL | CI registry prevents unregistered executable checks | No independent ability registry/oracle-strength gate |

## 6. Discovery pipeline audit

The requested discovery chain should not be interpreted as “Harness Core autonomously parses an arbitrary repository”. The valid agent-enabled contract starts from a selected scope and project instructions.

| Stage | Responsibility | Algorithm vs judgement | Current executable evidence | Independent oracle | Assurance result |
|---|---|---|---|---|---|
| 1. Task -> operation selection | Coordinator/agent | Agent judgement, then deterministic router | Router/fresh-context functions only | No real-agent trace | PARTIAL |
| 2. Existing project truth discovery | bootstrap skill | Agent judgement | No live-agent bootstrap eval | None | WEAK |
| 3. Source/evidence boundary selection | project + agent | Agent/human judgement | Source-boundary validators after selection | Real-project review in selected slices | PARTIAL |
| 4. Material fact/decision extraction | project + agent | Semantic judgement | Statement/semantic acceptance after atomization | Human/expert on selected corpora | PARTIAL |
| 5. Applicability | Coverage/Reference + project | Deterministic after project facts; judgement to establish facts | Strong deterministic tests | Hand-authored/holdout expectations | MODERATE |
| 6. Capability discovery | project/agent; Reference can propose known templates | Mixed | Strong for known Reference templates; none for novel project Capability discovery by agent | No frozen raw-repo oracle | WEAK |
| 7. Knowledge-flow dependencies | project/agent; graph validator | Mixed | Strong validation/derivation evidence once edges declared | Some real-project semantic review | MODERATE |
| 8. Authority grouping/boundaries | project/agent | Semantic judgement | Hand-authored Authority research fixtures validate boundary properties | No discovery oracle/repeated run | WEAK |
| 9. Project Engineering Graph construction/reconciliation | bootstrap/reconcile operation | Agent procedure + deterministic validation | Graph validators; no real agent procedure E2E | None for generated model | WEAK |
| 10. Consumer closure | Harness | Deterministic | Strong graph/profile/scenario evidence | Contract oracle | STRONG |
| 11. CREATE/WAIT/PENDING/COMPLETE/frontier | Harness | Deterministic | Strong target/decision/frontier scenarios | Contract oracle | STRONG |

### 6.1 Key negative result

No current test was found that executes the full contract:

~~~text
fresh agent
+ selected scope
+ raw unfamiliar repository
+ Harness Consumer Pack/instructions
        ↓
route bootstrap/reconcile
        ↓
identify accepted project evidence
        ↓
form project-specific Authorities + Capabilities + dependencies
        ↓
validate/reconcile Project Engineering Graph
        ↓
derive Consumer/frontier
        ↓
grade the resulting semantic model against an oracle
~~~

Existing greenfield scenarios start from a pre-authored Engineering Graph.

Existing real-project Scenario cases start from a project graph snapshot and/or manually selected source units/semantic surfaces.

Reference holdouts start from manually encoded project facts and test materialization of a frozen known template catalog.

### 6.2 Novel Capability and Authority tests

No executable evidence was found for the critical falsification cases:

- project evidence requires a useful Capability that does not exist in Reference Model templates;
- one reference Authority must be split because the project has independently changing decision surfaces;
- two plausible reference boundaries must remain merged because no independent lifecycle/public contract exists;
- an irrelevant reference template must not be invented merely because its vocabulary resembles project text.

These are the tests most capable of exposing reference-model bias.

## 7. Oracle independence audit

Use the following oracle classes for future evidence metadata:

| Oracle class | Definition | Typical current examples | Strength |
|---|---|---|---|
| O0 implementation-derived | Expected answer is materially produced by the same implementation/model being tested | Avoid where possible | Weak |
| O1 hand-authored contract | Maintainer-authored expected invariant/fixture | Most validators and synthetic scenarios | Strong for explicit mechanism contracts, weak for semantic generalization |
| O2 accepted real-project truth | Existing project canonical artifact/decision is the oracle | NAPMS/Prep real-project slices | Strong for that project; correlation risk |
| O3 frozen independent holdout | Oracle authored/frozen independently before execution on materially different domain | Reference external holdouts | Stronger generalization evidence |
| O4 blinded independent judgement | Evaluator sees blinded inputs; labels come from expert/cross-human/reference oracle | Live semantic calibration | Strong semantic-eval evidence when corpus is representative |

### 7.1 Circular validation risks

The following patterns reduce evidence strength even when tests are green:

- the Scenario coverage catalog defines the behaviors that scenarios must claim to cover; there is no separate Ability Model proving the catalog contains all Harness responsibilities;
- a scenario author both constructs the fixture graph and declares the expected graph reaction;
- Reference materializer holdouts are stronger because the model is frozen, but project facts remain a manual interpretation layer;
- real-project regression graphs are valuable but NAPMS/Nutrition/Prep have influenced Harness evolution, so they are not independent holdouts for every mechanism they helped shape;
- deterministic calibration of predictions against expert labels proves the scorer, not the live evaluator;
- repeated calls to the same deterministic driver are regression breadth, not independent oracle diversity.

## 8. Repeated clean-context agent evaluation

A minimal reproducibility protocol should freeze:

- repository fixture commit;
- selected task/scope;
- applicable target instructions;
- Harness commit/Consumer Pack;
- agent/model/provider descriptor;
- tool permissions;
- independent reference oracle;
- run count and normalization protocol.

Run at least three clean contexts during initial research; use five or more when estimating stability for a release criterion.

Do not compare prose literally.

### 8.1 Normalize to semantic IR

Normalize every run to:

- accepted source/evidence identities;
- Authority decision-surface membership;
- Capability semantic identity: subject + knowledge kind + independently provable decision/claim surface;
- production requires edges;
- applicability dispositions;
- Questions and owners;
- omitted obligations;
- invented obligations;
- selected Consumer closure;
- final frontier/completeness state.

Names may differ if semantic identity is equivalent.

### 8.2 Semantic convergence measures

Use separate measures rather than one score:

- **obligation omission recall** against the independent reference set;
- **invention precision** for Capabilities/Authorities/edges not justified by evidence;
- **Authority partition agreement** over reference decision/claim atoms: compare whether atom pairs are grouped/split consistently, rather than comparing Authority names;
- **Capability-set agreement** after semantic matching;
- **dependency-edge precision/recall** after matching semantic Capability identities;
- **applicability confusion matrix** for REQUIRED / NOT_APPLICABLE / UNKNOWN / QUESTION;
- **Question-owner accuracy**;
- **Consumer-closure agreement**;
- **pairwise run convergence** plus **oracle agreement**.

A run set is not reproducible merely because the final status matches. Two runs that both say COMPLETE but derive incompatible Authority/Capability graphs are materially non-convergent.

## 9. Ability × Evidence matrix

Assurance levels are defined in section 10.

| Ability | Strongest current evidence | Oracle | Level | Missing evidence / limitation |
|---|---|---|---|---|
| AB-01 Core structural truth | validators + acceptance + invalid scenarios | O1 | L3 | Property generation could broaden path space |
| AB-02 Engineering Graph topology | validators + cross-layer scenarios + project snapshots | O1/O2 | L4 | Deep graph defect HARN-023 |
| AB-03 Target-state action semantics | validators + Scenario Suite | O1 | L3 | Existing open cross-layer defects still constrain release claim |
| AB-04 Authority boundary formation | boundary research fixtures | O1 | L1/L2 | No raw-evidence discovery/repeated-agent oracle |
| AB-05 Capability discovery | Reference materializer holdouts for known templates | O3 | L5-known-template only | No novel project-specific Capability discovery |
| AB-06 Applicability/Coverage | deterministic validators/scenarios + holdouts | O1/O3 | L3/L5 | Project-fact discovery remains upstream judgement |
| AB-07 Project Authority Assessment | authority bootstrap/migration scenarios | O1 | L3 | No live-agent reconciliation |
| AB-08 Design target selection | profile validators + agent skill contract | O1 | L2 | Canonical docs explicitly say profile completeness remains agent judgement |
| AB-09 Existing-project bootstrap/reconcile | routed skill + downstream validators | O1 | L2 | No behavioral execution eval |
| AB-10 Greenfield bootstrap | greenfield example after graph authored | O1 | L2/L3 | No goal -> agent-built graph E2E |
| AB-11 Source acquisition/completeness | source-set/boundary/coverage scenarios + real slices | O1/O2 | L4 | Source selection itself remains manual/judgement |
| AB-12 Semantic derivation/admission | extensive scenarios, mutations, real defect/control | O1/O2 | L4 | Live semantic oracle corpus still small |
| AB-13 Questions/blockers | deterministic scenarios | O1 | L3 | Agent compliance not directly executed |
| AB-14 Lifecycle/currentness/migration | validators/scenarios | O1 | L3 | HARN-009/HARN-014 and HARN-013 verification state |
| AB-15 Decision/frontier orchestration | validators/scenarios | O1 | L3 | HARN-012 atomic apply remains unresolved |
| AB-16 Agent/method/artifact routing | deterministic router tests | O1 | L2/L3 | Task intent -> chosen operation not real-agent tested; HARN-021 |
| AB-17 Repository realization/projections | validators/scenarios/examples | O1 | L3 | Mostly constructed fixtures |
| AB-18 Consumer distribution | pack/wrapper validators | O1 | L3 | Upgrade identity migration remains EVO-018 research direction |
| AB-19 CI/validation policy | registry/meta-validator/workflows | O1 | L3 | Proves execution policy, not semantic adequacy of suite |
| AB-20 External semantic assurance | expert corpora + live repeated calibration | O4 | L6 on small corpus | Corpus representativeness/drift, provider diversity; EVO-031 |
| AB-21 Real-project portability | NAPMS/Prep + Nutrition research evidence | O2 | L4 | Not enough independent archetypes; several are co-design/regression projects |

## 10. Permanent assurance model

A single percentage should not be used because test count is not a valid denominator.

### 10.1 Evidence maturity ladder

| Level | Meaning |
|---|---|
| L0 NO_EVIDENCE | Ability is asserted but has no executable/inspectable evidence. |
| L1 STRUCTURAL_CONTRACT | Schemas/registries/static shape are validated. |
| L2 DETERMINISTIC_MECHANISM | The local mechanism has positive/negative/invariant executable evidence. |
| L3 CROSS_LAYER_SCENARIO | The ability is exercised across its material Harness boundaries, including failure reactions. |
| L4 REAL_PROJECT_REGRESSION | The mechanism has passed on accepted real-project truth. |
| L5 INDEPENDENT_HOLDOUT | A frozen materially different project/domain not used to design the mechanism passes a predeclared oracle. |
| L6 REPRODUCIBLE_AGENT_OR_SEMANTIC | Judgement-dependent behavior converges across clean-context runs and agrees with an independent semantic oracle. |
| L7 CALIBRATED_OPERATIONAL | Representative recurring calibration/drift policy exists for the deployed evaluator/agent population. |

The ladder is not a claim that every ability must reach L7. Deterministic algorithms normally stop at L3/L4 plus selected holdouts. Agent discovery and semantic evaluator responsibilities need the higher levels.

### 10.2 Required evidence facets

Each ability should also record independent facets:

- oracle class O0..O4;
- failure classes exercised;
- synthetic vs real vs holdout evidence;
- deterministic vs judgement-dependent execution;
- replay/reproducibility status;
- supported scale envelope;
- last evidence commit/run.

This prevents gaming the model by adding many tests that all exercise the same oracle/failure class.

### 10.3 Release claim rule

A future version may say “Harness performs its intended responsibilities with sufficient evidence” only when:

1. every release-critical Ability has an explicit observable contract;
2. every material failure class is mapped to at least one evidence class;
3. deterministic abilities reach at least cross-layer evidence for their critical paths;
4. judgement-dependent bootstrap/discovery abilities have repeated clean-context holdout evidence;
5. provider-backed semantic judgements are calibrated on a representative corpus appropriate to their use;
6. no open P0 functional defect or unresolved false-COMPLETE path remains;
7. the exhaustive deterministic gate is green on the exact integration candidate.

This is a vector release claim, not an average.

## 11. Scenario Suite quality

### Strengths

Scenario Suite is substantially better than a conventional regression directory:

- explicit dimensions;
- coverage requirements;
- registered drivers;
- invariant assertions rather than whole-output snapshots;
- mutation support;
- benchmark metrics;
- real-project execution type;
- cross-layer composition.

### Assurance weaknesses

1. **Catalog self-completeness is not independently proven.** A behavior absent from the catalog cannot make coverage fail.
2. **Discovery is allowed but not required as a stage value.** catalog-v1.yaml lists discovery in the stage taxonomy, but required_dimension_values does not require at least one discovery-stage scenario.
3. **Project-archetype distribution is not release-gated.** The catalog lists archetypes, but it does not require coverage for each or for a risk-selected subset.
4. **agent-evaluation is not real-agent execution.** AUD-012/EVO-001 already records this.
5. **min_scenarios: 1 proves presence, not diversity.** This is appropriate for many deterministic contracts but insufficient for judgement-heavy behavior.
6. **covers is scenario-authored.** The current suite can detect unknown coverage claims, but not whether a scenario's oracle is sufficiently independent for the ability it claims.
7. **Scenario ownership is behavior-requirement centric, not Harness-ability centric.** There is no independent mapping from AB-like abilities to mandatory scenarios/evals.

The suite has not become a random regression dump, because it has taxonomy and coverage ownership. The risk is different: the taxonomy can be internally complete while incomplete relative to Harness purpose.

## 12. Real projects as evidence

| Project/evidence | Current value | Holdout status |
|---|---|---|
| NAPMS | Strong real-project graph/derivation/regression/adoption evidence; one real semantic-loss defect was detected | Not independent for mechanisms/reference boundaries materially shaped by NAPMS |
| Prep | Real-project graph/slices; project-specific semantic evidence and external Scenario protocol use | Strong regression/portability evidence, not blind discovery holdout |
| Nutrition | Important design/research/portability input and source for Authority/reference decisions | Not independent for those decisions because it contributed to their design |
| Greenfield CSV | Good deterministic greenfield fixture and derivation chain | Constructed acceptance fixture, not holdout |
| User-facing/frontend fixtures | Good frontend structural/semantic regression coverage | Constructed fixtures |
| Browser extension / Stripe webhook / Airflow / Prometheus reference holdouts | Materially different external domains with frozen Reference Model | Strongest current independent holdout family, but only for declared facts -> known template materialization |

### 12.1 Minimum archetype portfolio

Do not require every possible project category. Select archetypes that activate materially different failure modes:

- tiny stateless CLI/library;
- stateful CRUD/API service;
- concurrent/event-driven integration service;
- domain-rich modular application;
- user-facing/full-stack application;
- data pipeline/batch workflow;
- legacy/migration system;
- multi-service/monorepo or plugin/extension topology;
- security/regulated-heavy case when relevant to promotion claims.

At least some should be frozen holdouts that did not participate in mechanism design.

## 13. Blind-spot status

| Blind spot | Current status |
|---|---|
| Capability omission | Downstream omission checks are strong; discovery-time omission remains weak |
| Capability overproduction | Partial for Reference Model; weak for agent-created project capabilities |
| Wrong Capability granularity | Semantic rules exist; no repeated discovery eval |
| Wrong Authority boundary | Research fixtures only; discovery-time boundary quality unproven |
| Missing dependency | Strong once semantic surfaces/graph are declared; discovery-time missing edge remains partial |
| Unnecessary dependency | Some boundary research/metamorphic evidence; not broad |
| Wrong N/A | Strong deterministic handling after evidence exists |
| Silent UNKNOWN -> NOT_APPLICABLE | Explicit fail-closed rules are well covered |
| Wrong Consumer closure | Strong deterministic evidence |
| Agent inventing knowledge | Skills/strict admission constrain it; no real-agent behavioral measurement |
| Agent uses downstream decisions before prerequisites | Strong graph/context/admission guards |
| Semantic drift | Strong downstream currentness/derivation evidence; evaluator coverage limited |
| Stale knowledge | Strong but existing HARN-009/HARN-014 and HARN-013 verification state remain |
| Reference-model bias | External holdouts help, but novel project Capability/Authority discovery is untested |
| Regression after reference-catalog change | Reference evolution/regressions exist |
| Migration errors | Consumer/reference migration partial; generic graph migration still open |
| Different agents/models produce incompatible graphs | Not measured |
| Works only on fixture vocabulary | Partially challenged by external domains; live-agent raw-repo behavior untested |
| Fixture encodes the answer | Material risk for synthetic/hand-authored graph tests; mitigated only by O2/O3/O4 evidence |

## 14. Minimum sufficient assurance graph

The minimal suite should not maximize test count. Each layer closes a distinct failure class.

~~~text
1. local structural + invariant checks
   closes malformed state / local safety regressions
        ↓
2. deterministic mechanism contracts
   closes algorithmic state-transition defects
        ↓
3. cross-layer Scenario contracts
   closes composition / precedence / invalidation defects
        ↓
4. existing-project + greenfield behavioral E2E
   closes procedure integration / bootstrap failures
        ↓
5. frozen independent project holdouts
   closes fixture/reference vocabulary overfit
        ↓
6. repeated clean-context agent discovery eval
   closes non-reproducible / omitted / invented project-model judgement
        ↓
7. semantic evaluator calibration where judgement is delegated
   closes evaluator FP/FN / drift risk
        ↓
8. CI policy + exact integration-candidate full gate
   proves the selected evidence actually ran for the release candidate
~~~

Layer 4 must exercise the actual routed procedure, not call the downstream deterministic functions directly.

Layer 5 must freeze the oracle before execution.

Layer 6 is necessary only for judgement-dependent abilities; it should not be imposed on deterministic Core logic.

## 15. Critical assurance gaps

These priorities are audit-local assurance priorities, not new HARN severities.

### P0 — release-claim blockers

**ASG-01 — Project-model formation is not end-to-end proven.**

No executable evidence currently establishes selected-scope unfamiliar repository -> fresh routed agent -> project-specific Authorities/Capabilities/dependencies -> validated Project Engineering Graph. This prevents a strong claim about bootstrap/discovery usefulness.

**ASG-02 — The assurance system has no independent Ability-to-Evidence denominator.**

Scenario/validator inventory is excellent at proving that registered checks exist and run. It does not prove that every Harness responsibility has been registered as an assurance obligation. Therefore “all tests green” can still coexist with an unmodelled ability gap.

### P1 — important assurance gaps

**ASG-03 — Real-agent reproducibility is unmeasured.**

There are no repeated clean-context runs measuring semantic convergence, capability/authority invention, omission, or graph incompatibility.

**ASG-04 — Oracle independence is uneven.**

Most deterministic tests correctly use hand-authored contract oracles, but semantic/discovery generalization often relies on fixtures created alongside the mechanisms. Stronger O3/O4 evidence exists only for narrower areas.

**ASG-05 — Scenario Suite does not gate discovery/archetype coverage.**

Discovery exists as a taxonomy value but is not a required stage; project archetype values are not required coverage dimensions; agent-evaluation remains structured/synthetic.

**ASG-06 — Existing functional open items still bound assurance.**

HARN-009, HARN-010, HARN-012, HARN-014, HARN-021, HARN-022 and HARN-023 remain open/decision gaps, while HARN-013 is still IN_PROGRESS at the audit baseline. Even a stronger test model must not hide those concrete functional states.

### P2 — strengthening gaps

**ASG-07 — Scale envelope is not defined.**

Already tracked by HARN-023/EVO-032.

**ASG-08 — Provider/model diversity is insufficient for broad semantic-evaluator claims.**

Current live evidence is useful but narrow and is already bounded by EVO-031.

**ASG-09 — Some files named “eval” validate benchmark declarations rather than execute the behavior under evaluation.**

This is primarily a diagnosability/taxonomy issue but can cause maintainers to overestimate evidence strength.

### P3 — presentation/ergonomics

**ASG-10 — Evidence class/oracle provenance is not visible in one place.**

A maintainer must read validator/scenario/research implementation to distinguish structural fixture validation, deterministic execution, real regression and independent holdout.

## 16. Minimal correction roadmap

No implementation is performed by this audit.

### Step 1 — highest information experiment

Create one frozen unfamiliar-repository fixture designed to falsify current assumptions.

It must contain:

- one project-specific required Capability absent from Reference Model templates;
- one Authority boundary where an attractive reference grouping is intentionally wrong for the project;
- one irrelevant reference concern that lexical similarity could over-generate;
- enough accepted project evidence for an independent reviewer to author the expected semantic model.

Run the real Consumer startup route with a fresh agent.

This one experiment can simultaneously falsify:

- capability discovery;
- authority boundary discovery;
- reference-model bias resistance;
- omission resistance;
- over-generation control;
- operation/skill execution compliance.

Do not add new discovery algorithms before this experiment.

### Step 2 — repeat the same experiment in clean contexts

Run 3-5 times with identical frozen inputs and normalize outputs semantically. Measure:

- omissions;
- inventions;
- Authority partition agreement;
- capability/edge agreement;
- Question ownership;
- final closure/frontier agreement.

If the runs do not converge, treat that as evidence before changing prompts/skills.

### Step 3 — add the Ability-to-Evidence registry/model

Only after the first experiment clarifies the real boundaries, create a small machine-readable assurance registry:

~~~text
ability
-> observable contract
-> material failure modes
-> required evidence classes
-> acceptable oracle class
-> current evidence refs
-> release-critical?
~~~

Scenario Suite requirements and CI checks should reference this model rather than becoming the denominator themselves.

### Step 4 — add two behavioral E2E paths

Minimum:

- existing project with reusable project-owned graph/projection;
- greenfield/minimal project with no prior Harness realization.

Both should execute routed skills, not merely call graph evaluators.

### Step 5 — promote a small holdout portfolio

Freeze materially different projects before running them. Prefer archetypes that add new failure modes rather than more examples of the same service shape.

### Step 6 — widen semantic calibration only where evidence shows value

Extend evaluator/provider/model variation after discovery/agent boundaries are measurable. Do not spend provider budget to compensate for missing deterministic or human-authored oracles.

## 17. Answers to the audit quality questions

1. **What tasks must Harness solve?** See the 21 observable abilities in section 3, separated into project semantic ownership, deterministic Harness responsibilities and agent-enabled procedures.
2. **Which have executable evidence?** Most deterministic abilities do; agent model-formation/discovery does not have live execution evidence.
3. **How strong is it?** Strongest at L3/L4 for deterministic mechanisms, L5 for Reference Model known-template holdouts, L6 only for narrow semantic evaluator calibration.
4. **What is only synthetic?** Most Core/graph/decision/coverage behavioral cases and all current Authority/Capability boundary discovery fixtures.
5. **What is real-project proven?** Selected NAPMS/Prep integration and semantic-derivation/source-assurance paths; Nutrition contributes research/design evidence.
6. **What has independent holdouts?** Reference Model materialization has the strongest frozen cross-domain holdouts.
7. **Which agent/semantic abilities lack reproducible checks?** Task-intent route selection, source selection, novel Capability discovery, Authority boundary discovery and project-graph construction.
8. **Can Harness discover a new Capability absent from templates?** The architecture permits project-specific Capabilities, but no executable repeated-agent evidence currently proves discovery quality.
9. **Can it reproducibly discover an Authority boundary?** Not currently demonstrated.
10. **Is raw repository -> Project Engineering Graph proven E2E?** No. Also, the valid contract is selected-scope agent bootstrap, not autonomous repository-wide prose mining.
11. **Which failure modes cannot the current suite detect reliably?** Systematic agent omission/invention during model formation, incompatible graphs across clean runs, catalogue-level assurance omission, and broad reference-vocabulary overfit outside current holdouts.
12. **What is the minimum release assurance suite?** The eight-layer graph in section 14, with live-agent layers only for judgement-dependent responsibilities.
13. **What should “this Harness version performs its purpose” mean?** Every release-critical ability has an observable contract, material failure modes have adequate evidence with stated oracle strength, judgement-dependent abilities have independent reproducible evidence, open false-COMPLETE defects are absent, and the exact candidate passed its required deterministic gate.

## 18. Audit dispositions

No new HARN defect is allocated from this pass.

Two non-defect research/assurance directions are persisted:

- EVO-033 — project-model discovery assurance;
- EVO-034 — ability-to-evidence assurance model.

Existing items remain relevant and are not duplicated:

- EVO-001 — real-agent behavioral execution evals;
- EVO-019 — Reference Model / Coverage ownership;
- EVO-031 — calibration representativeness/drift;
- EVO-032 — scale envelope;
- HARN-014 — generic project graph migration;
- HARN-021 — internal operation authorization;
- HARN-023 — deep graph recursion.
