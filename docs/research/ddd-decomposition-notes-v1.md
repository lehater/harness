# DDD decomposition through Authority knowledge flow

Status: experimental research.

The DDD pattern language was classified by the research sequence: engineering decision → accepted knowledge output → concrete consumer → dependency → ownership boundary.

## Main decomposition

The method produces five different categories rather than one Authority per DDD concept.

**Domain strategy/distillation.** Decisions about the problem-space landscape, subdomains, strategic differentiation, investment focus and domain vision. The accepted output is a domain landscape plus strategic classification. Model-boundary design, architecture/application design and tactical modeling can consume it.

**Model-context strategy.** Decisions about where a model and its language are valid, plus relationships between independently modeled contexts. Accepted outputs are Bounded Context boundaries, Context Map relationships and cross-context semantic contracts. Tactical modeling and integration/application/system design consume them.

**Tactical domain model.** Decisions about identity, descriptive values, invariants, aggregate consistency boundaries, domain-significant events, domain operations, domain-facing creation/retrieval semantics and internal model modules. These form a coherent semantic contract consumed by application, component, interface, data, verification and implementation design.

**Modeling practices.** Ubiquitous Language, continuous model integration, hands-on modeling, refactoring toward deeper insight, most Supple Design patterns, Evolving Order and several distillation techniques primarily describe how to produce or improve accepted knowledge. They do not automatically create a public Capability or Authority.

**Decisions owned elsewhere.** Some patterns discussed in DDD primarily decide technical structure. Layered Architecture is the clearest example; inclusion in DDD literature does not make it domain-semantic ownership.

## Strategic split discovered

The current STRATEGIC-DOMAIN-DESIGN boundary compresses two independently meaningful decision families:

1. domain strategy: what problem-space areas exist and where strategic differentiation/investment lies;
2. model-context strategy: where a particular model/language is applicable and how those contexts relate.

A subdomain is problem/business decomposition. A Bounded Context is model/language applicability. A one-to-one alignment can be a good design outcome, but is not a discovery rule.

The two outputs can evolve independently. One subdomain may require multiple models. Multiple problem-space responsibilities may sometimes remain inside one coherent model. A context boundary can change while the business landscape remains stable; strategic classification can change without mechanically redrawing a valid model boundary.

## Harness consequence under test

The evidence supports distinct capability families for domain strategy and model-context strategy. It does not yet prove that every project needs two mandatory Authorities.

The conservative model is:
- keep the two accepted knowledge families distinguishable;
- allow one STRATEGIC-DOMAIN-DESIGN Authority to own both when cohesive;
- permit an Authority split only when knowledge-flow and independent-change evidence proves separate ownership/lifecycles;
- when domain-strategy knowledge exists, model-context design consumes it;
- do not force simple projects to manufacture a subdomain taxonomy;
- reject Product Capability → Bounded Context renaming without model/language-boundary evidence.

## Falsification cases

The method must reject automatic Subdomain → Bounded Context mapping, capability groups renamed as contexts, strategic classification used as proof of a model boundary, premature tactical aggregate design in a non-trivial multi-model domain, and technical architecture treated as domain ownership merely because DDD discusses it.

It must allow simple one-context domains, multiple subdomains in one model context when justified, one subdomain represented by multiple contexts, independent evolution of domain strategy and context boundaries, and tactical evolution behind a stable context contract.
