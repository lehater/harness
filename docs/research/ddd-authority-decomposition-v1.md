# DDD pattern-language decomposition through Authority knowledge flow

Status: experimental research. Sources: Eric Evans, *Domain-Driven Design Reference* (2015), cross-checked against Fowler's Bounded Context/Aggregate descriptions and Microsoft's current domain-analysis/tactical-DDD guidance.

## Result

Running the DDD pattern language through decision → accepted knowledge → consumer does **not** produce one Harness Authority per DDD concept. It produces four materially different classes:

1. **Problem/domain strategy knowledge** — business/domain decomposition and strategic importance.
2. **Model-boundary strategy knowledge** — where a model/language is valid and how independently modeled contexts relate.
3. **Tactical domain-model knowledge** — identities, values, invariants, aggregate boundaries, domain events and domain-facing retrieval/creation semantics.
4. **Modeling/design practices** — techniques that improve a model but are not independently consumed public engineering knowledge.

A fifth class consists of patterns whose primary decision belongs outside domain ownership (for example Layered Architecture), even though DDD discusses them.

The key finding is that DDD itself contains **two independently meaningful strategic decision families** that the current STRATEGIC-DOMAIN-DESIGN Authority compresses:

- **domain strategy/distillation**: identify the domain landscape, subdomains/core differentiation and strategic investment;
- **model-context strategy**: establish Bounded Context/model-language boundaries and Context Map relationships.

They are related, but neither is definitionally the other. A subdomain is a problem/business decomposition; a Bounded Context is the applicability boundary of a model/ubiquitous language. A useful 1:1 alignment is a design outcome to justify, not a discovery rule.

## Knowledge-flow decomposition

### A. Domain strategy / distillation

Decisions:
- what business/domain capabilities form coherent subdomains;
- which domain is Core and where strategic modeling investment belongs;
- which capabilities are generic/supporting versus differentiating;
- what concise domain vision guides trade-offs.

Accepted outputs:
- domain/subdomain landscape;
- strategic classification and investment focus;
- domain vision/core rationale.

Concrete consumers:
- model-context strategy uses the landscape and strategic priorities when deciding where independent models are justified;
- product/application/system design may use strategic classification to choose investment/integration posture;
- tactical modeling uses core focus to allocate modeling depth.

This is public accepted knowledge, not merely an internal analysis.

### B. Model-context strategy

Decisions:
- where a particular model and Ubiquitous Language are valid;
- whether independently modeled areas share, translate, conform, publish a language, or separate;
- what semantic contracts cross context boundaries.

Accepted outputs:
- Bounded Context identities/boundaries;
- Context Map and relationship semantics;
- cross-context translation/public-language expectations.

Concrete consumers:
- tactical domain modeling needs to know which model/language it is allowed to make internally consistent;
- application/integration/interface/system design needs context relationships without re-owning domain meaning.

This output can change independently of subdomain classification: one subdomain may require multiple models; context boundaries can split/merge while the business landscape remains stable.

### C. Tactical domain modeling

Decisions:
- identity vs descriptive value;
- aggregate consistency/invariant boundaries;
- domain-significant events;
- domain operations not naturally owned by an entity/value;
- domain-facing creation and retrieval semantics;
- internal model modularization.

Accepted outputs:
- tactical model semantics: Entities, Value Objects, Aggregates, Domain Events, Domain Services, Factories, Repository contracts, model Modules.

Consumers:
- application/component/interface/data/verification/implementation design.

These patterns strongly cohere as one Authority because consumers generally need the accepted model as a semantic whole, while implementation details remain downstream.

### D. Modeling practices, not Authorities

Ubiquitous Language, Continuous Integration of the model, Hands-on Modelers, Refactoring Toward Deeper Insight, Intention-Revealing Interfaces, Side-Effect-Free Functions, Assertions, Standalone Classes, Closure of Operations, Declarative Design, Established Formalisms, Conceptual Contours, Evolving Order and several Core-distillation techniques are primarily **methods for producing or improving** accepted knowledge. They do not automatically deserve public CapabilityIds or Authorities.

They become public knowledge only when a concrete downstream consumer requires an accepted obligation/result (for example an explicit engineering policy).

### E. Outside-domain ownership despite appearing in DDD

Layered Architecture primarily decides technical dependency/layer structure and therefore maps to SYSTEM-ARCHITECTURE/COMPONENT-DESIGN, not TACTICAL-DOMAIN-DESIGN. DDD's inclusion of a pattern does not determine Harness ownership.

## Evans reference patterns: disposition

The executable inventory in `spec/research/ddd-authority-decomposition-v1.yaml` covers the complete named pattern set in the 2015 DDD Reference:
- Putting the Model to Work;
- Building Blocks;
- Supple Design;
- Context Mapping;
- Distillation;
- Large-scale Structure.

Each pattern is classified as one of:
- `public-domain-strategy`;
- `public-context-strategy`;
- `public-tactical-model`;
- `modeling-practice`;
- `external-authority`;
- `context-relationship-pattern`.

## Authority consequence under test

The research supports **splitting the current strategic decision space conceptually**, but it does not yet justify adding two mandatory Authorities to every graph.

The safer Harness interpretation is:

- introduce distinct capability families for **domain strategy** and **model-context strategy**;
- allow them to be owned by one STRATEGIC-DOMAIN-DESIGN Authority when the project is simple/cohesive;
- permit an Authority split when the knowledge-flow/independent-change evidence demonstrates separate ownership/lifecycles;
- require model-context outputs to consume accepted domain strategy when such strategy exists, but do not require every simple project to manufacture subdomain taxonomy;
- prohibit capability/product-feature lists from being relabeled as Bounded Contexts without model/language-boundary evidence.

This preserves Harness's project-specific atomicity principle while fixing the current conflation.

## Falsification cases

The method must reject:
- Product Capability → Bounded Context by naming similarity alone;
- Subdomain → Bounded Context as an automatic 1:1 mapping;
- Core/Supporting/Generic classification as proof of model boundary;
- Aggregate/service/repository decisions before the relevant model context is established in non-trivial domains;
- Ubiquitous Language as a free-floating global vocabulary in a multi-context model;
- Layered Architecture as domain semantic ownership merely because it appears in DDD literature.

It must allow:
- simple domain: one strategic owner and one model context;
- multiple subdomains represented inside one model context when justified;
- one subdomain represented by multiple Bounded Contexts when language/model consistency requires it;
- Bounded Context changes without reclassifying subdomains;
- domain-strategy changes without mechanically redrawing context boundaries;
- tactical model evolution behind a stable context boundary.

