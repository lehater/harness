# Engineering Coverage activation self-suppression audit

Status: research result supporting the canonical activation policy.

## Question

Can a concern disappear because its activation rule depends only on knowledge that would normally be produced while closing that same concern?

That pattern is unsafe for completeness: absence of the downstream design artifact suppresses the obligation that should have caused the artifact to be designed.

## Result

| Rule/family | Independent applicability signal | Risk | Result |
| --- | --- | --- | --- |
| BASELINE | Coverage evaluation itself | low | keep |
| SOFTWARE-IMPLEMENTATION-STRUCTURE | target Consumer contains `IMPLEMENTATION` | low | keep |
| HUMAN-INTERFACE | target Consumer contains `FRONTEND` after this change | low | fixed; frontend concerns no longer depend on pre-existing UI design |
| MACHINE-INTERFACE | interface-contract / interface Capability | medium | discovery-only unless project scope/profile independently requires a machine interface |
| PERSISTENT-DATA | data role plus persistence Capability | high | do not infer applicability from missing persistence design; require canonical scope/profile/obligation when persistence is mandatory |
| DATA-PROVENANCE | source/provenance capabilities that may be upstream domain/data facts | medium | acceptable as discovery; explicit upstream obligation remains authoritative |
| SECURITY-BOUNDARY | security-architecture role/kind | high | discovery-only; missing Security Architecture must not prove security N/A |
| IDENTITY-AUTHORITY | domain/application capability names | medium | useful independent semantic signal where identity/authorization is already in accepted scope |
| EXTERNAL-DEPENDENCIES | source/dependency identity capabilities | medium | useful discovery signal; externally imposed obligations still need explicit provenance/applicability |
| RUNTIME-SERVICE | architecture role plus service/deployment capability | medium | mostly independent structural signal; not universal for all implementation consumers |
| OBSERVABILITY-DESIGN | observability Capability | high | self-suppressing if used as sole completeness source; scope/profile must activate observability when required |
| QUALITY-DESIGN | quality design/capability | high | self-suppressing if used as sole source; accepted quality requirements/profile are the authority |
| MODULAR-COMPONENT-DESIGN | engineering role plus component-design/policy knowledge | medium | core engineering concerns are independently activated for implementation consumers; maintainability leaves still need an upstream requirement/profile when mandatory |
| RELEASE-DELIVERY | implementation/delivery knowledge | high | discovery-only; release/rollback applicability is product/deployment/process scope truth |
| manual activation classes | explicit accepted project fact | low | keep; these concerns cannot be inferred safely from generic topology |

## Architectural rule

Activation heuristics are recall/discovery aids. They are not proof that the concern universe is complete.

A concern that is mandatory for a selected Consumer/Scope must have at least one independent upstream basis:

1. a universal Consumer signal in Harness policy;
2. a canonical subject obligation whose concern list requires exact proof;
3. an accepted project applicability/profile fact; or
4. another accepted upstream semantic Capability whose meaning is independent of the downstream design being requested.

Do not make conditional concerns universal merely to remove self-suppression. That converts false negatives into false requirements.

## Regression established

`FRONTEND-IMPLEMENTATION` activates the human-interface concern family even when its Consumer closure contains no human-interface design or user-journey Capability. This catches the original class of frontend omission before any UI design artifact exists.

## Residual boundary

Persistence, security architecture, observability, quality and release/delivery cannot be made universally mandatory from generic software topology. Their completeness therefore depends on accepted project scope/profile/obligation inputs. This is intentional semantic ownership, not a Coverage escape hatch: subject inventory is mandatory, and projects must explicitly classify applicability rather than rely on silence.
