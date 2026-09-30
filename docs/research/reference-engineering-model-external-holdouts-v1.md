# Reference Engineering Model — external hold-outs v1

Status: active research.

## Question

Does the frozen Reference Engineering Model v0 survive a second external hold-out batch that did not participate in its construction?

## Freeze rule

`spec/research/reference-engineering-model-v0.yaml` is immutable for this experiment.

A failing hold-out is evidence against the current model. Do not modify v0 to make this batch green.

## External hold-outs

### Browser extension

Evidence basis:

- Manifest V3 supports popup/side-panel user interfaces and privileged permissions.
- extension service workers are event driven;
- extension storage persists data independently of service-worker lifetime.

Sources:

- https://developer.chrome.com/docs/extensions/mv3/manifest
- https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/basics
- https://developer.chrome.com/docs/extensions/develop/concepts/storage-and-cookies

### Stripe webhook consumer

Evidence basis:

- production endpoints are public HTTPS endpoints;
- webhook requests are authenticated with a signing secret;
- live delivery is retried automatically;
- duplicate and out-of-order events must be handled;
- asynchronous processing is recommended.

Source:

- https://docs.stripe.com/webhooks

### Airflow DAG pipeline

Evidence basis:

- a DAG defines scheduled tasks and dependencies;
- tasks can be retried;
- retry-safe tasks should avoid incomplete or duplicate durable outputs;
- runtime dependencies and operational execution are explicit parts of a deployed DAG.

Sources:

- https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html
- https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

### Prometheus exporter

Evidence basis:

- exporters expose metrics over HTTP;
- exporter collectors may be scraped concurrently;
- exporters commonly query an external monitored system;
- exposed HTTP endpoints create an explicit security boundary.

Sources:

- https://prometheus.io/docs/instrumenting/writing_exporters/
- https://prometheus.io/docs/operating/security/

## Acceptance rule

Each scenario declares only a subset of required and forbidden templates. The materializer must remain deterministic and every `STABLE` graph must pass the existing Engineering Graph validator.

If any hold-out produces a different status or violates an asserted required/forbidden template, record the mismatch as a falsification result before considering any Reference Model change.

## First-run calibration

The first CI run rejected the Prometheus exporter oracle because the fixture required `SECURITY-ANALYSIS` from `network_exposed` alone. That expectation was stronger than both the accepted project facts and the frozen v0 applicability contract. The fixture was corrected to require `SECURITY-ARCHITECTURE` only; the Reference Model was not changed.
