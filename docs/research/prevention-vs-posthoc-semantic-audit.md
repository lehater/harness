# Research — Prevention vs post-hoc semantic audit

Status: research only. Not canonical. No main changes.

## Question

Should Harness invest in making artifact formation semantically correct by construction,
or is it cheaper and safer to allow ordinary artifact generation and run a complete
semantic audit afterwards?

## Executive conclusion

Trying to make artifact generation **error-free by construction is not economically
justified and is probably unattainable** for unrestricted engineering artifacts.

But relying only on a **late full-project semantic audit is also a poor architecture**.

The rational target is a hybrid:

1. prevent only cheap, high-confidence error classes during formation;
2. validate every artifact semantically at its acceptance boundary;
3. run incremental downstream revalidation after accepted semantic changes;
4. keep a full-project semantic audit as a periodic/backstop check, not as the primary
   correctness mechanism.

In short:

> Do not optimize for perfect generation. Optimize for cheap generation plus strong,
> local, mandatory acceptance.

---

# 1. Why perfect formation is the wrong target

The recent NAPMS/Nutrition audit found defects caused by:

- stale downstream semantics after upstream replacement;
- incomplete operation/subject coverage;
- cross-artifact incompatibility;
- ownership/provenance leakage;
- lifecycle/status drift.

These are not all generation-time mistakes.

Some defects arise only after **later upstream change**. An artifact may have been
correct when authored and become wrong afterwards.

Example:

```text
Resource UI correct at T1
-> Resource domain model replaced at T2
-> same unchanged UI becomes semantically stale
```

No amount of better initial generation can prevent this class.

Therefore the real invariant is not:

```text
artifact was generated correctly
```

but:

```text
artifact is currently semantically valid against current accepted upstream truth
```

That is inherently a validation/revalidation problem.

---

# 2. Cost of trying to guarantee correct formation

To make generation close to error-free, Harness would need to constrain the authoring
process heavily:

- fully structured semantic schemas for most artifact kinds;
- exhaustive subject enumerations before generation;
- explicit assertion-level provenance while drafting;
- cross-artifact consistency solving during generation;
- mandatory decomposition of natural-language decisions into formal assertions;
- artifact-specific authoring engines;
- much larger prompt/context packages;
- more agent passes before a candidate artifact can even exist.

This has several costs.

## 2.1 High model and tooling complexity

Every new artifact family would require a richer production DSL and specialized
generation logic.

Harness would start drifting toward a universal engineering ontology.

That contradicts the current successful principle:

> artifact skills own artifact-specific semantics; Core remains small.

## 2.2 Higher authoring latency

Generation becomes an expensive proof-producing operation rather than a cheap proposal.

Many candidates that could have been produced quickly and rejected cheaply would instead
consume expensive reasoning during drafting.

## 2.3 False confidence remains

Even elaborate constrained generation cannot guarantee correctness for:

- ambiguous stakeholder intent;
- natural-language equivalence;
- external scientific/legal truth;
- future upstream changes;
- omissions not represented in the generation schema.

So the cost rises substantially without eliminating the need for later validation.

## 2.4 Reduced adaptability

A strict by-construction representation tends to freeze today's understanding of artifact
semantics.

New concern classes then require changes to the generator ontology before the project can
express them naturally.

---

# 3. Cost of relying only on full post-hoc audit

The opposite extreme is also inefficient.

Suppose Harness allows all artifacts to be authored freely and only later runs:

```text
audit every canonical artifact
x all upstream dependencies
x all downstream consumers
```

This works as a safety net but scales poorly.

## 3.1 Repeated global work

A defect in one upstream artifact can force reevaluation of a large project even when only
a small semantic closure is affected.

## 3.2 Late defect discovery

A semantic mistake can propagate through:

- architecture;
- interfaces;
- data design;
- test design;
- implementation design;
- Engineering Coverage.

The later it is found, the larger the repair set.

The NAPMS Resource UI issue demonstrates this directly: one stale semantic boundary
propagated into an entire frontend design chain.

## 3.3 Poor localization

A global audit tells us that the project is wrong, but the best correction point may be
several layers upstream.

Without local artifact acceptance, errors become normalized into downstream artifacts and
tests.

## 3.4 Audit itself still needs a contract

A full semantic audit cannot reliably answer "is everything correct?" unless Harness
already knows:

- what each artifact was required to contain;
- what sources it was allowed to use;
- what Authority owns each decision;
- what subjects had to be covered.

Those are exactly the semantic-acceptance contracts needed for local validation.

Therefore "only audit later" does not actually avoid building most of the semantic model.

---

# 4. The economically efficient split

The optimal split is to classify controls by cost and certainty.

## Tier A — prevent during generation

Use prevention only when it is cheap and deterministic.

Examples:

- give the agent only bounded accepted upstream context;
- enforce Authority write boundary;
- provide explicit artifact skill;
- provide required subject list;
- forbid unresolved external decisions from being invented;
- require structured identifiers where already natural.

These constraints improve first-pass quality cheaply.

They should not attempt full proof.

## Tier B — mandatory acceptance immediately after generation

This should be the main correctness boundary.

Check:

- semantic obligations complete;
- subject coverage complete;
- structured provenance valid;
- deterministic contradictions absent;
- ownership respected;
- required cross-contract mappings exist;
- bounded semantic review passes for residual prose.

Only accepted artifacts become canonical capability realizations.

This is much cheaper than perfect generation because failed candidates are disposable.

## Tier C — incremental revalidation after change

When accepted upstream semantics change:

```text
changed provider capability/assertion
-> invalidate affected accepted consumers
-> re-evaluate only affected semantic closure
```

This handles the class that generation can never solve.

Initially this can operate at capability/artifact granularity.

Later assertion-level provenance can narrow the affected set.

## Tier D — full semantic audit

Keep full audit for:

- migration of an existing project onto Harness;
- major canonical redesign;
- release/readiness milestones;
- periodic regression;
- checking the semantic-acceptance machinery itself.

It is a backstop and calibration tool, not the ordinary inner loop.

---

# 5. Relative cost model

Qualitatively:

| Strategy | Generation cost | Ongoing validation cost | Change/revalidation cost | Defect escape risk | Harness complexity |
|---|---:|---:|---:|---:|---:|
| Perfect-by-construction attempt | Very high | Still required | Medium/high | Medium | Very high |
| Free generation + global audits only | Low | Very high | Very high | High between audits | Medium |
| Hybrid local acceptance + incremental revalidation | Low/medium | Medium | Low/medium | Low | Medium |
| Hybrid + periodic full audit | Low/medium | Medium | Low/medium | Lowest practical | Medium |

The hybrid dominates because it spends expensive semantic reasoning only at a stable
boundary: acceptance.

---

# 6. Evidence from the seven real defects

The real findings divide naturally.

## Cheap to prevent or detect locally

- NAPMS 413 missing from OpenAPI;
- Nutrition ADR says "pilot branch" while registered canonical;
- Data Design contains implementation-vendor assertions outside allowed provenance.

These do not justify a sophisticated generation system. Simple acceptance checks are
cheaper.

## Best handled by artifact acceptance

- HTTP contract missing required Resource operations;
- Add Member journey missing member-identity application semantics;
- UI read model not realizable by OpenAPI.

These require explicit obligations and producer/consumer compatibility checks.

Trying to force the generator never to make such omissions would require almost the same
semantic model, but placed in a more fragile stage.

## Only revalidation can solve reliably

- Resource UI becomes stale after Resource domain replacement.

This proves that post-generation current-validity checking is unavoidable.

---

# 7. Recommended design principle for Harness

Harness should treat artifact production as **proposal generation**, not truth production.

```text
inputs
  -> cheap constrained generation
  -> candidate
  -> semantic acceptance
  -> canonical realization
```

The generator may be smart, but correctness must not depend on it being perfect.

This separation has a useful engineering property:

> better generation improves efficiency; acceptance preserves correctness.

If the model gets better, fewer candidates fail.

If the model gets worse, correctness does not collapse as long as acceptance remains strong.

That is much more robust than coupling correctness to authoring quality.

---

# 8. How much should be moved into generation?

Only information that also helps the acceptance contract and does not create duplicate
truth.

Good generation inputs:

- required capability;
- Authority;
- accepted upstream closure;
- explicit semantic obligations;
- required subject set;
- known forbidden inventions;
- unresolved Questions.

Do not add a separate "generation-only semantic model".

The same obligations should guide both:

```text
generation hints
and
acceptance checks
```

This avoids maintaining two semantic systems.

---

# 9. Where full audits remain valuable

A full audit is still important because the acceptance mechanism itself can be incomplete.

Periodic full audits answer:

- did we forget an obligation class?
- is a capability contract too broad?
- are there hidden semantic dependencies?
- did a migration bypass acceptance?
- are artifacts registered that predate the current mechanism?

This is analogous to reconciliation in distributed systems:

local transactions are the normal correctness mechanism;
periodic reconciliation detects failures in the mechanism itself.

That is the right role for the full semantic audit.

---

# Final decision recommendation

Do **not** invest in trying to make artifact generation universally error-free.

Invest in:

### P0

- mandatory semantic acceptance before canonical registration/use;
- subject-aware completeness;
- producer/consumer compatibility;
- semantic claim gating for Coverage;
- downstream invalidation/revalidation.

### P1

- use the same semantic obligations to guide generation so first-pass quality improves;
- deterministic provenance and lifecycle checks;
- incremental affected-closure calculation.

### P2

- assertion-level provenance to reduce revalidation scope;
- independent/adversarial semantic review for high-risk artifacts.

### Backstop

- periodic/full semantic audits after major redesigns and as regression calibration.

The desired system is therefore not:

```text
perfect generator
```

and not:

```text
generate freely -> periodically inspect everything
```

but:

```text
cheap constrained generation
-> mandatory local semantic acceptance
-> canonical truth
-> incremental revalidation on change
-> occasional full reconciliation audit
```

This gives most of the correctness benefit at substantially lower complexity and cost.
