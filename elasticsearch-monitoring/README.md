---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# Elasticsearch monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **Elasticsearch**. This directory is an optional fake cluster with `job=integrations/elasticsearch`.

Collect Elasticsearch metrics with `prometheus.exporter.elasticsearch` and remote-write them to **Grafana Cloud**. The `job` label is `integrations/elasticsearch`.

Docker Compose runs in WSL or Linux.

## Run

**WSL / Linux:** `./run-example.sh elasticsearch-monitoring`  
**Windows:** `.\run-example.ps1 elasticsearch-monitoring` (forwards to WSL)

Need `.env` from `.env.sample`. Ports **9200** and **12345**.

## Verify

```text
gcx metrics query 'elasticsearch_cluster_health_up{job="integrations/elasticsearch"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
