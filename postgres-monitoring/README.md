---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# PostgreSQL monitoring

**POV path:** Fleet Management → Create pipeline → **PostgreSQL** template (Linux/Windows). Connections → Install dashboards. Local Alloy is `remotecfg` only — see [`_cloud/curated-paths.md`](../_cloud/curated-paths.md).

This directory is optional SE practice: a synthetic Postgres so the Cloud dashboard lights up without a customer database. Do not enroll this Compose Alloy in Fleet. `job=integrations/postgres_exporter`, scrape **1m**.

Collect PostgreSQL server metrics with `prometheus.exporter.postgres` and remote-write them to **Grafana Cloud**.

Works on Windows and Linux via Docker Compose. Visualization is your Cloud stack, not a local Grafana.

## Before you begin

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Repo-root `.env` copied from `.env.sample` with Grafana Cloud metrics URL, instance ID, and access-policy token
- Ports **5432** (Postgres) and **12345** (Alloy UI) free on the host

## Architecture

```text
+----------+       +-------+       +----------------+
| postgres |  DSN  | Alloy |------>| Grafana Cloud  |
|          |<----->|       |       | Metrics        |
+----------+       +-------+       +----------------+
                                         |
                                         v
                                   Cloud Grafana
```

- **postgres**: PostgreSQL 18 on port 5432, user `alloy`, database `alloy`
- **Alloy**: scrapes the postgres exporter every 1m (Grafana Cloud 1 DPM) and remote-writes to Cloud
- **Grafana Cloud**: stores metrics; open Explore or the PostgreSQL integration dashboard

## Run the scenario

From the repository root, after `.env` is filled in:

**Windows (PowerShell, forwards to WSL Docker)**

```powershell
.\run-example.ps1 postgres-monitoring
```

**WSL / Linux (bash)**

```bash
./run-example.sh postgres-monitoring
```

Or from this directory: `docker compose --env-file ../image-versions.env --env-file ../.env up -d`

Check containers: `docker compose ps`  
Expect `postgres` and `alloy` (no Prometheus or Grafana).

## Explore

- **Alloy UI**: http://localhost:12345 — component graph and live debugging
- **Cloud Grafana**: `$GC_GRAFANA_URL` → Explore → Metrics datasource

### Verify with gcx

```text
gcx metrics query 'pg_up{job="integrations/postgres_exporter"}'
```

Expect `1` after the first scrape (~1m).

### PromQL

- `pg_up{job="integrations/postgres_exporter"}` — reachability
- `{__name__=~"pg_stat_database_.*",job="integrations/postgres_exporter"}` — database stats
- `{job="integrations/postgres_exporter"}` — all exporter series

## Alloy pipeline

1. Import `_cloud/destinations.alloy` and instantiate `grafana_cloud.metrics`
2. `prometheus.exporter.postgres` connects to `postgresql://alloy:alloy@postgres:5432/alloy?sslmode=disable`
3. `discovery.relabel` sets `job=integrations/postgres_exporter`
4. `prometheus.scrape` every 1m → Cloud remote write (1 DPM; do not drop this to 15s in a customer POV)

## Customize

- Change `data_source_names` for a real customer Postgres
- **Change scrape interval**: Keep **1m** for Cloud POVs (1 DPM). Going to 15s multiplies billed metric volume by 4.
- Credentials stay in `.env`; do not hard-code Cloud tokens in `config.alloy`

## Troubleshoot

- `docker compose logs alloy` — missing `GC_*` env vars fail Alloy at startup
- No `pg_up` in Cloud: wait 15–30s, then confirm remote_write in the Alloy UI
- Port 5432 or 12345 already bound: change the host mapping in `docker-compose.yml`

## Stop

```text
docker compose down
```

## Customer handoff

Fleet → Create pipeline → PostgreSQL template. Connections → Install dashboards. DSN via collector env. Local Alloy is remotecfg only. Do not paste this directory’s `config.alloy` or `destinations.alloy` into Fleet.

## Next steps

- Alloy `prometheus.exporter.postgres`: https://grafana.com/docs/alloy/latest/reference/components/prometheus/prometheus.exporter.postgres/
- Grafana Cloud PostgreSQL integration dashboards in the Cloud Connections UI
