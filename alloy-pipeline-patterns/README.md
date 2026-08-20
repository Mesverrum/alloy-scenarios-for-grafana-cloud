---
os: [linux, windows]
signals: [metrics, logs]
deploy: compose
cloud_products: []
---

# Alloy pipeline patterns (labels, relabel, filters)

**POV path:** no Cloud integration for this. Fleet → Custom pipeline → paste [`pipeline.alloy`](pipeline.alloy) (or splice the rules into an existing template). Splice means: integration scrape `forward_to` → `prometheus.relabel.shaped` / `loki.process.shaped` instead of straight to remote_write.

Compose in this directory is SE practice with a noisy generator. Do not enroll that Alloy in Fleet.

This is **not** Adaptive Telemetry. Adaptive recommends drop/aggregation from query usage inside Cloud. These rules are explicit and run in Alloy (they also save egress).

## What the pipeline shows

| Signal | Component | Action |
| ------ | --------- | ------ |
| Metrics | `discovery.relabel` | Create `job`, `instance`, `env` on the scrape target |
| Metrics | `prometheus.relabel` `keep` | Drop `noisy_debug_total` |
| Metrics | `labeldrop` | Remove `request_id`, `user_id` |
| Metrics | `replace` | Normalize `/api/orders/1001` → `/api/orders/:id`; rename `method` → `http_method` |
| Metrics | `lowercase` | Normalize `http_method` |
| Metrics | `hashmod` | `instance` → `shard` (modulus 4) |
| Metrics | `labelkeep` | Allowlist remaining labels |
| Metrics | static `target_label` | Add `pipeline`, `team` |
| Logs | `stage.json` | Parse the line, including `ts` |
| Logs | `stage.timestamp` | Use the JSON `ts` field (`RFC3339`) instead of ingest time |
| Logs | `stage.drop` | Drop `/health`, `/ready`, and `level=debug` |
| Logs | `stage.replace` | Same path normalize on logs |
| Logs | `stage.sampling` | Keep 50% of `{level="info"}`; keep all errors |
| Logs | `stage.limit` | Cap at 20 lines/s (`drop = true`) |
| Logs | `stage.metrics` | Count surviving lines as `alloy_pipeline_shaped_log_lines_total` |
| Logs | `stage.static_labels` | Invent `env`, `pipeline`, `team` |
| Logs | `stage.labels` | Index `level`, `method`, `status`, `service` |
| Logs | `stage.structured_metadata` | Keep `request_id` and `path` off the label index |
| Logs | `stage.match` | Extra `alert_worthy=true` only on `{level="error"}` |

Related labs: [`metric-cardinality-control`](../metric-cardinality-control/) (before/after fan-out), [`log-secret-filtering`](../log-secret-filtering/), [`log-to-metrics`](../log-to-metrics/), [`otel-examples/cost-control`](../otel-examples/cost-control/) (OTel filter/sample), [`otel-tail-sampling`](../otel-tail-sampling/).

## Run

**Windows:** `.\run-example.ps1 alloy-pipeline-patterns`  
**Linux / WSL:** `./run-example.sh alloy-pipeline-patterns`

Alloy UI: http://localhost:12345 — open `prometheus.relabel.shaped` and `loki.process.shaped` live debug.

## Verify

Wait ~1m for the first scrape.

```text
gcx metrics query 'app_up{job="alloy_pipeline_patterns"}'
gcx metrics query 'http_requests_total{job="alloy_pipeline_patterns"}'
gcx metrics query 'alloy_pipeline_shaped_log_lines_total'
gcx logs query '{job="alloy_pipeline_patterns", pipeline="alloy_process"}'
```

Expect: `app_up=1`; request series with `route` like `/api/orders/:id`, lowercase `http_method`, and a `shard` label; **no** `request_id` label; logs without `/health` or debug lines; error logs with `alert_worthy=true`; fewer info lines than the generator writes (sampling).

In Cloud Explore, `noisy_debug_total` must be absent. `user_id` must not appear on `http_requests_total`.
