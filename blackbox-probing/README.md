---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# Blackbox probing

Probe HTTP endpoints with `prometheus.exporter.blackbox` and remote-write probe metrics to **Grafana Cloud**. Targets: the local nginx demo and `https://grafana.com`. The `job` label is `integrations/blackbox`.

This is the Alloy version of synthetic HTTP checks. For Cloud **Synthetic Monitoring** as a paid product, use `gcx synthetic-monitoring` instead of this collector.

Docker Compose runs in WSL or Linux.

## Run

**WSL / Linux:** `./run-example.sh blackbox-probing`  
**Windows:** `.\run-example.ps1 blackbox-probing` (forwards to WSL)

Need `.env` from `.env.sample`. Ports **8080** and **12345**.

## Verify

```text
gcx metrics query 'probe_success{job="integrations/blackbox"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
