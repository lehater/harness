# Resource Detail Blind Comparison

Status: research result / non-canonical

## Comparison target

Blind candidate was formed from Resource Catalogue use-case/domain truth without reading:
- `docs/contracts/ui/mvp-navigation.yaml`;
- `docs/contracts/ui/resource-detail.yaml`;
- legacy UI;
- frontend implementation.

It was then compared to the current narrow canonical Resource-history UI pilot.

## Recovered independently

The blind candidate recovered all major semantic decisions of the canonical UI pilot:

- Resource detail is keyed by stable ResourceId;
- Resource current facts are primary;
- missing current facts are explicit and do not mean Resource absence;
- history is subordinate to Resource detail rather than a new business object;
- loading, not-found and operational error are distinct;
- returning to catalogue does not mutate Resource;
- replace/end-style changes preserve current/history distinction;
- retry exists for operational read failure;
- current and historical facts remain distinguishable;
- UI does not own Resource domain semantics.

This is strong evidence that `human-interface-design` can derive a useful screen/state contract from accepted upstream truth rather than copying implementation.

## Decisions present in canonical UI but not derivable exactly

### Exact route `/resources/{resourceId}`

This is a supported interface representation choice. It is not implied by Resource domain truth.

The blind candidate correctly left the exact route unconstrained.

If stable deep-link URL is a public product/interface contract, the canonical UI artifact owns it legitimately.

### History initially collapsed/summary

This is an interaction/presentation decision, not derivable from domain history semantics.

The blind candidate required subordinate inspectability but left disclosure/tab/layout free.

This is correct independence: both realizations can satisfy the same upstream semantics.

### Exact data mapping / HTTP source

The canonical screen contract maps to its selected HTTP read model.

This belongs to Interface/System/Component realization once machine contract exists and need not be Product/Domain truth.

## Additional blind decisions not explicit in the narrow canonical UI pilot

The blind candidate also derived:
- mutation conflict/stale-version state from accepted aggregate versioning;
- explicit differentiation of Site/responsibility from authority;
- HostAddress vs Prefix preservation;
- prohibition on automatic Endpoint grouping;
- client prohibition on trusted authority fields.

These come from upstream domain/security semantics and show why a UI contract should consume the complete relevant upstream closure rather than only navigation requirements.

## Verdict

The second slice validates the same boundary as the first:

`User/use-case semantics -> Human Interface Design`

is sufficient to derive screen/view/state/transition contracts while leaving local representation choices free.

The canonical UI contract can validly add independently owned interface choices such as route names or disclosure style, but those should not be mistaken for upstream requirements.

No new Authority or Core construct is exposed by this comparison.
