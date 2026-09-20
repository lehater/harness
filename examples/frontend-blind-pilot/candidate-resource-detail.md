# Candidate Resource Detail Human Interface — Blind Slice 2

Status: experimental / non-canonical blind reconstruction  
Input boundary: Resource Catalogue use case/domain model plus accepted product/security/machine-interface knowledge; existing UI contracts excluded until comparison.

## User goal

Inspect one stable Resource, understand its current catalogue facts, inspect explanatory history, and perform supported Resource-authoring actions without confusing missing current facts with missing Resource identity.

## Navigation model

- Resource catalogue/list -> Resource detail by stable ResourceId.
- Resource detail -> catalogue/list.
- Resource detail -> history as subordinate detail state, not a separate domain object.
- After a successful replace/clear mutation, remain in Resource detail and refresh current + historical representation.

Exact URL is implementation/interface representation unless separately accepted.

## Resource detail view

Purpose: one stable Resource identity and its current/historical catalogue facts.

Always-visible identity:
- ResourceId;
- immutable AuthorityScopeRef as catalogue context, never as editable or derived authority;
- display name when supplied by accepted external contract.

Current fact groups:
- logical Endpoints;
- each Endpoint current AddressRealization or explicit no-current-address;
- current Site, or explicit absence;
- current OWNER responsibility, or explicit absence;
- current ADMINISTRATOR responsibility, or explicit absence.

History:
- prior address realizations;
- prior Site assignments;
- prior responsibility assignments;
- validity interval/provenance when available from accepted read contract;
- history remains subordinate to Resource identity/current facts.

## States

- loading — identity/context retained; no false current truth shown;
- loaded — Resource exists and current facts are available;
- partial-current — Resource exists while one or more current fact categories are absent;
- not-found — stable ResourceId does not resolve;
- error/unavailable — Resource truth could not currently be obtained;
- mutation-submitting;
- mutation-validation-rejected;
- mutation-conflict/stale-version;
- mutation-dependency-failure.

Critical distinctions:
- no current address != Resource not found;
- empty history != history unavailable;
- stale/conflict != validation error;
- Site/OWNER/ADMINISTRATOR != authority.

## Supported interactions

From accepted Resource Catalogue use case:
- add logical Endpoint;
- set/replace Endpoint HostAddress or Prefix;
- clear current Endpoint address;
- set/replace/clear Site;
- set/replace/clear OWNER;
- set/replace/clear ADMINISTRATOR.

After accepted mutation:
- stable ResourceId/EndpointRef remains unchanged where invariant requires it;
- new current fact becomes visible;
- replaced/ended fact remains explainable in history;
- aggregate version/conflict handling prevents lost-update success illusion.

## Interaction rules

- HostAddress and Prefix remain distinct semantic variants.
- Prefix input must not be silently host-bit-normalized if domain rejects that transformation.
- adding an Endpoint is explicit; UI must not auto-group endpoints by address/Site/responsibility/name.
- responsibility edits never imply an authority grant.
- trusted actor/permission/authority inputs are never editable client fields.

## History interaction

History may be inline, disclosure, tab or equivalent subordinate interaction.

Required semantics:
- current facts remain distinguishable while history is inspected;
- historical records are visibly non-current;
- empty history is explicit;
- validity/provenance is shown when provided by accepted interface contract.

Exact interaction control remains free.

## Recovery

- not-found offers return to Resource catalogue/list;
- retryable read failure exposes retry;
- mutation validation keeps the relevant authoring context;
- stale-version conflict requires reload/reconciliation before claiming success;
- dependency failure remains operational failure and does not rewrite catalogue semantics.

## Deliberately unconstrained

- route string;
- page vs panel shell;
- table/card/list presentation;
- history tab vs disclosure;
- exact layout;
- responsive breakpoints;
- component library;
- visual tokens;
- framework/state library.
