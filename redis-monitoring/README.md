---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# Redis monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **Redis**. This directory is an optional fake Redis with `job=integrations/redis`.

Collect Redis metrics with `prometheus.exporter.redis` and remote-write them to **Grafana Cloud**. The `job` label is `integrations/redis` so the Cloud Redis integration dashboard can light up.

Works on Windows and Linux via Docker Compose.

## Before you begin

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Repo-root `.env` copied from `.env.sample`
- Ports **6379** and **12345** free on the host

## Architecture

```text
+-------+       +-------+       +----------------+
| Redis |------>| Alloy |------>| Grafana Cloud  |
| :6379 |       |       |       | Metrics        |
+-------+       +-------+       +----------------+
```

## Run

**Windows:** `.\run-example.ps1 redis-monitoring`  
**Linux:** `./run-example.sh redis-monitoring`

Expect `redis` and `alloy` from `docker compose ps`.

## Verify

- Alloy UI: http://localhost:12345
- Cloud Grafana: `$GC_GRAFANA_URL` → Explore

```text
gcx metrics query 'redis_up{job="integrations/redis"}'
```

PromQL: `redis_up{job="integrations/redis"}`, `{job="integrations/redis"}`

## Stop

`docker compose down` from this directory.

## Customer handoff

Copy `config.alloy` and `_cloud/destinations.alloy`. Point `GC_*` at the customer stack and replace `redis:6379` with the customer address.
