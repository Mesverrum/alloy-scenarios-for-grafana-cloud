---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# Microsoft SQL Server monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **MSSQL**. This directory is an optional fake SQL Server with `job=integrations/mssql`.

Collect SQL Server metrics with `prometheus.exporter.mssql` (including custom queries in `mssql-queries.yaml`) and remote-write them to **Grafana Cloud**. The `job` label is `integrations/mssql`.

Docker Compose runs in WSL or Linux. The SQL Server image is amd64.

## Run

**WSL / Linux:** `./run-example.sh mssql-monitoring`  
**Windows:** `.\run-example.ps1 mssql-monitoring` (forwards to WSL)

Need `.env` from `.env.sample`. Ports **1433** and **12345**.

## Verify

```text
gcx metrics query 'mssql_up{job="integrations/mssql"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
