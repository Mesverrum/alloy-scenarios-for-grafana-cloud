<p align="center">
  <img src="./img/banner.png" alt="Grafana Alloy Scenarios Banner" width="300"/>
</p>

# Grafana Alloy scenarios for Grafana Cloud

This fork of [alloy-scenarios](https://github.com/grafana/alloy-scenarios) is optimized for **Grafana Cloud** POVs: Alloy (or Instrumentation Hub / Fleet Management) collects telemetry; Grafana Cloud stores and visualizes it. There is no local Loki, Prometheus, Tempo, or Grafana.

Read [`AGENTS.md`](AGENTS.md) and [`_cloud/README.md`](_cloud/README.md) for credentials, the shared destinations module, and the agent + gcx verify loop. Productized paths (k8s, CPO, DBs) are in [`_cloud/curated-paths.md`](_cloud/curated-paths.md).

## POV open (use these, not Alloy labs)

| Ask | Open |
| --- | ---- |
| Kubernetes | Instrumentation Hub, then `$GC_GRAFANA_URL/a/grafana-k8s-app/configuration` — see [`k8s/`](k8s/) |
| AWS / Azure / GCP | **Observability → Cloud provider** — see [`cloudwatch-metrics/`](cloudwatch-metrics/), [`aws-firehose-logs/`](aws-firehose-logs/), [`azure-event-hubs-logs/`](azure-event-hubs-logs/) (stubs) |
| PostgreSQL, MySQL, Redis, … | `$GC_GRAFANA_URL/connections/add-new-connection` — Compose labs below only if you need a fake database |

Converted Cloud-ready scenarios so far: Docker scenarios send to Grafana Cloud via `_cloud/destinations.alloy`. Kubernetes, CPO, and database **product** demos start in the stack UI, not Compose.

## Before you begin

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Git
- Grafana Cloud stack credentials in `.env` (copy `.env.sample`)

## Run a scenario

Copy `.env.sample` to `.env` and fill in Cloud URLs, instance IDs, and an access-policy token.

Docker Compose runs in **Linux or WSL**. Native Windows does not run Docker in this workflow.

**WSL / Linux**

```bash
cp .env.sample .env
./run-example.sh postgres-monitoring
```

**Windows PowerShell** (forwards to WSL)

```powershell
Copy-Item .env.sample .env
.\run-example.ps1 postgres-monitoring
```

Syntax-only Alloy check (no database, no Cloud token): `./validate-alloy.sh` or `.\validate-alloy.ps1`.

Image versions are in `image-versions.env`. Kubernetes: prefer [Instrumentation Hub](https://grafana.com/docs/grafana-cloud/learn-and-build/get-started/set-up-your-account/inst-hub-setup/) (Linux clusters); Helm values under `k8s/` are the GitOps fallback.

## Explore the services

- **Alloy UI** at http://localhost:12345
- **Grafana Cloud** at `GC_GRAFANA_URL` (Explore, integrations, Kubernetes Monitoring, Fleet Management)
- Verify with `gcx metrics query` / `gcx logs query` — see [`_cloud/pov-index.yaml`](_cloud/pov-index.yaml)

## Scenarios

Browse scenarios by telemetry type.
Each row links to a directory with a README and all the configuration files required to deploy and run the scenario.

### Logs

These scenarios focus on log collection, log parsing, log routing, and log redaction.

| Scenario | Description |
| -------- | ----------- |
| [Amazon Data Firehose logs](aws-firehose-logs/) | **CPO stub.** POV: Observability → Cloud provider → AWS → Logs with Firehose. Alloy receiver lab is optional. |
| [Azure Event Hubs logs](azure-event-hubs-logs/) | **CPO stub.** POV: Observability → Cloud provider → Azure. Alloy Event Hubs consumer is a logs fallback, not Azure metrics. |
| [GELF log ingestion](gelf-log-ingestion/) | Ingest Graylog Extended Log Format logs over `UDP`. |
| [Kafka logs](kafka/) | Consume and process logs from Apache Kafka topics. |
| [Log API gateway](log-api-gateway/) | Use Alloy as a centralized log gateway that accepts logs via a Loki-compatible push API endpoint. |
| [Log routing](routing/) | Route logs from multiple sources to different Loki tenants based on log content and origin. |
| [Log secret filtering](log-secret-filtering/) | Redact sensitive credentials and secrets from logs with pattern rules before storage. |
| [Log-to-metrics](log-to-metrics/) | Extract a request counter and latency histogram from application logs while forwarding the raw logs to Loki. |
| [Logs from file](logs-file/) | Tail log files with Alloy. |
| [Logs over TCP](logs-tcp/) | Receive and process TCP logs in JSON format. |
| [Popular logging frameworks](app-instrumentation/logging/popular-logging-frameworks/) | Parse logs from popular logging frameworks across 7 programming languages. |
| [Promtail to Alloy migration](promtail-to-alloy-migration/) | Run Promtail (EOL March 2026) and its `alloy convert` equivalent side by side against one log file and verify identical results in Loki. |
| [Structured log parsing](mail-house/) | Parse structured logs into labels and structured metadata. |
| [Syslog monitoring](syslog/) | Monitor non-RFC5424 compliant syslog messages with `rsyslog` and Alloy. |
| [systemd journal](systemd-journal/) | Forward systemd journal entries to Loki with filters and labels tuned for fast queries. |
| [Windows security events](windows-events/) | Forward Windows Security event logs to Loki with filters and field extraction for security operations center workflows. |

### Tracing

These scenarios show distributed tracing with OpenTelemetry and Tempo.

| Scenario | Description |
| -------- | ----------- |
| [Distributed tracing](trace-delivery/) | Learn distributed tracing through a sofa delivery workflow from order to doorstep. |
| [Game of tracing](game-of-tracing/) | Play an interactive strategy game that teaches distributed tracing, sampling, and service graphs. |
| [OpenTelemetry basic tracing](otel-basic-tracing/) | Collect and visualize OpenTelemetry traces with Alloy and Tempo. |
| [OpenTelemetry SDK traces across languages](app-instrumentation/traces/opentelemetry-sdk/) | Instrument five languages with the OpenTelemetry tracing SDK and collect standalone traces through Alloy into Tempo. |
| [OpenTelemetry Jaeger and Zipkin receivers](otel-jaeger-zipkin-receiver/) | Ingest Jaeger and Zipkin trace formats with Alloy and forward them to Tempo over OTLP. |
| [Zero-code eBPF instrumentation](beyla-zero-code-instrumentation/) | Auto-instrument an unmodified Go HTTP service with `beyla.ebpf` -- no OpenTelemetry SDK, no agent, no code changes. Produces RED metrics and traces from eBPF probes alone. |
| [OpenTelemetry load balancing](otel-loadbalancing/) | Shard traces across two tail-sampling Alloy instances with `otelcol.exporter.loadbalancing` -- same trace ID, same backend. |
| [OpenTelemetry service graphs](otel-tracing-service-graphs/) | Generate service graphs with the Alloy `servicegraph` connector. |
| [OpenTelemetry span metrics](otel-span-metrics/) | Generate RED metrics from OpenTelemetry traces with the span metrics connector. Request rate, error rate, and duration. |
| [OpenTelemetry tail sampling](otel-tail-sampling/) | Apply tail sampling policies to OpenTelemetry traces with Alloy and Tempo. |
| [Trace correlation with exemplars](trace-log-correlation-exemplars/) | Jump from a latency histogram to the exact trace behind it with OpenMetrics exemplars flowing through Alloy into Prometheus and Tempo. |

### Metrics

These scenarios collect and forward metrics with Alloy.

| Scenario | Description |
| -------- | ----------- |
| [Alloy pipeline patterns](alloy-pipeline-patterns/) | Cookbook: create labels, `prometheus.relabel` keep/drop/labeldrop/replace, and `loki.process` parse/drop/static_labels/structured metadata. Collector-side shaping, not Adaptive Telemetry. |
| [Alloy clustering](alloy-clustering/) | Run a three-node Alloy cluster that consistent-hashes `prometheus.scrape` targets across nodes. Stop a node and its targets redistribute to the survivors within seconds. |
| [Blackbox probing](blackbox-probing/) | Monitor endpoint availability and response times with synthetic HTTP probes. |
| [Prometheus Operator Probes](k8s/prometheus-operator-probes/) | Scrape Prometheus Operator `Probe` resources with Alloy as the blackbox prober (`/probe` path). |
| [Metric cardinality control](metric-cardinality-control/) | Compare original Prometheus metrics with a cardinality-controlled `prometheus.relabel` path that drops noisy series and volatile labels and normalizes dynamic routes. |
| [OpenTelemetry SDK metrics across languages](app-instrumentation/metrics/opentelemetry-sdk/) | Instrument five languages with the OpenTelemetry metrics SDK and push them through Alloy to Prometheus. |
| [Prometheus client metrics across languages](app-instrumentation/metrics/prometheus-client/) | Expose `/metrics` with native Prometheus client libraries in five languages and scrape them with Alloy. The pull-model counterpart to the OpenTelemetry SDK scenario. |
| [OTel metrics pipeline](otel-metrics-pipeline/) | Forward OpenTelemetry metrics from applications through Alloy. Alloy batches and transforms samples before it sends them to Prometheus. |

### Profiling

These scenarios collect continuous profiles from applications.

| Scenario | Description |
| -------- | ----------- |
| [Continuous profiling](continuous-profiling/) | Collect and visualize CPU, memory, and goroutine profiles from Go applications with Grafana Pyroscope. |
| [eBPF host profiling](ebpf-host-profiling/) | Profile every process on a Linux host with `pyroscope.ebpf` -- no language agents, no application code changes. Uses Docker container discovery to attribute samples per workload. |
| [Java profiling](java-profiling/) | Attach async-profiler to a running JVM with `pyroscope.java` -- CPU and allocation flame graphs with no agent jar and no code changes. |

### Secrets and configuration

These scenarios load credentials and configuration from external stores.

| Scenario | Description |
| -------- | ----------- |
| [Vault secrets](vault-secrets/) | Pull `prometheus.remote_write` `basic_auth` credentials from HashiCorp Vault at runtime with `remote.vault`. Credentials reload on rotation. |

### Frontend

These scenarios collect telemetry from browser applications.

| Scenario | Description |
| -------- | ----------- |
| [Faro frontend observability](faro-frontend-observability/) | Collect frontend web telemetry, including logs, errors, and web vitals, from browser applications with the Faro Web SDK. |

### Cloud monitoring

These scenarios pull telemetry from cloud provider APIs.

| Scenario | Description |
| -------- | ----------- |
| [Amazon CloudWatch metrics](cloudwatch-metrics/) | **CPO stub.** POV: Observability → Cloud provider → AWS (scrape or metric streams). LocalStack/YACE lab is optional. |

### Infrastructure monitoring

POV for Linux / Windows / Docker / NGINX: `$GC_GRAFANA_URL/connections/add-new-connection`. Labs below match Cloud integration `job` labels.

These scenarios monitor hosts, containers, and network devices.

| Scenario | Description |
| -------- | ----------- |
| [Docker monitoring](docker-monitoring/) | Monitor Docker container metrics and logs. |
| [Linux monitoring](linux/) | Collect Linux system metrics, journal entries, and log files with Alloy. |
| [Windows monitoring](windows/) | Monitor Windows system metrics and Event Logs. |
| [NGINX monitoring](nginx-monitoring/) | Monitor NGINX access and error logs plus `stub_status` metrics with Alloy. |
| [Self-monitoring](self-monitoring/) | Configure Alloy to monitor itself and collect its own metrics and logs. |
| [SNMP monitoring](snmp/) | Monitor devices with the Alloy SNMP exporter for Simple Network Management Protocol. |
| [vCenter / vSphere](vcenter-monitoring/) | Collect vCenter metrics with `otelcol.receiver.vcenter` (`job=integrations/vsphere`) and optional VCSA syslog. Requires a real vCenter; no simulator. |

### Database and cache monitoring

POV: `$GC_GRAFANA_URL/connections/add-new-connection` (Cloud Integrations). Directories below are optional synthetic workloads with matching `job=integrations/...` labels.

These scenarios monitor databases and in-memory caches.

| Scenario | Description |
| -------- | ----------- |
| [Elasticsearch monitoring](elasticsearch-monitoring/) | Monitor Elasticsearch cluster health, node status, and performance metrics. |
| [Memcached monitoring](memcached-monitoring/) | Monitor Memcached instance metrics, including connections, memory usage, and command performance. |
| [Microsoft SQL Server monitoring](mssql-monitoring/) | Monitor SQL Server file sizes, batch requests, and connections with `prometheus.exporter.mssql`, plus app-specific metrics from a custom `query_config`. |
| [MongoDB monitoring](mongodb-monitoring/) | Monitor MongoDB op-counters, connection pool, and replica-set replication metrics with `prometheus.exporter.mongodb`. Runs a single-node replica set with an insert load generator. |
| [MySQL monitoring](mysql-monitoring/) | Monitor MySQL database server metrics and performance indicators. |
| [PostgreSQL monitoring](postgres-monitoring/) | Monitor PostgreSQL transaction statistics, connections, and server configuration. |
| [RabbitMQ monitoring](rabbitmq-monitoring/) | Monitor RabbitMQ queue, connection, and channel metrics plus broker container logs. |
| [Redis monitoring](redis-monitoring/) | Monitor Redis instance metrics, including connections, memory usage, and command throughput. |

### Kubernetes

**POV:** Instrumentation Hub + Kubernetes Monitoring (`$GC_GRAFANA_URL/a/grafana-k8s-app/configuration`). See [`k8s/README.md`](k8s/). Helm under `k8s/cloud-full` is GitOps fallback only.

The `k8s/` directory groups Helm-based and manifest-based examples for Alloy on Kubernetes.

| Scenario | Description |
| -------- | ----------- |
| [Kubernetes](k8s/) | Cloud-first stub: Instrumentation Hub, then GitOps Helm values that remote-write to Grafana Cloud. |

### Experimental OTel engine examples

Alloy v1.14 and later include an experimental **OTel Engine** that runs standard OpenTelemetry Collector YAML configurations directly.
These scenarios use OTel YAML syntax for teh OTel Engine and a minimal Alloy configuration to enable the Alloy UI.
Refer to the [OTel examples README](otel-examples/) for details.

| Scenario | Description |
| -------- | ----------- |
| [Cost control](otel-examples/cost-control/) | Drop health checks, filter debug logs, and apply probabilistic sampling to cut telemetry volume. |
| [Count connector](otel-examples/count-connector/) | Derive request rate and error rate metrics from traces and logs with the `count` connector. |
| [File log processing](otel-examples/filelog-processing/) | Collect and parse mixed-format log files with the OTel `filelog` receiver and operator chains. |
| [Host metrics](otel-examples/host-metrics/) | Collect CPU, memory, disk, and network metrics with the `hostmetrics` receiver. |
| [Kafka buffer](otel-examples/kafka-buffer/) | Buffer traces through Kafka for durability and `backpressure` control. |
| [Multi-pipeline fan-out](otel-examples/multi-pipeline-fanout/) | Send traces to two backends. Each destination runs its own process path. |
| [Multi-tenant routing](otel-examples/routing-multi-tenant/) | Route logs to different Loki tenants based on resource attributes with fan-out and filter. |
| [OTTL transform cookbook](otel-examples/ottl-transform/) | A cookbook of OpenTelemetry Transformation Language patterns for JSON parsing, severity mapping, attribute promotion, and truncation. |
| [PII redaction](otel-examples/pii-redaction/) | Scrub personally identifiable information, credit cards, emails, and IP addresses from traces and logs with OpenTelemetry Transformation Language `replace_pattern`. |
| [Resource enrichment](otel-examples/resource-enrichment/) | Attach host, OS, and Docker metadata to all signals with `resourcedetection`. |

## Contribute

Contributions of scenarios and improvements are welcome.
You can contribute in several ways.

### Suggest a scenario

Share an idea when you don't have time to implement a full scenario.

1. Open an [issue](https://github.com/grafana/alloy-scenarios/issues/new) on GitHub with the label `scenario-suggestion`
2. Describe the scenario and what it would show
3. Explain why this would be valuable to the community
4. Outline any special requirements or considerations

### Contribute a scenario

Add a complete scenario to the repository.

1. Fork this repository and create a branch
2. Create a directory in the root of this repository with a descriptive name for your scenario
3. Follow the scenario template section below
4. Submit a pull request with your scenario

### Improve a scenario

Update a scenario you want to change.

1. Fork this repository and create a branch
2. Make your improvements to the scenario
3. Submit a pull request with a clear description of your changes

### Scenario template

Include the following files when you create a scenario:

- `docker-compose.yml`: Docker Compose file with the observability backends and Alloy
- `docker-compose.coda.yml`: Docker Compose override with the demo app services for use with the `coda` CLI or `-f` flag
- `config.alloy`: Alloy configuration file for the scenario
- `README.md`: Documentation that explains the scenario
- Any additional files needed for your scenario, such as scripts or data files

### Scenario checklist

Confirm the following items before you submit your scenario:

- Create a directory in the root of this repository with a descriptive name
- Include a `docker-compose.yml` file with the necessary components, such as Loki, Grafana, Prometheus, or a subset
- Create a complete `config.alloy` file that shows the monitoring approach
- Write a `README.md` with:
  - A clear description of what the scenario shows
  - Prerequisites to run the demo
  - Step-by-step instructions to run the demo
  - Expected output and what to look for
  - Explanation of key configuration elements
- Add the scenario to the table in this `README.md`
- Ensure the scenario works with the centralized image management system
- Verify all components start correctly with `docker compose up -d`

### Best practices for scenarios

Follow these guidelines when you author or update a scenario:

- Keep the scenario focused on one concept
- Use clear, descriptive component and variable names
- Add comments to explain complex parts of your Alloy configuration
- Include a Customize section in your `README.md` with information about how readers might change the setup
- Provide sample queries for Grafana, Prometheus, Loki, or Tempo that work with your scenario
- Use environment variables for versions and configurable parameters

## Get help

If you have questions about a scenario or Alloy configuration, use these resources:

- Join the [Grafana Labs Community Forums](https://community.grafana.com/)
- Read the [Grafana Alloy documentation](https://grafana.com/docs/alloy/)

## License

This repository is licensed under the Apache License, Version 2.0.
Refer to [LICENSE](LICENSE) for the full license text.
