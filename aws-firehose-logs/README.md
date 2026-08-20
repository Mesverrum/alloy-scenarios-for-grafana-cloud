---
os: [any]
signals: [logs]
deploy: wizard
cloud_products: [cloud-provider-observability]
---

# Amazon Data Firehose logs — Grafana Cloud path

**POV path:** Firehose delivers **to Grafana Cloud**, not to Alloy.

1. Open `$GC_GRAFANA_URL`
2. **Observability → Cloud provider → AWS**
3. Configure **Logs with Firehose** (or Logs with Lambda for smaller volume)

Docs: [AWS observability](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/monitor-cloud-provider/aws/)

CPO Firehose uses Grafana Cloud’s hosted Loki ingest URL. Standing up `loki.source.awsfirehose` is a different architecture (Alloy as the HTTP destination).

## Collector lab (not the POV)

`config.alloy` listens for Firehose-shaped POSTs and a Python container fakes the producer. No AWS account. Useful for teaching the component or a private-network hop that CPO cannot reach.

Do not dual-run this against log groups already streaming into CPO.

See [`_cloud/curated-paths.md`](../_cloud/curated-paths.md).
