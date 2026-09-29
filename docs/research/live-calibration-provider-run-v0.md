# First real Live Calibration Run — execution integration v0

Status: provider adapter implemented; live CI execution pending.

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

Selected for the first run. Provider capability probing happened before any scorable result: explicit `claude-haiku-4.5`, `gpt-5.3-codex`, and `gpt-5-mini` requests were rejected as unavailable for the workflow identity. A one-shot `--model=auto` capability probe, isolated from the calibration corpus, resolved to provider model `gpt-6-luna`. The calibration descriptor was then pinned to `gpt-6-luna`; no calibration labels were inspected or used to make these execution-only changes.

Current GitHub documentation supports non-interactive Copilot CLI execution in
GitHub Actions with `copilot-requests: write` and the built-in
`GITHUB_TOKEN`. The Harness repository is personally owned, so this route does
not require a repository-stored provider API secret when the repository owner's
Copilot entitlement permits the request.

The run pins:

- execution provider: `github-copilot`;
- requested model: `gpt-6-luna`;
- Copilot CLI: `1.0.86`;
- provider adapter: `github-copilot-cli-live-calibration` v1;
- generic transport adapter: `process-json` v1.

GitHub Copilot does not expose an immutable provider model revision through the
selected silent CLI surface. The required v0 descriptor therefore uses the
explicit absence marker `model_version: UNREPORTED`; it is not presented as
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

A real scorer result is intentionally not predicted here. It is written only
after the provider workflow actually completes.

## References

- GitHub Copilot CLI in Actions:
  https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions
- GitHub Copilot CLI programmatic reference:
  https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
- GitHub Copilot CLI command reference:
  https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- GitHub Models retirement:
  https://docs.github.com/en/github-models
