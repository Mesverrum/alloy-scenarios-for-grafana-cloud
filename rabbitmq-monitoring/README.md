---
os: [linux]
signals: [metrics, logs]
deploy: compose
cloud_products: [integrations]
---

# RabbitMQ monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **RabbitMQ**. This directory is an optional fake broker with `job=integrations/rabbitmq`.

Scrape RabbitMQ's Prometheus endpoint and collect the broker container logs into **Grafana Cloud**. The `job` label is `integrations/rabbitmq`. Metrics scrape at **1m** (Cloud 1 DPM).

**Linux/WSL only** for logs (`unix:///var/run/docker.sock`).

## Run

**WSL / Linux:** `./run-example.sh rabbitmq-monitoring`  
**Windows:** `.\run-example.ps1 rabbitmq-monitoring` (forwards to WSL)

Need `.env` with metrics **and** logs credentials. Ports **5672**, **15672**, **15692**, **12345**.

## Verify

```text
gcx metrics query 'rabbitmq_build_info{job="integrations/rabbitmq"}'
gcx logs query '{job="integrations/rabbitmq"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
