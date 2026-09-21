# Research — Hierarchical Engineering Concern Catalog v1

Status: research only. Not canonical.

## Conclusion

The useful unit is a **semantic leaf concern**, not a document, Authority, Capability, standard clause, or generic quality label.

A scalable model therefore needs four distinct layers:

1. **Canonical concern tree** — stable semantic review subjects such as security.authorization, reliability.recovery, operability.logging.
2. **Cross-cutting lenses** — alternative navigation/taxonomy views (not state owners), especially Quality.
3. **Project projection** — applicability, coverage, evidence, blockers, provenance, freshness.
4. **Presentation policy** — aggregation and progressive disclosure.

This keeps one coverage state per semantic concern while allowing several standards and viewpoints to reference it.

## Why v0 is too coarse

Rows such as quality.attributes, reliability.concurrency, security.analysis and operability.observability combine multiple independently decidable questions.

A row may currently be COVERED because one artifact exists although several important subtopics are unassessed. This is strongest in quality because ISO quality models intentionally span security, reliability and human interaction as well as performance and maintainability.

The inverse problem also occurs: Nutrition has accessibility, consistency and provenance knowledge distributed across requirements, interface, data and verification artifacts, yet coarse rows are UNASSESSED because no dedicated artifact owns the umbrella term.

## Concept model

### Concern

A stable semantic question useful for project completeness/navigation.

Properties:
- has stable id and parent;
- can be independently applicable or non-applicable;
- can be covered by multiple accepted knowledge sources;
- can have blockers and lifecycle state;
- does not imply one artifact.

### Quality attribute

A property of the product/system that may require measurable or qualitative constraints.

It is represented either:
- as a canonical concern where it has independent engineering semantics (for example reliability.recovery), or
- as a quality-only leaf where no stronger existing top-level concern owns it (for example quality.performance.latency).

Quality is therefore a **lens**, not a second source of state.

### Requirement

Project-specific normative statement. A requirement can cause one or many concerns to become applicable and may be evidence for coverage.

### Risk

Potential undesirable outcome with likelihood/impact/uncertainty. Risk can cause applicability or prioritization but is not a concern itself.

### Analysis lens

Reusable way to inspect concerns, such as STRIDE, ISO 25010, NIST CSF, WCAG or SRE. A lens maps onto concerns; it does not own project truth.

### Capability

Harness producer/consumer contract. Capabilities are implementation-independent knowledge outputs used to derive coverage.

### Verification dimension

The evidence question "how do we prove this concern?" Verification concerns reference the semantic concern being verified.

## External taxonomy findings

### ISO/IEC 25010:2023 and ISO/IEC 25019:2023

ISO 25010:2023 defines a product quality model with nine characteristics and sub-characteristics. ISO 25019:2023 separately defines quality-in-use. These are strong vocabulary sources, but using the hierarchy literally as the Harness concern tree would duplicate existing Security, Reliability and Human Interface ownership.

Research mapping:
- Functional suitability -> intent.behavior + verification.functional.
- Performance efficiency -> quality.performance.*.
- Compatibility -> interface compatibility + interoperability/coexistence leaves.
- Interaction capability -> interface.human.*.
- Reliability -> reliability.*.
- Security -> security.*.
- Maintainability -> quality.maintainability.* plus engineering evidence.
- Flexibility -> quality.flexibility.*.
- Safety -> optional specialized.safety.

Sources:
- https://www.iso.org/standard/78176.html
- https://www.iso.org/standard/78177.html

### ISO/IEC/IEEE 42010:2022

42010 reinforces the distinction between stakeholder concerns, viewpoints/views and the architecture description. Harness should therefore keep Engineering Concern broader than architecture Viewpoint. A concern may reference an architecture viewpoint when appropriate, but governance, verification, supply chain and privacy should not be forced into architecture views.

Source:
- https://www.iso.org/standard/74393.html

### arc42 / Q42

arc42's strongest contribution is not another mandatory hierarchy but **quality scenarios**: context/stimulus, response and measurable acceptance criteria. Q42 also demonstrates a pragmatic non-exclusive quality graph rather than pretending every quality belongs cleanly in one tree.

Use in Harness:
- concern taxonomy for recall;
- quality scenarios as requirement/evidence;
- scenario type (usage/change/failure) as metadata, not concern identity.

Sources:
- https://docs.arc42.org/section-10/
- https://quality.arc42.org/

### NIST SSDF

SSDF groups secure software development into Prepare the Organization, Protect the Software, Produce Well-Secured Software and Respond to Vulnerabilities. These are lifecycle/practice lenses, not product-security characteristics.

Use:
- map SSDF practices primarily to security.secure-development, dependency.*, delivery.*, verification.security and security.vulnerability-management.

Source:
- https://csrc.nist.gov/pubs/sp/800/218/final

### NIST CSF 2.0

CSF 2.0 organizes cybersecurity outcomes around Govern, Identify, Protect, Detect, Respond and Recover. This is useful as a security-risk/operations lens.

Use:
- Govern -> governance + security policy;
- Identify -> boundaries/assets/dependencies;
- Protect -> security controls;
- Detect -> operability telemetry/security monitoring;
- Respond -> incident/vulnerability response;
- Recover -> reliability.recovery + continuity.

Do not duplicate these as six project artifacts.

Source:
- https://www.nist.gov/cyberframework

### OWASP ASVS / SAMM

ASVS is useful for application-security verification/control taxonomy. SAMM is useful for organizational software-security practices. Neither should become the baseline concern tree.

Use:
- ASVS -> leaf-level security/verification mappings when a web/application-security specialization is active.
- SAMM -> secure-development maturity lens, especially governance/design/implementation/verification/operations.

Sources:
- https://owasp.org/www-project-application-security-verification-standard/
- https://owaspsamm.org/model/

### STRIDE

STRIDE categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) are threat-analysis categories. They map naturally to identity, integrity, accountability, confidentiality, availability/abuse and authorization.

STRIDE is therefore a lens under security.threat-analysis, not six baseline concerns.

### Google SRE

SRE makes reliability operationally concrete through SLIs/SLOs/error budgets. Common indicators include latency, error rate, throughput and availability; monitoring guidance emphasizes latency, traffic, errors and saturation.

Use:
- reliability.availability owns availability semantics;
- quality.performance owns latency/throughput;
- operability.metrics owns measurement mechanics;
- SLOs/error budgets are requirements/control-loop artifacts linking those concerns.

Sources:
- https://sre.google/sre-book/service-level-objectives/
- https://sre.google/sre-book/monitoring-distributed-systems/

### OpenTelemetry

OpenTelemetry supports traces, metrics, logs and baggage as telemetry signals. These are observability mechanisms, not quality attributes.

Use:
- operability.logging
- operability.metrics
- operability.tracing
- correlation context spanning signals.

Source:
- https://opentelemetry.io/docs/concepts/signals/

### Twelve-Factor App

Twelve-Factor is a useful SaaS/operability/deployment lens:
- dependency declaration;
- config;
- backing services;
- build/release/run;
- stateless processes;
- concurrency;
- disposability;
- dev/prod parity;
- logs;
- admin processes.

It should activate where the deployment shape resembles a service. It is not universal project policy.

Source:
- https://12factor.net/

### WCAG 2.2

WCAG organizes web accessibility under Perceivable, Operable, Understandable and Robust with testable success criteria.

Use:
- interface.human.accessibility is the canonical concern;
- WCAG level/success criteria become obligation/requirement/verification metadata;
- do not create one top-level concern per WCAG principle.

Source:
- https://www.w3.org/WAI/WCAG22/Understanding/intro

### W3C Internationalization

W3C i18n separates internationalization (designing for adaptation) from localization. Relevant leaves include language/script, directionality, character encoding, numbers/dates/times, names and cultural formatting.

Use:
- interface.human.i18n with optional expanded children only when activated.

Source:
- https://www.w3.org/International/questions/qa-i18n

### SLSA

SLSA provenance is verifiable information describing where, when and how artifacts were produced; current tracks distinguish provenance/integrity strength.

Use:
- delivery.provenance
- delivery.integrity
- dependency.trust

Reproducible build is related but not identical to provenance.

Source:
- https://slsa.dev/spec/v1.2/provenance

### Privacy frameworks

NIST Privacy Framework uses Identify-P, Govern-P, Control-P, Communicate-P and Protect-P and explicitly describes itself as risk-based rather than a universal checklist.

Use:
- governance.privacy as canonical concern;
- processing inventory/classification -> data.classification;
- control/transparency/individual participation can be expanded by a privacy specialization.

Source:
- https://www.nist.gov/privacy-framework

## Quality decomposition decision

### Quality is an umbrella/index

Quality should be rendered as an overview page/lens across canonical concern leaves.

It should not own duplicate states for:
- Security;
- Reliability;
- Human Interface/Accessibility;
- Safety.

It owns only quality attributes that otherwise lack a semantic home:
- performance: latency, throughput, resource efficiency, capacity;
- compatibility: interoperability, coexistence;
- maintainability: modularity, reusability, analysability, modifiability, testability;
- flexibility: adaptability/portability, scalability, installability, replaceability.

Functional suitability is projected from requirements + functional verification rather than recreated as another owner.

### Consequence

"Quality = COVERED" is only valid as an aggregate display statement over all **applicable** quality-lens leaves.

A project may legitimately show:

Quality PARTIAL
- Performance COVERED
  - Latency NOT_APPLICABLE (explicit no numeric target for scope)
  - Throughput NOT_APPLICABLE
  - Resource efficiency UNASSESSED
  - Capacity NOT_APPLICABLE
- Reliability PARTIAL -> reliability.*
- Security COVERED -> security.*
- Maintainability COVERED
- Interaction PARTIAL -> interface.human.*

No independent QUALITY artifact is required.

## Parent aggregation

Parent state is derived from direct leaf descendants after specialization/applicability resolution.

Rules, in order:

1. If every descendant is NOT_APPLICABLE -> NOT_APPLICABLE.
2. If every descendant is UNASSESSED -> UNASSESSED.
3. If every descendant is DEFERRED -> DEFERRED.
4. If every applicable descendant is COVERED and remaining descendants are NOT_APPLICABLE -> COVERED.
5. If any descendant is STALE -> STALE when stale coverage affects required evidence; otherwise PARTIAL with stale marker.
6. If any descendant is BLOCKED -> BLOCKED when blocker prevents required parent completion; otherwise PARTIAL.
7. If any applicable descendant is MISSING -> MISSING when no covered sibling can make the parent semantically complete; otherwise PARTIAL.
8. Any heterogeneous mix not captured above -> PARTIAL.

Important: PARTIAL is a **display-only aggregate state**. It is not a legal leaf state.

## Progressive disclosure

Default collapsed view shows top-level parents.

Expand automatically when:
- descendants contain MISSING, BLOCKED, STALE or UNASSESSED;
- child states differ;
- parent is COVERED but evidence is split across materially different artifacts/Authorities and navigation benefit is high;
- a parent is PARTIAL;
- freshness differs among applicable children.

Keep collapsed when:
- parent is UNASSESSED and no descendant has evidence;
- parent is NOT_APPLICABLE and one accepted parent applicability decision semantically excludes the full subtree;
- parent is DEFERRED with one accepted deferral applying to the full subtree;
- all applicable children are COVERED by one coherent evidence bundle and no child-specific navigation is useful.

Always support fully-expanded output.

A collapsed NOT_APPLICABLE/DEFERRED parent must carry the evidence/rationale that justifies inheritance. If exclusion applies only to some children, expand.

## Activation depth

Default baseline depth should stop at independently decidable leaves.

Do not expand merely because a standard has more levels.

Expand a leaf into deeper children when at least one condition holds:
- children can have different applicability states;
- children can be covered by different Authorities/Capabilities;
- one child can block implementation while another is satisfied;
- a standard/obligation requires separate verification;
- project evidence already distinguishes them;
- users need separate navigation.

This avoids hundreds of rows for small projects.

## Provenance model

No manual prose chain should be required when graph data can derive it.

Recommended derived chain:

Concern
-> concern-to-capability mapping
-> Capability provider
-> Authority + CanonicalArtifact
-> artifact depends_on/prerequisites
-> upstream requirements/decisions
-> Consumers requiring capability
-> verification capabilities/evidence

Explicit project data is needed only for:
- applicability decision/rationale not derivable from accepted knowledge;
- mapping where generic concern-to-capability semantics are ambiguous;
- externally imposed obligation interpretation.

Example:

security.identity
  applicable because: accepted external OIDC identity boundary
  caused by: FIRST-MVP-REQUIREMENTS + SECURITY-ARCHITECTURE decision
  covered by: engineering.architecture.security / SECURITY-ARCHITECTURE
  consumed by: interface, operability, implementation, verification
  freshness: derived from provider/prerequisite lifecycle

## Freshness

Coverage and artifact existence are independent dimensions.

freshness:
- CURRENT: lifecycle evaluation proves prerequisites/baseline are current.
- STALE: lifecycle evaluation proves provider accepted against superseded prerequisite/baseline.
- UNKNOWN: lifecycle metadata cannot prove either.

Never use file date/commit date as freshness.

If required coverage is stale, leaf state may render STALE while preserving "artifact exists" as evidence metadata.

## Automatic derivation experiment

Three classes of inputs:

### A. Directly derivable
- CapabilityId -> provider artifact;
- provider -> Authority;
- artifact -> path;
- artifact/capability -> Consumers;
- unresolved Question -> BLOCKED;
- missing required provider -> MISSING;
- lifecycle metadata -> CURRENT/STALE/UNKNOWN;
- explicit project N/A capability/decision -> NOT_APPLICABLE.

### B. Explicit mapping, then derivable
- concern -> one/many CapabilityIds or knowledge_kind;
- quality lens -> canonical concern refs;
- artifact kind -> concern when semantics are declared in catalog mapping.

### C. Human/accepted applicability decision
- privacy applies to this data?
- accessibility conformance obligation?
- safety classification?
- external legal/contractual obligation?
- whether a qualitative requirement is sufficient or a numeric target is required.

Estimated current pilots:

| Project | Direct automatic | Explicit concern mapping then automatic | Human applicability |
|---|---:|---:|---:|
| NAPMS | ~58% | ~27% | ~15% |
| Nutrition | ~51% | ~31% | ~18% |

These are research estimates by leaf classifications, not measured production telemetry. The largest remaining manual area is applicability, not provider/path lookup.

## NAPMS findings

The coarse v0 "quality.attributes = COVERED" hid a mixed picture:

- correctness and maintainability constraints are explicit;
- numeric latency, throughput, availability and scale targets are explicitly NOT_REQUIRED for first MVP;
- resource-efficiency remains unassessed;
- reliability consistency/failure semantics are strong;
- recovery/continuity is not covered by the same evidence;
- observability logging/correlation/dependency diagnostics are covered;
- metrics/SLO alerting is intentionally light because numeric targets are not required;
- threat analysis covers all STRIDE categories at design level;
- vulnerability-management and broader secure-development lifecycle are not established by the threat-model artifact alone.

Therefore the refined map should show mixed child states instead of a single COVERED parent.

## Nutrition findings

Several v0 UNASSESSED rows were too coarse:

- accessibility has accepted baseline requirements and frontend verification evidence, though no formal WCAG conformance claim;
- data integrity, consistency, provenance and reproducible standard-data evidence are explicit;
- local-browser security architecture is covered for the accepted trust boundary;
- security threat analysis remains unassessed;
- reliability has consistency/failure-semantics evidence but no availability/recovery objectives;
- operability has some failure/diagnostic semantics, but no dedicated logging/metrics/tracing/health model;
- privacy applicability cannot be safely inferred merely because profile data exists; it needs accepted classification/privacy analysis.

## Tiny ETL stress result

The hierarchy remains usable if:
- parent N/A inheritance can collapse whole irrelevant subtrees;
- specializations stay inactive by default;
- semantic leaves can be satisfied by lightweight requirements rather than documents.

For the synthetic CSV ETL:
- interface.human -> NOT_APPLICABLE collapses accessibility/i18n/usability;
- security identity/authorization -> NOT_APPLICABLE under accepted local trust scope;
- reliability distributed subtopics -> mostly NOT_APPLICABLE, while failure semantics/determinism remain relevant;
- operability can be lightweight: exit status + error summary, without metrics/tracing/alerting;
- data quality/reproducibility remain relevant even without persistence.

This is substantially smaller than rendering every ISO/OWASP/WCAG leaf.

## Dashboard proposal

Generated package:

docs-generated/engineering-map/
- README.md                      # collapsed top-level map and legend
- coverage-map.yaml             # complete machine projection
- coverage-map-expanded.md      # full tree
- quality.md                    # quality lens
- provenance.md                 # concern -> reason/evidence/consumers
- artifacts.md                  # artifact -> concerns/reasons
- gaps.md                       # MISSING/BLOCKED/STALE/UNASSESSED
- concerns/
  - security.md
  - reliability.md
  - operability.md
  - data.md
  - interface.md
  - verification.md
  - ...

README.md should be the first page of Human Documentation Projection.

## Validator rules for prototype

P0:
- leaf state must be one of the seven semantic states;
- parent state must not be persisted;
- NOT_APPLICABLE requires evidence/rationale;
- DEFERRED requires rationale + owner + reopening condition;
- COVERED requires semantic evidence (capability/artifact/accepted requirement), not only path;
- STALE requires lifecycle evidence;
- referenced concern ids must exist;
- lens ids must resolve to canonical leaves.

P1:
- warn when COVERED evidence is only a filename;
- warn when umbrella parent is explicitly mapped while heterogeneous descendants exist;
- warn when full subtree is expanded under inherited N/A/deferred decision without contradictory evidence.

## What to prototype next

1. Keep catalog and map research-only.
2. Use v1 concern ids in refined pilot maps.
3. Add renderer/validator that:
   - loads catalog + project rows;
   - derives parent states;
   - validates evidence rules;
   - applies progressive disclosure;
   - renders Markdown.
4. Next experiment should derive rows from actual Engineering Graph/Core plus a small explicit applicability overlay rather than hand-authored complete rows.
5. Only after that experiment measure real automation percentage and decide whether a concern-to-capability mapping registry belongs in Harness.
