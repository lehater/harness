# Security design boundary research

Status: research hypothesis. This document does not change Harness Core or canonical Authority ownership.

## Research question

What security knowledge must be accepted before IMPLEMENTATION, which Authority owns each decision, and how should Harness prevent an implementation agent from inventing security-critical semantics?

The investigation deliberately does not assume that "security" is one Authority. It tests the existing SECURITY-ARCHITECTURE and SECURITY-ANALYSIS boundaries and looks for residual decision classes only when the atomicity test requires them.

## External reference model

The research uses external frameworks as coverage lenses, not as Harness ontology:

- NIST SP 800-218 SSDF: secure development practices must be integrated into the SDLC rather than treated as a late implementation activity.
- NIST CSF 2.0: security is a risk/outcome space and does not prescribe one realization mechanism.
- CISA Secure by Design: security outcomes should be designed into products and secure defaults should not shift avoidable burden to users.
- OWASP ASVS and related OWASP guidance will be used as control/verification coverage, not as automatic project requirements.

A checklist item is not automatically an Authority, Capability, requirement, or blocking Question.

## Candidate decision classes and ownership hypotheses

| Decision class | Preliminary owner | Security role |
| --- | --- | --- |
| Who may perform a business action | PRODUCT / DOMAIN | Own the semantic entitlement or policy. |
| Identity/trust boundaries and authentication architecture | SECURITY-ARCHITECTURE | Select trusted identities, admission boundaries and enforcement structure. |
| Authorization enforcement placement | SECURITY-ARCHITECTURE with DOMAIN/PRODUCT semantics upstream | Preserve semantic policy while selecting enforcement boundary. |
| Public 401/403/error representation | INTERFACE-DESIGN | Represent accepted security outcomes externally. |
| Session/token lifecycle | SECURITY-ARCHITECTURE, with interface/runtime consequences | Own security lifecycle unless product semantics independently constrain it. |
| Sensitive-data classification/disclosure rule | SECURITY-ARCHITECTURE or project security policy; DATA/INTERFACE/OPERABILITY consume it | Security owns protection requirement, consumers own their representation/evidence. |
| Physical persistence representation | DATA-DESIGN | Security supplies protection constraints; Data owns storage realization contract. |
| Secrets source/topology | SECURITY-ARCHITECTURE + SYSTEM-ARCHITECTURE where deployment topology matters | Configuration mechanics do not become a separate Security Authority. |
| Encryption/key-management requirement | SECURITY-ARCHITECTURE | Own protection/trust requirement; private library/API mechanics remain implementation freedom. |
| Threat enumeration and control coverage | SECURITY-ANALYSIS | Analyze accepted design, identify threats/control gaps, route missing decisions upstream. |
| Security verification evidence | VERIFICATION-DESIGN / TEST-DESIGN | Prove accepted controls/semantics without redefining them. |
| Diagnostic redaction/security event evidence | OPERABILITY-DESIGN | Project accepted security constraints into runtime evidence. |
| Dependency/supply-chain development discipline | ENGINEERING-POLICY unless architecture-specific | Cross-cutting secure-development constraint rather than product security semantics. |

## Atomicity hypotheses

### SECURITY-ARCHITECTURE

Candidate responsibility: own security-specific trust, identity, admission, protection and enforcement structure derived from accepted product/domain/system truth.

It must not own:
- business entitlement semantics merely because they are security-sensitive;
- HTTP/UI representation;
- physical data schema;
- diagnostic signal design;
- test mechanics;
- generic secure coding rules;
- threat analysis as if analysis itself selected architecture.

Atomicity to validate:
1. semantic cohesion: trust/protection/enforcement structure;
2. independent change: security structure can change behind stable product/domain contracts;
3. public contract: downstream Interface/Data/Component/Operability/Verification/Implementation consume its constraints.

### SECURITY-ANALYSIS

Candidate responsibility: analyze accepted design against credible threats, abuse paths and required controls; establish coverage and create Questions when accepted design is insufficient.

It must not silently repair the design. A discovered missing authorization rule, trust boundary, disclosure rule or resilience requirement is routed to its semantic owner.

Atomicity to validate:
1. semantic cohesion: threat/control coverage over an accepted design baseline;
2. independent change: threat knowledge and coverage can evolve without directly becoming architecture;
3. public contract: findings/coverage and blocking Questions consumed by upstream owners and verification/implementation readiness.

## Pre-implementation blocking Questions

A security Question should block IMPLEMENTATION when coding would otherwise have to invent a security-critical externally meaningful or trust-boundary decision. Candidate classes:

- actor/identity or protected-action semantics are ambiguous;
- trust boundary or authentication source is unresolved;
- authorization semantics or enforcement responsibility is unresolved;
- sensitive-data classification/disclosure policy is missing where protected data crosses a boundary;
- secret/credential lifecycle or source is required but undefined;
- session/token lifecycle affects accepted behavior but is undefined;
- fail-open versus fail-closed behavior is undecided;
- security-relevant state change lacks required integrity/atomicity semantics;
- required encryption/key ownership or protected transport boundary is undecided;
- threat analysis finds a material control gap whose owner has not accepted a resolution;
- a security verification oracle cannot be derived without inventing upstream semantics.

Normally non-blocking implementation freedoms include private exception classes, crypto/library API syntax after algorithm/protocol constraints are settled, middleware/helper structure, framework-specific guard syntax, test framework mechanics and internal naming.

## Security Analysis is not an OWASP checklist Authority

External catalogs provide coverage prompts. Harness must distinguish:

1. applicability: does this threat/control concern exist for the accepted system?
2. ownership: which Authority owns the semantic decision?
3. analysis: is accepted design adequately covered?
4. realization: what implementation freedom remains?
5. evidence: how will Verification/Test Design prove it?

Importing every external control as a mandatory Capability would create false requirements and violate project-specific applicability.

## Candidate Harness mechanics

Current hypothesis: no new Core entity is required.

Existing primitives are sufficient:
- Authority owns the decision boundary;
- Capability expresses accepted security knowledge;
- CanonicalArtifact materializes it;
- Question represents unresolved security gaps;
- prerequisites propagate closure;
- Engineering Policy can hold normative secure-development constraints;
- Verification/Test Design owns proof.

Potential reusable skills, subject to validation:
- security-architecture: produce project-specific trust/protection/enforcement contract without stealing upstream semantics;
- security-analysis: threat/control coverage and gap routing against accepted design.

Do not add SECURITY-POLICY, THREAT, CONTROL, ASSET or RISK as Core entities unless pilots show that ordinary artifacts/capabilities/questions cannot preserve necessary semantics.

## Validation plan

Use two materially different cases in separate project branches.

### Nutrition Management

Useful pressure points:
- local CLI trust boundary;
- imported/provider data;
- local persistence;
- sensitive household/member information;
- absence of web/session authentication;
- distinction between secure input/data handling and unjustified authentication infrastructure.

This case tests whether security analysis can explicitly conclude NOT_APPLICABLE without inventing web-centric controls.

### NAPMS

Useful pressure points:
- browser/HTTP trust boundary;
- server-side session identity;
- protected actions and authorization;
- PostgreSQL;
- session/credential disclosure;
- interface error representation;
- operability redaction;
- long-running service lifecycle.

This case tests whether Product/Domain entitlement, Security Architecture enforcement, Interface representation, Data protection and Operability evidence remain separable.

## Promotion criteria

Do not canonicalize Harness changes until both pilots show:

- the same Security Architecture responsibility survives materially different runtimes;
- Security Analysis discovers/routs gaps without becoming a second architecture owner;
- no broad "Security" Authority is needed;
- blocking Questions can be represented by existing Harness mechanics;
- downstream consumers can identify exactly which accepted security knowledge they require;
- external security frameworks improve coverage without becoming unconditional project requirements.

If these criteria fail, revise/split/merge Authorities according to the atomicity test rather than preserving the current catalog by convention.
