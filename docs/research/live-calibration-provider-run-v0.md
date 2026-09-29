# First real Live Calibration Run — execution integration v0

Status: completed integration proof; real provider-backed evidence recorded. GitHub Copilot auto-routing is not model-reproducible and is not a deterministic PR gate.

## Baseline note

The requested starting point is commit `f61648183e4e3ab626b21e5e4ed5f0c3ecfb48e3`.
While this task was being started, PR #96 advanced
`experiment/scenario-suite` to descendant commit
`af45c52c498e028b7d1fa446dbace49ac72b3161` and added the generic
operator-loaded external-process driver. This task reuses that already-merged
process boundary instead of duplicating it. The remaining RED is narrower:
no concrete provider/model has yet produced real calibration evidence.

## Execution RED

The deterministic Live Calibration Validator and generic external-process path
exist, but the repository has no provider-specific semantic evaluator adapter,
no real provider invocation, and no recorded real scorer result.

The RED is therefore:

```text
blinded live request
        ↓
Scenario Suite external process driver
        ↓
[MISSING concrete provider/model execution]
        ↓
no real request-bound predictions
        ↓
no real calibration evidence
```

A synthetic process fixture is not evidence that a model/provider can satisfy
the protocol.

## Practically available evaluator mechanisms

### GitHub Copilot CLI

Selected for the first run. Provider capability probing happened before any scorable result: explicit `claude-haiku-4.5`, `gpt-5.3-codex`, and `gpt-5-mini` requests were rejected as unavailable for the workflow identity. A one-shot `--model=auto` capability probe, isolated from the calibration corpus, resolved to `gpt-6-luna`, but an explicit `gpt-6-luna` request was also rejected. The runnable workflow identity therefore supports provider auto-routing but not an explicit model pin. The first real calibration uses `model: auto` and records the CLI-observed resolved model in runtime provenance. This is real provider execution with weaker model-level reproducibility than an explicit pin; no calibration labels were inspected or used to choose the routing configuration.

Current GitHub documentation supports non-interactive Copilot CLI execution in
GitHub Actions with `copilot-requests: write` and the built-in
`GITHUB_TOKEN`. The Harness repository is personally owned, so this route does
not require a repository-stored provider API secret when the repository owner's
Copilot entitlement permits the request.

The run pins:

- execution provider: `github-copilot`;
- requested model policy: `auto`;
- Copilot CLI: `1.0.86`;
- provider adapter: `github-copilot-cli-live-calibration` v1;
- generic transport adapter: `process-json` v1.

The Actions workflow identity did not permit an explicit model pin. The
descriptor therefore binds the requested routing policy `model: auto`, not a
specific model. The adapter reads only model identity metadata from the pinned
Copilot CLI session events after execution and records the resolved model under
runtime provenance. The immutable provider model revision remains unavailable,
so `model_version: UNREPORTED` is retained and is not presented as
provider-reported model identity.

### GitHub Models

Not usable. GitHub retired the Models playground, catalog, inference API and
BYOK surface on 2026-07-30.

### Direct OpenAI / Anthropic API

Technically suitable, but no repository credential or independently controlled
service endpoint is part of the current Harness execution environment. Adding a
secret-dependent second integration before proving the first provider path
would add operational scope without new semantic evidence.

### HUMAN adapter

Valid in principle, but rejected as the first execution proof because it does
not prove automated provider integration or repeatability.

## Provider boundary

The existing `live_calibration_process_driver.py` receives the bound Harness
request and launches the provider adapter as a separate process.

The provider adapter receives no expert labels. Before invoking Copilot it
constructs a new model payload containing only:

- the protocol instruction;
- opaque `case_request_id`;
- `source`;
- `target`;
- `relation`;
- the structured output contract.

It does not include:

- canonical case id;
- `expected_status`;
- `mutation_class`;
- expert rationale;
- Harness request id;
- Harness run id;
- corpus/protocol fingerprints;
- evaluator descriptor.

The Copilot CLI is executed from a fresh temporary working directory with a
fresh `COPILOT_HOME`, repository custom instructions disabled, built-in MCPs
disabled, remote session/export disabled, and the only declared available tool
(`ask_user`) disabled by `--no-ask-user`.

## Provenance

Reproducibility-relevant requested configuration is fingerprinted in the
Evaluator Descriptor before request construction.

Runtime provenance is adapter-observed evidence and is deliberately separate
from the descriptor. The adapter records:

- execution provider;
- requested model;
- observed Copilot CLI version;
- fresh client session UUID;
- completion timestamp;
- enforced isolation flags.

No provider request id or immutable provider model revision is invented when
the CLI does not expose one.

The generic process driver persists this response provenance under
`execution.provider_provenance`. This is audit evidence, not trusted
attestation, so `independence.status` remains `UNVERIFIED`.

## Structured protocol

The model receives one JSON input and is instructed to return exactly:

```yaml
version: 1
kind: harness-live-semantic-evaluator-response
results:
  - case_request_id: ...
    status: ACCEPTED | REJECTED
    rationale: optional brief audit rationale
    findings: optional array
```

Markdown wrappers and free-form text are rejected as invalid JSON. Private
chain-of-thought is neither requested nor persisted.

## Failure handling

The provider adapter and existing validator/process boundary fail closed across
the required classes:

- missing provider executable -> process unavailable/failed, never scorable;
- provider timeout -> external execution does not produce a successful run;
- API/non-zero CLI failure -> FAILED/INCOMPLETE;
- invalid JSON or free-form text -> rejected before a successful evaluator response;
- missing case -> INCOMPLETE;
- duplicate case -> INVALID;
- unknown case -> INVALID;
- invalid status -> INVALID.

The last four result-shape failures remain validator responsibilities; the
provider adapter passes model results through rather than repairing them.

## Real-run protocol

The dedicated workflow renders fresh run identities from
`GITHUB_RUN_ID + GITHUB_RUN_ATTEMPT`, then executes the provider scenario via
Scenario Suite and the existing `--driver-module live_calibration_process_driver`
mechanism.

Two runs of the exact same corpus/protocol/evaluator binding are executed so
that real stability can be measured immediately. The workflow persists the full
Scenario Suite report and a compact summary as a GitHub Actions artifact.

## Real run evidence

PR #97 head commit `8489df5c11a90e95c76968a3801a63725453ea91`
completed GitHub Actions workflow run `36502184056`, attempt 2, successfully.
The persisted artifact is `live-calibration-evidence` artifact
`11005519111`, digest
`sha256:9b910cc801755de3c1f620040f8bb89340d2424e68367677508e18d6d44db40a`.

Both executions used the same bound evaluator descriptor:

- evaluator fingerprint:
  `LCEVAL-0a670c5231ac40358125de00bfab1939a1a3026b66c14cbfb203785be9cc3b09`;
- corpus fingerprint:
  `LCCORPUS-2c25776cd379162b71939691dd9d50e18943674ad1d407ec78bdb354e63455e9`;
- protocol fingerprint:
  `LCPROTO-1d77f3452d39b187229944c7e0e9463a14ec06774074729e6a95aacac31daafb`;
- provider: `github-copilot`;
- requested model policy: `auto`;
- resolved model observed in both executions: `mai-code-1.1-flash`;
- observed Copilot CLI version: `1.0.86`;
- process adapter executable SHA-256:
  `2536c63c609a40ad7e84fac232a129749b8e26076c44f2925bce7c8436760f28`.

Run 1:

- run id: `GH-36502184056-2-1`;
- request id:
  `LCREQ-4bddd422039c183f2604120a35727c29c3bdf00671ad87033f4c560999a05139`;
- confusion: TP=5, TN=5, FN=0, FP=0;
- detection recall: `1.0`;
- false-positive rate: `0.0`;
- accuracy: `1.0`;
- misses: none.

Run 2:

- run id: `GH-36502184056-2-2`;
- request id:
  `LCREQ-3934984813e230178e68984ed17817549dcd92f397561bbe9c0c34461828fcbc`;
- confusion: TP=5, TN=5, FN=0, FP=0;
- detection recall: `1.0`;
- false-positive rate: `0.0`;
- accuracy: `1.0`;
- misses: none.

Every corpus class scored 1/1 in both runs. The normalized verdicts were stable:

- `semantic-weakening` -> REJECTED;
- `semantic-inversion` -> REJECTED;
- `semantic-subject-swap` -> REJECTED;
- `semantic-partial-loss` -> REJECTED;
- `semantic-outcome-substitution` -> REJECTED;
- `valid-paraphrase` -> ACCEPTED;
- `valid-decomposition` -> ACCEPTED;
- `valid-aggregation` -> ACCEPTED;
- `valid-strengthening` -> ACCEPTED;
- `valid-subject-preservation` -> ACCEPTED.

The artifact retains the request-bound `case_request_id`, normalized verdict,
brief rationale and findings for every prediction. The two evaluator sessions
had distinct client session ids and distinct run/request ids.

Stability evaluation returned:

```yaml
status: STABLE
unstable_cases: []
```

No consensus or score aggregation was applied.

## Repeat execution findings

A later automatic execution on head
`77c8a1ef6c68a8b8f5ac792702be061be0f598fe` exposed two important
runtime properties without any prompt or scorer change.

Workflow run `36504064197`, attempt 1:

- run 1 resolved to `gpt-6-luna` and remained scorable;
- accuracy was `0.9`, detection recall `1.0`, false-positive rate `0.2`;
- the only miss was `valid-subject-preservation`, predicted REJECTED instead
  of ACCEPTED;
- run 2 also resolved to `gpt-6-luna`, but returned an unknown
  `case_request_id`;
- Harness rejected run 2 as `INVALID` with
  `LIVE_CALIBRATION_UNKNOWN_CASE_BINDING`.

The same workflow was rerun without a code change as attempt 2:

- run 1 resolved to `mai-code-1.1-flash` and scored 10/10;
- run 2 failed provider-response parsing because the returned envelope did not
  contain the required `version: 1`;
- the process boundary produced `FAILED`, and the validator produced
  `INCOMPLETE`; no partial score was accepted.

These failures are expected fail-closed behavior, not evidence to repair or
reinterpret provider output. They also prove that `model: auto` does not bind
an immutable model identity: the same evaluator fingerprint resolved to
`mai-code-1.1-flash` and `gpt-6-luna` across executions. The semantic mismatch
on the v1 subject-preservation case is retained as historical evidence of
cross-model interpretation under an ambiguous oracle, not as a model-quality
ranking.

The first successful two-run pair is therefore `STABLE` only for that observed
pair. Across later scorable executions of the same auto-routing descriptor,
`valid-subject-preservation` disagreed. Subsequent disagreement analysis found
that the v1 case itself was under-specified: the source stated an owner-only edit
invariant while the target stated only owner-only UI action availability. The
`gpt-6-luna` rejection was therefore semantically defensible and must not be
used as standalone evidence that one model is worse. Corpus/protocol v2 make
that distinction explicit; see `semantic-disagreement-analysis-v0.md`.

`model: auto` remains non-reproducible at model identity, and later malformed
provider responses remain operational evidence that this route is unsuitable
as a deterministic PR gate.

Because live provider routing and output validity are nondeterministic, the
Copilot workflow is operator-triggered evidence generation rather than a normal
pull-request gate. Deterministic process/adapter validators remain in the
regular `harness-check` CI path.

## Independence assessment

The first real run establishes the following dimensions separately:

- binding: PROVEN by Harness fingerprints and opaque case binding;
- execution separation: ESTABLISHED at the external-process boundary;
- fresh session: ESTABLISHED by distinct client session ids plus fresh temporary
  Copilot home/working directories;
- different configuration: NO; repeated executions use the same bound
  descriptor;
- different model: OBSERVED across repeats because provider auto-routing
  selected both `mai-code-1.1-flash` and `gpt-6-luna`; this is not a
  controlled independent-evaluator comparison;
- different provider: NO; all runs use GitHub Copilot;
- trusted provider attestation: ABSENT.

Therefore `independence.status: UNVERIFIED` remains correct. The evidence
proves real external execution, label withholding, request binding and
fail-closed handling. It does not prove provider-internal model isolation,
immutable model revision, stable provider routing, or independence from unknown
provider-side context.

## Closure

The execution RED is closed as an integration proof: a concrete provider
adapter received only the blinded semantic payload, invoked a real external
model, returned structured predictions, and successful predictions were
deterministically bound and scored by the existing Live Calibration Validator.
Malformed later provider responses were rejected without producing misleading
scores.

The stronger goal "same immutable provider model produces reproducible results"
is not established by the currently available Copilot `auto` route. That
requires an explicitly pinnable provider/model or stronger external
attestation/control-plane evidence.

### Cost-policy follow-up

Repository policy now uses GPT-6 Luna as the default cost baseline for
provider-backed checks. GitHub's current public model/pricing documentation
classifies GPT-6 Luna as a lightweight model and prices it below
MAI-Code-1.1-Flash.

The existing GitHub Actions identity was re-probed with explicit
`--model=gpt-6-luna` on Copilot CLI 1.0.86 and again on 1.0.88. Both executions
failed before semantic scoring with:

`Model "gpt-6-luna" from --model flag is not available.`

Therefore the repository must not pretend the current Actions identity can pin
GPT-6 Luna. The live workflow now defaults to the explicit GPT-6 Luna request
and exposes `auto` only as an operator-selected fallback/research option.
This means the cost-preferred baseline fails closed today rather than silently
routing to a different model.

No Core entity, scorer, orchestration framework, provider registry, consensus
mechanism or generic evaluator SDK was added.

A second provider/model comparison is not required to close this task. It is a
separate future case only if an independently executable second evaluator is
actually available.

## References

- GitHub Copilot CLI in Actions:
  https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions
- GitHub Copilot CLI programmatic reference:
  https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
- GitHub Copilot CLI command reference:
  https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- GitHub Models retirement:
  https://docs.github.com/en/github-models
