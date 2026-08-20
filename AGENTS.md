# Agent guide — Grafana Cloud Alloy scenarios

This fork sends telemetry to **Grafana Cloud**. Do not start local Loki, Prometheus, Tempo, Grafana, or Pyroscope.

## Before changing or running a scenario

1. Credentials live in gitignored `.env` (copy from `.env.sample`). Never invent URLs or tokens. Never commit `.env`.
2. Destinations live in [`_cloud/destinations.alloy`](_cloud/destinations.alloy) for **Compose labs only**. Customer path is Fleet templates or `pipeline.alloy` (no destinations). Local disk: [`_cloud/remotecfg.alloy`](_cloud/remotecfg.alloy).
3. POV routing: [`_cloud/pov-index.yaml`](_cloud/pov-index.yaml) maps checkbox → wizard or directory → verify queries. Curated products: [`_cloud/curated-paths.md`](_cloud/curated-paths.md).

## Run

Docker Compose scenarios are meant to run where Docker runs. On this fork that is **Linux or WSL**, not native Windows Docker.

- **WSL / Linux:** `./run-example.sh <scenario-dir>` (requires `.env`)
- **Windows PowerShell:** `.\run-example.ps1 <scenario-dir>` forwards to WSL. Do not expect a Windows Docker daemon.

Alloy UI is `http://localhost:12345` (published from WSL Docker). Visualization is Cloud Grafana (`GC_GRAFANA_URL`), not `localhost:3000`.

Syntax-only check (no Postgres, no Cloud token):

```text
# from WSL
./validate-alloy.sh

# from Windows PowerShell
.\validate-alloy.ps1
```

## Verify with gcx

Prefer gcx over clicking around in the UI.

```text
gcx login --server https://<stack>.grafana.net
gcx config current-context
gcx metrics query '<promql from pov-index>'
gcx logs query '<logql>'
gcx fleet collectors list
```

Do not mint access-policy tokens via gcx unless a command exists for it. Ingest `GC_TOKEN` comes from Cloud Access Policies / the OTLP tile.

## Paid Cloud products — prefer these paths

Wizards and deep links: [`_cloud/curated-paths.md`](_cloud/curated-paths.md).

| Customer ask | First path | Fallback in this repo |
| ------------ | ---------- | --------------------- |
| Kubernetes observability | Instrumentation Hub + `$GC_GRAFANA_URL/a/grafana-k8s-app/configuration` | `k8s/cloud-full` Helm values |
| AWS / Azure / GCP | Observability → Cloud provider (CPO) | Alloy labs in `cloudwatch-metrics/`, `aws-firehose-logs/`, `azure-event-hubs-logs/` are **not** the POV |
| Database / host integrations | Fleet → Create pipeline → **integration template**; Connections → Install dashboards | Compose `*-monitoring/` only if you need a fake workload |
| Custom Alloy / no template | Fleet → paste scenario `pipeline.alloy` | Never paste `destinations.alloy` into Fleet (it already appends remote_write) |
| Config at scale / Windows hosts | Fleet Management (`gcx fleet`) + [`_cloud/remotecfg.alloy`](_cloud/remotecfg.alloy) | Native Alloy local file is remotecfg only |

Instrumentation Hub is Linux Kubernetes today. Windows POVs use native Alloy + Fleet templates. Compose labs are not Fleet collectors.

## OS rules

- Tag each scenario `os: [linux, windows, any]` in README frontmatter / pov-index.
- Linux-only sources (`loki.source.journal`, `prometheus.exporter.unix`, docker.sock) stay tagged linux.
- Windows-only sources (`prometheus.exporter.windows`, `loki.source.windowsevent`) stay first-class.
- README commands: `docker compose` is shared and runs in Linux/WSL. `run-example.ps1` / `validate-alloy.ps1` only wrap WSL. Do not assume a Windows Docker daemon.

## New or converted scenarios

- If Grafana Cloud has a Fleet **integration template**, the README is a click-path (template + matching attributes). Do not invent a competing River file for the customer.
- Custom / no template: add `pipeline.alloy` — Fleet-ready body only. No `import.file`, no `remotecfg`, no `grafana_cloud.*`. Forward to `prometheus.remote_write.metrics_service.receiver` and/or `loki.write.grafana_cloud_loki.receiver`.
- Compose `config.alloy` is optional SE practice (synthetic workload). It may import `_cloud/destinations.alloy`. Never enroll that container in Fleet.
- Alloy + workload only in `docker-compose.yml`. Mount `_cloud/destinations.alloy`. Set `GC_DESTINATIONS_FILE=/etc/alloy/cloud/destinations.alloy` on the Alloy service. `env_file: ../.env`.
- Do not add Loki/Prometheus/Tempo/Grafana/Pyroscope services or their config YAML.
- Align `job` labels with Cloud integrations when an integration exists.
- Default `scrape_interval` is **1m**. Grafana Cloud metrics billing assumes 1 data point per minute; 15s scrapes are 4× DPM and cause POV sticker shock. Faster intervals need an explicit comment and a cost callout in the README.
- Include gcx verify queries in the README.
