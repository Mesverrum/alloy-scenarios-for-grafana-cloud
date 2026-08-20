# CLAUDE.md

This file provides guidance when working in this repository.

## Project Overview

This is a **Grafana Cloud** fork of Alloy demonstration scenarios. Each scenario lives in its own top-level directory and sends telemetry to Grafana Cloud (metrics, logs, traces, profiles). Do not run a local Loki / Prometheus / Tempo / Grafana / Pyroscope stack.

Read [`AGENTS.md`](AGENTS.md), [`_cloud/README.md`](_cloud/README.md), and [`_cloud/curated-paths.md`](_cloud/curated-paths.md) before adding or converting a scenario. Kubernetes, Cloud Provider Observability, and database integrations use Cloud wizards first; Alloy/Compose in this repo is the fallback.

## Running Scenarios

Copy `.env.sample` to `.env` and fill in Grafana Cloud credentials first.

Docker Compose runs in **WSL or Linux**, not a Windows Docker daemon.

```powershell
# Windows → WSL
.\run-example.ps1 <scenario-dir>
.\validate-alloy.ps1
```

```bash
# WSL / Linux
./run-example.sh <scenario-dir>
./validate-alloy.sh
```

Stop a scenario from WSL: `cd <scenario-dir> && docker compose down`

Image versions are centralized in `image-versions.env`. Kubernetes scenarios use Helm or Instrumentation Hub — see `k8s/` and `_cloud/`.

## Scenario Structure

```
scenario-name/
├── docker-compose.yml  # Alloy + demo workloads only (no local LGTM)
├── config.alloy        # Pipeline; imports _cloud/destinations.alloy
├── README.md           # POV, OS tags, gcx verify queries, Cloud UI path
└── app/                # Optional demo application
```

Shared Cloud writers: `_cloud/destinations.alloy`. Credentials: repo-root `.env` (gitignored).

## Alloy Configuration Language

`config.alloy` files use Alloy's River syntax. Pipelines:

1. **Receivers/Sources** — ingest data
2. **Processors/Transformers** — parse, relabel, batch
3. **Writers** — `grafana_cloud.metrics` / `logs` / `otlp` / `profiles` from the destinations module

## Creating a New Scenario

Templates: `.cursor/docker-example.mdc` (Docker) and `.cursor/k8s-example.mdc` (Kubernetes).

Checklist:

1. New top-level directory
2. `docker-compose.yml` with Alloy + workload only; `env_file: ../.env`; mount `_cloud/destinations.alloy`
3. `config.alloy` imports the Cloud destinations module
4. README with OS tags, Cloud Grafana path, gcx verify queries
5. Add the scenario to `_cloud/pov-index.yaml` and the main README
6. Alloy UI at `http://localhost:12345`

## Key Conventions

- Visualization is Grafana Cloud (`GC_GRAFANA_URL`), not localhost:3000
- Alloy HTTP server on port 12345
- Align `job` labels with Cloud integrations (`integrations/postgres_exporter`, …)
- Default scrape interval is 1m (Grafana Cloud 1 DPM billing). Do not copy OSS 15s scrapes.
- Windows and Linux command examples; tag Linux-only or Windows-only sources
- Prefer Instrumentation Hub (Linux k8s), Cloud Provider Observability, and Connections integrations over hand-rolled collector sprawl. See `_cloud/curated-paths.md`.
