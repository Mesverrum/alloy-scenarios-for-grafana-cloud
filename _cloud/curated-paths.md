# Grafana Cloud curated paths

POV default for productized observability. Do **not** start with a hand-rolled Alloy pipeline when a Cloud wizard exists.

Replace `$GC_GRAFANA_URL` with the stack URL from `.env` (no trailing slash).

| Customer ask | Open this | What it does |
| ------------ | --------- | ------------ |
| Kubernetes (Linux clusters) | [Instrumentation Hub](https://grafana.com/docs/grafana-cloud/learn-and-build/get-started/set-up-your-account/inst-hub-setup/) in the stack nav, then `$GC_GRAFANA_URL/a/grafana-k8s-app/configuration` | Installs Alloy, optional Beyla, activates Kubernetes Monitoring |
| Kubernetes GitOps / Helm | Same k8s-app configuration page (copy the generated Helm command) or [`k8s/cloud-full`](../k8s/cloud-full/) | Chart values that remote-write to this stack |
| AWS / Azure / GCP | **Observability → Cloud provider**, or `$GC_GRAFANA_URL/connections/add-new-connection` and search AWS / Azure / GCP | Cloud Provider Observability (no Alloy) |
| Databases, caches, Linux, Windows, NGINX, Docker, vSphere | **Fleet Management → Create pipeline → integration template**, then Connections → Install dashboards | Cloud Integrations via Fleet. Local Alloy is `remotecfg` only. |
| Custom Alloy (relabel, syslog shaping, …) | Fleet → Create pipeline → paste `pipeline.alloy` | Only when no integration template exists |
| Fleet onboarding / Windows hosts | **Observability → Fleet Management** | Collector inventory + remote config |

gcx after `gcx login --server $GC_GRAFANA_URL`:

```text
gcx instrumentation          # Instrumentation Hub (Linux k8s)
gcx fleet collectors list    # Fleet Management
gcx metrics query '<promql>'
gcx logs query '<logql>'
```

## Kubernetes

**Use in a POV:** Instrumentation Hub (Linux Kubernetes). Windows nodes are native Alloy + Fleet, not Instrumentation Hub.

**Do not:** install in-cluster Prometheus, Loki, Tempo, Grafana, or Pyroscope from the old `k8s/*/prometheus-values.yml` / `loki-values.yml` files.

GitOps fallback: create a Secret from repo-root `.env`, then Helm with [`k8s/cloud-full`](../k8s/cloud-full/). Per-signal values also live under `k8s/metrics`, `k8s/logs`, `k8s/tracing`, `k8s/profiling`.

```sh
kubectl create namespace meta
kubectl create secret generic grafana-cloud --from-env-file=.env -n meta
```

## Cloud Provider Observability

**Use in a POV:** Observability → Cloud provider → AWS / Azure / GCP. Account connect, scrape or Firehose, curated views.

The directories `cloudwatch-metrics/`, `aws-firehose-logs/`, and `azure-event-hubs-logs/` are **collector internals** (Alloy talking to fake LocalStack / Firehose / Event Hubs). They are not the Cloud AWS/Azure story. Do not run them against a real account that is already onboarded in CPO (double ingest).

| Lab directory | Cloud product instead |
| ------------- | --------------------- |
| `cloudwatch-metrics` | CPO CloudWatch scrape or metric streams |
| `aws-firehose-logs` | CPO Logs with Firehose (Firehose → Grafana Cloud, not Alloy) |
| `azure-event-hubs-logs` | CPO Azure metrics (serverless) + Azure logs (Function or Alloy only if they already run Alloy) |

## Database and infrastructure integrations

**Use in a POV:** collector already in Fleet (or onboard with [`remotecfg.alloy`](remotecfg.alloy) only) → **Fleet Management → Remote configuration → Create configuration pipeline → pick platform → pick the integration**. Fleet prefills the River and **appends `remote_write`**. Then Connections → Install so dashboards/alerts exist.

Do **not** hand the customer `config.alloy` from this repo when that integration is in the Fleet picker. Do **not** paste [`destinations.alloy`](destinations.alloy) into a Fleet pipeline.

Compose directories below are SE practice (synthetic DB, no customer collector). `job` labels still match the integration. Scrape interval is **1m**.

| Integration | Fleet | Connections search | `job` label | Compose lab (optional) |
| ----------- | ----- | ------------------ | ----------- | ---------------------- |
| PostgreSQL | Template | PostgreSQL | `integrations/postgres_exporter` | `postgres-monitoring/` |
| MySQL | Template | MySQL | `integrations/mysqld_exporter` | `mysql-monitoring/` |
| Redis | Template | Redis | `integrations/redis` | `redis-monitoring/` |
| MongoDB | Template | MongoDB | `integrations/mongodb_exporter` | `mongodb-monitoring/` |
| Elasticsearch | Template | Elasticsearch | `integrations/elasticsearch` | `elasticsearch-monitoring/` |
| SQL Server | Template | MSSQL | `integrations/mssql` | `mssql-monitoring/` |
| Memcached | Template | Memcached | `integrations/memcached` | `memcached-monitoring/` |
| NGINX | Template | NGINX | `integrations/nginx` | `nginx-monitoring/` |
| RabbitMQ | Template | RabbitMQ | `integrations/rabbitmq` | `rabbitmq-monitoring/` |
| Linux node | Template | Linux Node | `integrations/node_exporter` | `linux/` |
| Windows | Template | Windows | (Windows exporter) | `windows/` |
| Docker | Template | Docker | `integrations/docker` | `docker-monitoring/` |
| SNMP | Template | SNMP | `integrations/snmp` | `snmp/` |
| vSphere / vCenter | Template if listed, else paste [`vcenter-monitoring/pipeline.alloy`](../vcenter-monitoring/pipeline.alloy) | vSphere | `integrations/vsphere` | `vcenter-monitoring/` (real vCenter) |
| Relabel / drop / log shaping | Paste [`alloy-pipeline-patterns/pipeline.alloy`](../alloy-pipeline-patterns/pipeline.alloy) | — | — | `alloy-pipeline-patterns/` |

Deep-link pattern (search if a slug 404s):

```text
$GC_GRAFANA_URL/connections/add-new-connection
```

## Fleet Management (ideal path: almost no local config)

The only Alloy that should live on disk is [`remotecfg.alloy`](remotecfg.alloy). Fleet already has **integration templates** for Linux, Windows, Postgres, MySQL, NGINX, Docker, SNMP, and the rest of the Connections catalog. Self-monitoring pipelines are created for you.

POV sentence:

> Install Alloy with the Fleet onboarding snippet. Enable the integration template (or paste `pipeline.alloy` if there is no template). Do not maintain a local `config.alloy`.

### Order of operations

1. **Onboard** — Fleet Management UI → copy the install/`remotecfg` snippet onto the host (Linux package, Windows MSI, or k8s via Instrumentation Hub). Local file = remotecfg + attributes only.
2. **Dashboards** — Connections → Install the integration (alerts + dashboards). This does not have to install a second Alloy.
3. **Config** — Fleet → Remote configuration → Create pipeline:
   - **Template exists** → pick platform → pick integration → set matching attributes (`os=linux`, `role=database`, …). Edit DSN/endpoint env vars on the collector. Stop. Do not paste this repo.
   - **No template** → Custom → paste that scenario’s `pipeline.alloy`. Fleet appends `prometheus.remote_write` / Loki write. Do not paste `destinations.alloy` or `import.file`.
4. **Verify** — `gcx fleet collectors list`, then the README PromQL/LogQL.

Compose `config.alloy` in this repo is for SE practice when there is no collector and you need a fake workload. Never enroll that Docker Alloy in Fleet.

### What to paste vs what to click

| Need | Do this |
| ---- | ------- |
| Postgres, MySQL, Linux, Windows, NGINX, Docker, SNMP, … | Fleet integration **template** |
| vSphere | Template if the picker has it; else [`vcenter-monitoring/pipeline.alloy`](../vcenter-monitoring/pipeline.alloy) |
| Keep/drop/relabel/structured metadata | [`alloy-pipeline-patterns/pipeline.alloy`](../alloy-pipeline-patterns/pipeline.alloy) spliced into the template (change `forward_to` to the shaping components) |
| Kubernetes | Instrumentation Hub (registers collectors in Fleet) |
| AWS / Azure / GCP | Cloud Provider Observability — not Fleet |

`pipeline.alloy` files in this repo are Fleet-shaped: no `remotecfg`, no destinations module, `forward_to = [prometheus.remote_write.metrics_service.receiver]` and `loki.write.grafana_cloud_loki.receiver` (names Fleet injects).

Windows: Hub does not cover it. MSI + remotecfg + Windows **template**.

vCenter: match `role=vsphere` on a **Linux jump host**, not the VCSA.

Alloy clustering is scrape sharding, not Fleet.

Docs: [integration templates](https://grafana.com/docs/grafana-cloud/observe-and-act/send-data/fleet-management/set-up/configuration-pipelines/integrations/), [onboard standalone Alloy](https://grafana.com/docs/grafana-cloud/send-data/fleet-management/set-up/onboard-collectors/standalone-alloy/).

