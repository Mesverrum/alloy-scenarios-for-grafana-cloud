---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# Memcached monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **Memcached**. This directory is an optional fake Memcached with `job=integrations/memcached`.

Collect Memcached metrics with `prometheus.exporter.memcached` and remote-write them to **Grafana Cloud**. The `job` label is `integrations/memcached`.

Works on Windows and Linux via Docker Compose.

## Run

**Windows:** `.\run-example.ps1 memcached-monitoring`  
**Linux:** `./run-example.sh memcached-monitoring`

Need `.env` from `.env.sample`. Ports **11211** and **12345**.

## Verify

```text
gcx metrics query 'memcached_up{job="integrations/memcached"}'
```

Alloy UI: http://localhost:12345

## Stop

`docker compose down`
