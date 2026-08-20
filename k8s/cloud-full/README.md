---
os: [linux]
signals: [metrics, logs, traces, profiles]
deploy: helm
cloud_products: [kubernetes-monitoring]
---

# Kubernetes Monitoring Helm (GitOps fallback)

Use **Instrumentation Hub** first ([`../README.md`](../README.md)). This folder is the copy-paste Helm values when the customer wants GitOps.

```sh
# from repo root, with .env filled in
kubectl create namespace meta
kubectl create secret generic grafana-cloud --from-env-file=.env -n meta

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm upgrade --install k8s grafana/k8s-monitoring --version "^4.0.0" \
  -n meta -f k8s/cloud-full/k8s-monitoring-values.yml
```

The Secret must contain `GC_PROM_URL`, `GC_PROM_USER`, `GC_LOKI_URL`, `GC_LOKI_USER`, `GC_OTLP_URL`, `GC_OTLP_USER`, `GC_PYRO_URL`, `GC_PYRO_USER`, and `GC_TOKEN` (same keys as [`.env.sample`](../../.env.sample)).

Verify in Cloud Grafana: `$GC_GRAFANA_URL/a/grafana-k8s-app`
