---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# SNMP monitoring

Walk a local `snmpd` with `prometheus.exporter.snmp` and remote-write to **Grafana Cloud**. The `job` label is `integrations/snmp`. Metrics scrape at **1m** (Cloud 1 DPM).

Docker Compose runs in WSL or Linux.

## Run

**WSL / Linux:** `./run-example.sh snmp`  
**Windows:** `.\run-example.ps1 snmp` (forwards to WSL)

Need `.env` from `.env.sample`. Port **12345**.

## Verify

```text
gcx metrics query '{job="integrations/snmp"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
