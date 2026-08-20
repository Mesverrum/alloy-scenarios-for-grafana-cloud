---
os: [linux]
signals: [metrics, logs, traces, profiles]
deploy: wizard
cloud_products: [instrumentation-hub, kubernetes-monitoring, fleet]
---

# Kubernetes observability (Grafana Cloud)

**POV path:** do not deploy Alloy, Prometheus, Loki, Tempo, or Grafana into the cluster by hand.

1. Open the customer stack (`GC_GRAFANA_URL`).
2. **Instrumentation Hub** (Linux Kubernetes) — [setup docs](https://grafana.com/docs/grafana-cloud/learn-and-build/get-started/set-up-your-account/inst-hub-setup/). Paste the Helm command it prints. That installs Alloy, can enable Beyla, and activates Kubernetes Monitoring.
3. Confirm in **Fleet Management** and **Kubernetes Monitoring**: `$GC_GRAFANA_URL/a/grafana-k8s-app` and `$GC_GRAFANA_URL/a/grafana-k8s-app/configuration`.

Windows nodes are **not** Instrumentation Hub today. Use native Alloy + Fleet Management (`gcx fleet`).

```text
gcx login --server "$GC_GRAFANA_URL"
gcx fleet collectors list
```

## GitOps fallback

Only if the customer cannot use Instrumentation Hub (air-gapped GitOps, existing Helm, etc.):

1. `kubectl create namespace meta`
2. `kubectl create secret generic grafana-cloud --from-env-file=../.env -n meta`
3. Install `grafana/k8s-monitoring` **^4** with [`cloud-full/k8s-monitoring-values.yml`](cloud-full/k8s-monitoring-values.yml) (metrics + logs + traces + profiles to Grafana Cloud).

Per-signal values (same Cloud destinations, same Secret) if you need a thinner chart:

| Folder | Signal | Chart values |
| ------ | ------ | ------------ |
| [cloud-full](cloud-full/) | All | Combined |
| [metrics](metrics/) | Cluster + annotated Pods | `k8s-monitoring-values.yml` |
| [logs](logs/) | Pod logs + events | `k8s-monitoring-values.yml` |
| [tracing](tracing/) | OTLP receiver | `k8s-monitoring-values.yml` |
| [profiling](profiling/) | pprof | `k8s-monitoring-values.yml` |
| [events](events/) | Events via `loki.source.kubernetes_events` | Manifests + Cloud Loki |
| [kube-state-metrics-cadvisor](kube-state-metrics-cadvisor/) | Raw Alloy pipeline | `grafana/alloy` chart |
| [prometheus-operator-probes](prometheus-operator-probes/) | Probe CRs | `grafana/alloy` chart |

Do **not** Helm-install the `prometheus-values.yml`, `loki-values.yml`, `tempo-values.yml`, `pyroscope-values.yml`, or `grafana-values.yml` files in those folders. They are leftover OSS backends.

See [`_cloud/curated-paths.md`](../_cloud/curated-paths.md).
