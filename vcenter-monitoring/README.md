---
os: [linux, windows]
signals: [metrics, logs]
deploy: compose
cloud_products: [integrations]
---

# vCenter / vSphere monitoring

**POV path:** Connections → Install **vSphere** dashboards. Then Fleet Management → vSphere **template** if the picker has it; otherwise paste [`pipeline.alloy`](pipeline.alloy) onto a Linux jump-host collector (`role=vsphere`). Local Alloy is `remotecfg` only. Do not install Alloy on the VCSA.

Compose in this directory is SE practice against a **real** vCenter (no simulator). Do not enroll that container in Fleet.

There is **no vCenter simulator**. Point `VCENTER_*` at a lab or customer vCenter (7.0.2+ / ESXi 6.7 U2+). Docker Compose runs Alloy in WSL or Linux; Alloy does not install on the vCenter appliance.

`prometheus.exporter.vsphere` is deprecated. Do not use it.

## Before you begin

- Repo-root `.env` from `.env.sample` with Grafana Cloud credentials **and**:

  ```text
  VCENTER_ENDPOINT=https://vcenter.lab.example
  VCENTER_USERNAME=readonly@vsphere.local
  VCENTER_PASSWORD=...
  ```

- A **Read Only** vSphere user with rights on the vCenter, cluster, and every object you want on the dashboard
- vCenter **Statistics Collection Level ≥ 2** (otherwise many performance counters are missing)
- Ports **12345** (Alloy UI) and **1514** (optional syslog) free on the host
- From WSL Docker, a network route to vCenter (VPN/DNS). Add `extra_hosts` in `docker-compose.yml` if the FQDN only resolves on the host

## Architecture

```text
+-----------+  SDK/HTTPS   +-------+  remote write   +----------------+
| vCenter   |------------->| Alloy |---------------->| Grafana Cloud  |
| (real)    |  syslog:1514 |       |  Loki push      | Metrics + Logs |
+-----------+              +-------+                 +----------------+
```

- **Alloy**: `otelcol.receiver.vcenter` (experimental; Compose sets `--stability.level=experimental`)
- **Metrics**: OTLP → batch → transform (`job=integrations/vsphere`) → `otelcol.exporter.prometheus` with `resource_to_telemetry_conversion` so datacenter/cluster/host/VM names become Prometheus labels
- **Logs** (optional): vCenter remote syslog → `loki.source.syslog` on TCP/UDP 1514 → keep vpxd / applmgmt / analytics → Cloud

## Run the scenario

Fill `VCENTER_*` in `.env`, then from the repository root:

**Windows (PowerShell, forwards to WSL Docker)**

```powershell
.\run-example.ps1 vcenter-monitoring
```

**WSL / Linux (bash)**

```bash
./run-example.sh vcenter-monitoring
```

Or from this directory: `docker compose --env-file ../image-versions.env --env-file ../.env up -d`

Expect only `alloy` (no local Prometheus or Grafana). First metrics appear after ~1m.

## Explore

- **Alloy UI**: http://localhost:12345 — component graph and live debugging
- **Cloud Grafana**: `$GC_GRAFANA_URL` → Connections → vSphere dashboards (overview, clusters, hosts, VMs, logs)

### Verify with gcx

```text
gcx metrics query '{job="integrations/vsphere"}'
gcx metrics query 'vcenter_cluster_cpu_effective{job="integrations/vsphere"}'
gcx logs query '{job="integrations/vsphere"}'
```

Expect cluster/host/VM series after the first collection. Logs stay empty until vCenter forwards syslog to this host on port 1514.

### PromQL

- `vcenter_cluster_cpu_effective{job="integrations/vsphere"}`
- `vcenter_host_cpu_utilization_percent{job="integrations/vsphere"}`
- `vcenter_vm_cpu_utilization_percent{job="integrations/vsphere"}`
- `vcenter_datastore_disk_utilization_percent{job="integrations/vsphere"}`

## TLS

This lab sets `insecure_skip_verify = true` (HTTPS, ignore appliance cert). The Cloud wizard snippet often sets `insecure = true`, which **turns TLS off** — only use that for `http://`. Production: `ca_file` / `ca_pem` for the vCenter CA.

## Cost / cardinality

Keep **1m**. VM metrics scale with every VM × disk × NIC. To cut DPM, disable `vcenter.vm.*` in the receiver `metrics { }` block or `prometheus.relabel` drop `{__name__=~"vcenter_vm_.*"}` before remote write. vSAN counters are on by default; disable them if the cluster has no vSAN.

## Troubleshoot

- Alloy exits immediately: `VCENTER_ENDPOINT` / user / password missing from `.env`
- Component unhealthy, TLS errors: try skip-verify vs a real CA; confirm the endpoint is `https://host` (no `/sdk` required)
- Empty dashboards, receiver healthy: Statistics Level below 2, or the user cannot see the cluster
- Unreachable from Docker: from WSL, `curl -k "$VCENTER_ENDPOINT"`; add `extra_hosts` or a VPN route into the WSL VM
- Syslog not parsing: vCenter may not send RFC5424 — put [`syslog/`](../syslog/) rsyslog in front, or disable `use_rfc5424_message`

## Stop

```text
docker compose down
```

## Customer handoff

Fleet template if listed, else paste [`pipeline.alloy`](pipeline.alloy) onto a Linux jump-host collector. Local file is [`_cloud/remotecfg.alloy`](../_cloud/remotecfg.alloy). Env: `VCENTER_*`. Do not paste `destinations.alloy` into Fleet. Do not put Alloy on the VCSA.

## Next steps

- Alloy `otelcol.receiver.vcenter`: https://grafana.com/docs/alloy/latest/reference/components/otelcol/otelcol.receiver.vcenter/
- Grafana Cloud vSphere integration: https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-vsphere/
