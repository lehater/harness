# Process Simplicity and Efficiency v0

Status: canonical global constraint.

## Normative rule

When procedures preserve the same required guarantees, Harness must require the
materially simpler one: fewer steps, artifacts, round trips, persisted states,
recomputation and coordination. Aim for **minimum sufficient process**, not
minimum validation.

Validate at the cheapest sufficient layer; reuse unchanged CURRENT state;
evaluate only the affected closure; aggregate independent blockers; keep
intermediate state non-current; publish coherently.

CI is a verification boundary, not an interactive exploration mechanism.
Repeated generic project glue belongs behind a Harness application boundary.

Preserve semantic correctness, Authority ownership, no fabricated acceptance,
reproducibility, lifecycle/currentness, traceability, compatibility and
atomic/CAS publication. Persist only invariant-bearing state.

**automate mechanics, not authority**.
