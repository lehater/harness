# CDR contract-change reconsideration — read-only preflight v1

Status: **experimental, nonauthorizing**, Harness PR #220.

## Boundary and reuse

- **Engineering Graph** owns declared per-production direct prerequisites and
  Authority ownership. Structural validation belongs to
  `harness.project_model.engineering_graph`.
- **Capability Lifecycle** already detects `PREREQUISITE_TOPOLOGY`,
  prerequisite acceptance/fingerprint changes, `STALE` and `REVALIDATE`.
  This preflight must not create another currentness state machine.
- **CDR** evaluates whether a target's **own independently accepted output
  obligations** materially consume a particular supplier's accepted public
  contract. A changed source or Git revision by itself proves no directness.
- **Target project Authority** remains the owner of semantic acceptance, the
  decision on direct edges and the authorized Engineering Graph edit.

## Entry and output

Invoke explicitly after a coherent project change, with the project checked
out cleanly at the new Git commit and the old commit an ancestor of the new:

```sh
make cdr-change-preflight \
  PROJECT_ROOT=/path/to/project \
  CDR_BEFORE=<full-40-character-old-sha> \
  PROJECT_COMMIT=<full-40-character-new-sha> \
  CDR_OUTPUT=/tmp/cdr-contract-change.json
```

The preflight reads both pinned revisions of
`.harness/engineering-graph.yaml`, `.harness/core.yaml`,
`.harness/semantic-baseline.yaml`, and Core-registered reviewed provider
artifacts directly from Git. It does not check out, edit or publish files.
It uses the **existing Engineering Graph validator** in each snapshot.

Results:

- `changed_capabilities`: exact observed differences in production identity,
  output contract, `requires`, Authority public contract, registered source,
  source digest and semantic review revision;
- `cdr_review_targets`: changed target production contracts and immediate
  consumers of changed sources; **candidates for reconsideration**, not a
  command to infer or add an edge;
- `lifecycle_only_transitive_scope`: further downstream impact; the existing
  lifecycle evaluator alone determines semantic currentness;
- `unreviewed_changes`: source bytes differ but review revision did not change.
  Returns `BLOCKED_UNREVIEWED_SOURCE_CHANGE`, exit code 2;
- `automatic_writeback_allowed=false` always.

The query is bounded to 5000 produced Capabilities. Invalid graph snapshots,
unavailable or unpinned Git objects, dirty HEAD, missing reviewed sources,
ambiguous Core providers and inconsistent Authority registrations fail closed.

## Decision point

Review `cdr_review_targets` only after distinguishing a real *public contract*
change from a content-only or administrative acceptance-revision change.
If no externally consumed rule changed, Lifecycle is sufficient; do not
manufacture a topology revision.

For material public changes, the consuming Authority revisits target-owned
accepted output obligations, direct rule consumption, alternate immediate
provider sufficiency and source change sensitivity. Use existing
`cdr-prepare` / `cdr-reconcile` / `cdr-dossier` /
`cdr-check-review` as **non-authorizing** evidence preparation.
The output cannot establish independently accepted target obligations,
reviewer identity or graph mutation authority.

When target and provider contracts are actually accepted and a trusted
project-owned decision authorizes an edge change, the project's normal
Engineering Graph change procedure must validate the candidate graph and
recompute Lifecycle under the new topology. Old lifecycle identities remain
evidence but are `STALE` on a changed prerequisite set.

## Limits

The preflight compares project-native review revisions and registered source
content, **not** semantic equivalence of two texts. It deliberately errs
toward unnecessary *review candidates*, never toward automatic graph edits.
The baseline inventory cannot by itself prove independent acceptance of
a new target output. A draft output contract is still draft.

Only explicit invocation is enabled in PR #220. There is **no default
Capability CREATE routing, autonomous acceptance event, trusted reviewer
attestation or writes to PREP/Harness main**. Those remain governance gates.

## Regression evidence

`tests/test_cdr_contract_change.py` checks no-change, reviewed upstream
change/direct vs transitive routing, modified direct prerequisites, blocked
unreviewed source, non-ancestor/invalid pin and dirty working tree.
