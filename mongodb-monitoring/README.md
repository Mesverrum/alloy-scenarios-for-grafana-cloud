---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# MongoDB monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **MongoDB**. This directory is an optional fake replica set with `job=integrations/mongodb_exporter`.

Collect MongoDB metrics with `prometheus.exporter.mongodb` and remote-write them to **Grafana Cloud**. The `job` label is `integrations/mongodb_exporter`. A sidecar initiates a single-node replica set and inserts documents so op-counters and replication metrics have values.

Works on Windows and Linux via Docker Compose.

## Run

**Windows:** `.\run-example.ps1 mongodb-monitoring`  
**Linux:** `./run-example.sh mongodb-monitoring`

Need `.env` from `.env.sample`. Ports **27017** and **12345**.

## Verify

```text
gcx metrics query 'mongodb_up{job="integrations/mongodb_exporter"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
