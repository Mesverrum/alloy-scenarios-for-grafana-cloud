# Grafana Cloud destinations

Shared Alloy writers for every scenario in this fork. Scenarios collect telemetry; this module sends it to Grafana Cloud. Do not run local Loki, Prometheus, Tempo, Grafana, or Pyroscope.

## Setup

1. Copy [`.env.sample`](../.env.sample) to `.env` at the repository root and fill in stack URLs, instance IDs, and an access-policy token.
2. Start a scenario with `./run-example.ps1 <dir>` (Windows) or `./run-example.sh <dir>` (Linux).
3. Confirm data in Cloud Grafana (`GC_GRAFANA_URL`) or with `gcx metrics query` / `gcx logs query` / `gcx traces`.

Docker Compose mounts this file at `/etc/alloy/cloud/destinations.alloy` and sets `GC_DESTINATIONS_FILE` to that path. Native Alloy reads `GC_DESTINATIONS_FILE` from `.env`.

## Signals

Instantiate only what the scenario uses:

| Component | Export | Cloud product |
| --------- | ------ | ------------- |
| `grafana_cloud.metrics "default" {}` | `.receiver` | Metrics / Mimir |
| `grafana_cloud.logs "default" {}` | `.receiver` | Logs / Loki |
| `grafana_cloud.otlp "default" {}` | `.input` | OTLP gateway (traces, and OTel metrics/logs) |
| `grafana_cloud.profiles "default" {}` | `.receiver` | Profiles / Pyroscope |

Scrape metrics at **1m** by default. Grafana Cloud metrics billing assumes 1 data point per minute; OSS examples often use 15s (4× DPM).

## Customer handoff

**Default:** Fleet Management integration template (or `pipeline.alloy` paste). Local Alloy is [`remotecfg.alloy`](remotecfg.alloy) only. See [`curated-paths.md`](curated-paths.md).

**Do not** give the customer `destinations.alloy` to paste into Fleet. Fleet appends `remote_write`.

`destinations.alloy` is only for Compose labs in this repo (SE practice, no customer collector).

For Kubernetes and Cloud Provider Observability, start with those wizards — not Alloy files.
