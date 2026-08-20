---
os: [linux]
signals: [metrics, logs]
deploy: compose
cloud_products: [integrations]
---

# Alloy self-monitoring

Scrape Alloy's own metrics (`prometheus.exporter.self`) and collect Docker container logs (`loki.source.docker`) into **Grafana Cloud**. The metrics `job` is `integrations/alloy`.

**Linux/WSL only** — needs `unix:///var/run/docker.sock`. Native Windows Docker is not used in this fork.

## Run

**WSL / Linux:** `./run-example.sh self-monitoring`  
**Windows:** `.\run-example.ps1 self-monitoring` (forwards to WSL)

Need `.env` from `.env.sample` with **metrics and logs** URLs. Port **12345**.

## Verify

```text
gcx metrics query 'alloy_build_info{job="integrations/alloy"}'
gcx logs query '{container="alloy"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
