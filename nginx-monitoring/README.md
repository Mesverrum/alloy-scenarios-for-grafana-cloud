---
os: [linux, windows]
signals: [metrics, logs]
deploy: compose
cloud_products: [integrations]
---

# NGINX monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **NGINX**. This directory is an optional fake NGINX with `job=integrations/nginx`.

Tail NGINX access/error logs and scrape `nginx-prometheus-exporter` into **Grafana Cloud**. The `job` label is `integrations/nginx`. Metrics scrape at **1m** (Cloud 1 DPM).

Docker Compose runs in WSL or Linux.

## Run

**WSL / Linux:** `./run-example.sh nginx-monitoring`  
**Windows:** `.\run-example.ps1 nginx-monitoring` (forwards to WSL)

Need `.env` with metrics **and** logs credentials. Ports **8080** and **12345**.

## Verify

```text
gcx metrics query 'nginx_up{job="integrations/nginx"}'
gcx logs query '{job="integrations/nginx"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
