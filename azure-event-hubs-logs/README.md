---
os: [any]
signals: [logs]
deploy: wizard
cloud_products: [cloud-provider-observability]
---

# Azure Event Hubs logs — Grafana Cloud path

**POV path for Azure infrastructure:** Cloud Provider Observability, not this Alloy consumer.

1. Open `$GC_GRAFANA_URL`
2. **Observability → Cloud provider → Azure**
3. Connect a service principal for **Azure Monitor metrics** (serverless pull, no collector)
4. For logs: CPO **Azure Function** (`azure_eventhub_to_loki`) is the hosted path. Alloy’s Event Hubs source is documented as an alternative if they already run Alloy.

Docs: [Cloud Provider Observability](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/monitor-cloud-provider/) · [Azure logs with Alloy](https://grafana.com/docs/grafana-cloud/observe-and-act/monitor-infrastructure/monitor-cloud-provider/azure/config-azure-logs-alloy/) (fallback)

## Collector lab (not the Azure metrics POV)

`config.alloy` uses `loki.source.azure_event_hubs` against a local Kafka-compatible broker and fake Activity Log records. No Azure subscription. Use it to show the Alloy component, not to replace CPO Azure metrics.

See [`_cloud/curated-paths.md`](../_cloud/curated-paths.md).
