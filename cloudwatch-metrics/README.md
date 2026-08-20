---
os: [any]
signals: [metrics]
deploy: wizard
cloud_products: [cloud-provider-observability]
---

# Amazon CloudWatch metrics — Grafana Cloud path

**POV path:** do not run Alloy or LocalStack to demo AWS.

1. Open `$GC_GRAFANA_URL`
2. **Observability → Cloud provider → AWS**
3. Add the account (IAM role delegation; no long-lived keys)
4. Create a **CloudWatch metrics scrape** job, or **metric streams** (Firehose → Grafana Cloud ingest)

Docs: [AWS observability](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/monitor-cloud-provider/aws/) · [How CloudWatch collection works](https://grafana.com/docs/grafana-cloud/observe-and-act/monitor-infrastructure/monitor-cloud-provider/aws/cloudwatch-metrics/about-cloudwatch-metrics/)

That is Cloud Provider Observability: hosted scrape or Firehose streams, resource tags, curated AWS views. Grafana Cloud does **not** need Alloy for this.

## Collector lab (not the POV)

`config.alloy` in this directory wraps YACE (`prometheus.exporter.cloudwatch`) against LocalStack. Keep it for:

- a customer who already runs Alloy/YACE and is migrating to Cloud
- showing the exporter component, offline

Do **not** point this lab at a real AWS account that is already in CPO (duplicate series and CloudWatch API cost).

See [`_cloud/curated-paths.md`](../_cloud/curated-paths.md).
