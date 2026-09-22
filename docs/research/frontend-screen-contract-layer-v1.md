# Research — Frontend screen contract layer

Status: research candidate. Branch: `research/frontend-screen-contract-layer`.

## Decision

Harness does not need a parallel frontend ontology.

The existing Authorities and knowledge kinds are sufficient if `screen-view-design` is strengthened into the canonical closure point between accepted product/application/machine-interface semantics and a reusable presentation provider.

The target dependency is:

```text
Product / Domain
  -> Use cases / user journeys
  -> machine-interface query + command contracts
  -> Human Interface semantics
  -> Screen/View semantic contract
       - read/query bindings
       - command bindings
       - semantic screen/view model
       - state/error mapping
       - permission/navigation bindings
       - allowed/excluded capabilities
       - presentation feature mapping
  -> Presentation System / external baseline
  -> frontend architecture + component realization
  -> verification/test/rendered evidence
```

Presentation System may be developed in parallel once its own inputs are known. It supplies reusable presentation vocabulary; it does not authorize product behavior.

## Why the original layer list is too granular

The following are independent decisions, but most do not justify independent Harness knowledge kinds:

| Concern | Canonical owner | Representation |
| --- | --- | --- |
| User goal/use case | Product / Domain / Application Design | existing requirements/use-case/journey artifacts |
| Frontend read/query contract | Interface Design | operation/schema in existing machine-interface contract |
| Frontend command contract | Interface Design | operation/schema in existing machine-interface contract |
| Screen interaction semantics | Interface Design | existing Human Interface Design |
| Screen/View model | Interface Design | required section of Screen/View Design |
| UI transient state | Interface Design + System Architecture boundary | semantic states in Screen/View; lifetime/cache mechanics in architecture |
| Errors/outcomes | Interface Design | machine-interface outcome -> screen-state mapping |
| Permission/capability visibility | Security + Interface Design | accepted security semantics mapped into Human/Screen contract |
| Navigation | Interface Design | existing Human Interface/navigation contract |
| Presentation pattern selection | Interface Design | Screen/View pattern mapping |
| Template/component realization | Component Design / implementation | implementation assets; canonical only when explicitly promoted |
| Responsive/accessibility semantics | Interface Design/Quality | facets of Human Interface, Presentation System and Screen/View |
| Verification | Verification/Test Design | existing verification and test artifacts |

A separate `frontend-query-contract`, `view-model`, `pattern-mapping` or `BFF` knowledge kind would duplicate existing Authority boundaries.

## Data boundary

These representations are intentionally distinct:

```text
Backend DTO
  -> frontend query projection
  -> Screen/View Model
  -> component props
```

A backend DTO is a transport representation.

A frontend query projection is an application/interface operation result optimized for a read use case. It may equal a backend DTO for a simple use case, but that equality is accidental and must not make the DTO the UI semantic model.

A Screen/View Model names exactly the information and semantic distinctions the screen consumes. Interface Design owns its meaning; frontend adapter/component code owns the executable transformation.

Component props are private realization contracts unless a reusable component has intentionally been made a public Component Design contract.

## Transformation responsibility

- Interface Design owns required operations, result semantics, Screen/View model fields and outcome/state mapping.
- System Architecture owns the client/server boundary, state lifetime, aggregation placement and cache/invalidation policy when architectural.
- Component Design owns the code-facing adapter boundary that maps transport/query results into Screen/View models and then into components.
- Product/Domain/Security remain authoritative for business and authorization meaning.

Raw transport objects reaching presentation components are a design smell because the screen then inherits transport naming, optionality and error semantics.

## Read projection and BFF decision

Use the existing application/API when one accepted operation already supplies the needed semantics with reasonable call shape and no client-side reconstruction of business/security truth.

Add a read projection or screen-oriented query inside the existing application boundary when a user task needs a purpose-built read shape, aggregation or bounded list that the current API does not provide.

A separate deployable Backend-for-Frontend is justified only when there is an independently changing client-specific boundary: materially different channel needs, aggregation/latency policy, security mediation, protocol adaptation or ownership. It is not the default response to an inconvenient DTO.

Frontend aggregation is acceptable for a small number of independent, optional panels where no coherent snapshot, authorization-sensitive filtering or domain interpretation is required. It is an architecture defect when the browser performs repeated cross-context joins/fan-out, N+1 reconstruction, consistency-sensitive snapshots, authorization decisions or reusable business rules.

## Presentation provider contract

A Presentation System may reference an external baseline:

```yaml
external_baseline:
  provider: mui
  artifact: crud-dashboard
  version: <immutable version>
  feature_policy:
    default: deny
```

The provider supplies appearance, components and optional presentation features. It is never semantic authority.

Each Presentation System pattern declares offered provider features. Each Screen/View binds only selected features to an already-authorized screen capability:

```yaml
patterns:
  CATALOGUE:
    features: [open-item, create-item, search, filter, sort, paginate, bulk-delete]

semantic_contract:
  capabilities:
    allowed:
      - {id: open-resource, backed_by: navigation:resource-detail}
      - {id: create-resource, backed_by: command:create-resource}
    excluded: [search, filter, sort, bulk-delete]
  pattern_mapping:
    - pattern: CATALOGUE
      feature_bindings:
        open-item: open-resource
        create-item: create-resource
```

Unbound provider features remain disabled. This is stronger than maintaining an exhaustive exclusion list because a future template version cannot silently activate a newly introduced feature.

## Minimal Screen/View semantic contract

A screen is design-closed when it contains or references:

1. reads/query bindings with stable operation ids;
2. command bindings with stable operation ids;
3. one semantic Screen/View model and source mapping;
4. allowed semantic capabilities, each backed by accepted read/command/navigation/local semantics;
5. notable exclusions;
6. presentation pattern feature bindings;
7. mapping for every declared screen state/error/outcome;
8. responsive/accessibility semantics where the screen changes shared defaults;
9. contract, semantic and rendered verification obligations.

This remains one `screen-view-design` artifact family.

## Proof obligations

The frontend implementation consumer must not become complete from artifact existence alone.

Required closure:

```text
Use Case
 -> required data/actions
 -> accepted query/command operations
 -> Screen/View semantic model
 -> allowed capabilities
 -> presentation feature bindings
 -> component realization
 -> rendered verification evidence
```

The semantic screen evaluator rejects at least:

- read or command bindings whose operation does not exist;
- view-model fields sourced from unknown bindings;
- presentation features mapped to non-authorized screen capabilities;
- external baselines whose feature default is not deny;
- declared screen states without semantic source mapping;
- screens without contract/semantic/rendered verification obligations.

Its result can be adapted to existing Harness semantic-acceptance evidence. A rejected Screen/View capability therefore invalidates downstream implementation capabilities through the existing Engineering Coverage invalidation closure. No new target-state mechanism is required.

## Coverage taxonomy

Two concern names are sufficient for explicit coverage without a new Authority:

- `interface.human.presentation-system` -> `engineering.interface.human.presentation-system`
- `interface.human.screen-composition` -> `engineering.interface.human.screen-composition`

Projects may bind their existing Presentation System and Screen/View capabilities to these claims. Subject-scoped Screen/View proof should be used when a project needs per-subject completeness.

## NAPMS pilot findings

### Resource Detail

Current NAPMS already has the strongest chain:

`getResource -> ResourceView -> resource-detail data mapping -> Detail composition`.

The missing piece is an explicit Screen/View model and explicit feature authorization/pattern mapping. No BFF is justified.

### Resource Catalogue

Canonical product/journey semantics require locating/selecting a Resource and starting supported Resource creation. The modern first-MVP OpenAPI has `createResource` and `getResource`, but no canonical list/read operation for the catalogue.

Therefore the current Screen/View declaration of `FILTER-BAR` and search/filter controls is not closed. Legacy `/api/v1/catalogues/**` endpoints are implementation evidence only and cannot silently satisfy the modern contract.

The minimal modern read contract is a list projection sufficient to identify/open resources. Search, filters, user-selectable sorting, bulk actions and delete are not implied by the catalogue pattern. Pagination is transport/quality policy unless explicitly promoted to user semantics.

### Dashboard-like outcome

NAPMS Policy Export is a useful aggregate-screen test. `materializeCurrentPolicy` already returns a purpose-built aggregate application result containing status, evaluation time, selection, authority evidence, provenance, non-effective items, rows and issues.

The screen can map that one operation result into an outcome/dashboard-like view model. A separate BFF or browser fan-out is not required.

## KISS result

Keep:
- existing Authorities;
- existing machine-interface contract;
- Human Interface Design;
- Presentation System Design;
- Screen/View Design;
- System Architecture;
- Component/Verification/Test/Implementation Design;
- existing semantic-acceptance and Engineering Coverage invalidation mechanisms.

Extend:
- Screen/View Design output contract;
- Presentation System external-baseline semantics;
- coverage proof names;
- validators.

Do not add:
- a frontend-specific Authority;
- a MUI-specific artifact kind;
- mandatory BFF;
- independent canonical artifacts for every UI state/model/mapping facet;
- a second frontend graph.
