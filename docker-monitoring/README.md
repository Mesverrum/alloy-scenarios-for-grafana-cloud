---
os: [linux]
signals: [metrics, logs]
deploy: compose
cloud_products: [integrations]
---

# Docker monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **Docker**. This directory is an optional local Docker socket scrape with `job=integrations/docker`.

Collect container metrics (`prometheus.exporter.cadvisor`) and Docker logs into **Grafana Cloud**. The `job` label is `integrations/docker`. Metrics scrape at **1m** (Cloud 1 DPM); the OSS example used 10s (6× billed DPM).

**Linux/WSL only** — Docker socket and host mounts.

## Run

**WSL / Linux:** `./run-example.sh docker-monitoring`  
**Windows:** `.\run-example.ps1 docker-monitoring` (forwards to WSL)

Need `.env` with metrics **and** logs credentials. Port **12345**.

## Verify

```text
gcx metrics query '{job="integrations/docker"}'
gcx logs query '{job="integrations/docker"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
