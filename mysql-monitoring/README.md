---
os: [linux, windows]
signals: [metrics]
deploy: compose
cloud_products: [integrations]
---

# MySQL monitoring

**POV path:** `$GC_GRAFANA_URL/connections/add-new-connection` → search **MySQL**. This directory is an optional fake MySQL with `job=integrations/mysqld_exporter`.

Collect MySQL metrics with `prometheus.exporter.mysql` and remote-write them to **Grafana Cloud**. The `job` label is `integrations/mysqld_exporter` so the Cloud MySQL integration dashboard can light up.

Works on Windows and Linux via Docker Compose.

## Before you begin

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Repo-root `.env` copied from `.env.sample`
- Ports **3306** and **12345** free on the host

## Architecture

```text
+-------+       +-------+       +----------------+
| MySQL |------>| Alloy |------>| Grafana Cloud  |
| :3306 |       |       |       | Metrics        |
+-------+       +-------+       +----------------+
```

## Run

**Windows:** `.\run-example.ps1 mysql-monitoring`  
**Linux:** `./run-example.sh mysql-monitoring`

Expect `mysql` and `alloy` from `docker compose ps`.

## Verify

- Alloy UI: http://localhost:12345
- Cloud Grafana: `$GC_GRAFANA_URL` → Explore

```text
gcx metrics query 'mysql_up{job="integrations/mysqld_exporter"}'
```

PromQL: `mysql_up{job="integrations/mysqld_exporter"}`, `{job="integrations/mysqld_exporter"}`

## Stop

`docker compose down` from this directory.

## Customer handoff

Copy `config.alloy` and `_cloud/destinations.alloy`. Point `GC_*` at the customer stack and replace the demo DSN.
