#!/usr/bin/env python3
"""Rewire remaining Alloy scenarios to Grafana Cloud destinations.

Run from the repo root (WSL/Linux): python3 _cloud/convert_to_cloud.py
Idempotent enough to skip files that already import grafana_cloud.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    "_cloud",
    "img",
    ".git",
    ".cursor",
    ".github",
    ".claude",
}

# Already converted by hand (or k8s/helm handled separately).
ALREADY = {
    "postgres-monitoring",
    "mysql-monitoring",
    "redis-monitoring",
    "memcached-monitoring",
    "mongodb-monitoring",
    "elasticsearch-monitoring",
    "mssql-monitoring",
    "blackbox-probing",
    "self-monitoring",
    "nginx-monitoring",
    "rabbitmq-monitoring",
    "snmp",
    "docker-monitoring",
}

BACKEND_SERVICES = {
    "loki",
    "prometheus",
    "grafana",
    "tempo",
    "tempo-init",
    "memcached",
    "pyroscope",
}

WRITE_COMPONENTS = (
    "loki.write",
    "prometheus.remote_write",
    "pyroscope.write",
    "otelcol.exporter.otlp",
    "otelcol.exporter.otlphttp",
)

RECEIVER_REPLACEMENTS = [
    (r"loki\.write\.[A-Za-z0-9_]+\.receiver", "grafana_cloud.logs.default.receiver"),
    (r"prometheus\.remote_write\.[A-Za-z0-9_]+\.receiver", "grafana_cloud.metrics.default.receiver"),
    (r"pyroscope\.write\.[A-Za-z0-9_]+\.receiver", "grafana_cloud.profiles.default.receiver"),
    (r"otelcol\.exporter\.otlp(?:http)?\.[A-Za-z0-9_]+\.input", "grafana_cloud.otlp.default.input"),
]


def strip_component_blocks(src: str, component_type: str) -> str:
    out = []
    i = 0
    pattern = re.compile(rf"(?m)^[ \t]*{re.escape(component_type)}\s+\"[^\"]+\"\s*\{{")
    while i < len(src):
        m = pattern.search(src, i)
        if not m:
            out.append(src[i:])
            break
        out.append(src[i : m.start()])
        brace = src.find("{", m.start())
        depth = 0
        j = brace
        while j < len(src):
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        # drop trailing whitespace/newlines after the block (keep one newline)
        while j < len(src) and src[j] in " \t":
            j += 1
        if j < len(src) and src[j] == "\n":
            j += 1
        i = j
    return "".join(out)


def ensure_header(src: str) -> str:
    if 'import.file "grafana_cloud"' in src:
        return src
    needs_metrics = "grafana_cloud.metrics.default.receiver" in src or "prometheus.scrape" in src or "prometheus.exporter" in src
    needs_logs = "grafana_cloud.logs.default.receiver" in src or "loki.source" in src or "loki.process" in src
    needs_otlp = "grafana_cloud.otlp.default.input" in src or "otelcol.receiver" in src
    needs_profiles = "grafana_cloud.profiles.default.receiver" in src or "pyroscope.scrape" in src or "pyroscope.ebpf" in src or "pyroscope.java" in src

    # After replacement, detect from remaining references
    needs_metrics = needs_metrics or "grafana_cloud.metrics.default.receiver" in src
    needs_logs = needs_logs or "grafana_cloud.logs.default.receiver" in src
    needs_otlp = needs_otlp or "grafana_cloud.otlp.default.input" in src
    needs_profiles = needs_profiles or "grafana_cloud.profiles.default.receiver" in src

    lines = [
        'import.file "grafana_cloud" {',
        "	filename = sys.env(\"GC_DESTINATIONS_FILE\")",
        "}",
        "",
    ]
    if needs_metrics:
        lines.append('grafana_cloud.metrics "default" {}')
    if needs_logs:
        lines.append('grafana_cloud.logs "default" {}')
    if needs_otlp:
        lines.append('grafana_cloud.otlp "default" {}')
    if needs_profiles:
        lines.append('grafana_cloud.profiles "default" {}')
    if needs_metrics or needs_logs or needs_otlp or needs_profiles:
        lines.append("")
    return "\n".join(lines) + src.lstrip("\n")


def convert_alloy(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    if 'import.file "grafana_cloud"' in src:
        return False
    original = src
    for comp in WRITE_COMPONENTS:
        src = strip_component_blocks(src, comp)
    for pat, repl in RECEIVER_REPLACEMENTS:
        src = re.sub(pat, repl, src)
    src = re.sub(r'scrape_interval\s*=\s*"(10s|15s|30s)"', 'scrape_interval = "1m"', src)
    src = ensure_header(src)
    if src != original:
        path.write_text(src, encoding="utf-8", newline="\n")
        return True
    return False


def strip_compose_backends(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if m and m.group(1) in BACKEND_SERVICES:
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if re.match(r"^  [A-Za-z0-9_-]+:\s*$", nxt) or re.match(r"^[A-Za-z]", nxt):
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    text = "".join(out)
    # Drop depends_on entries for backends (simple line removals)
    cleaned = []
    for line in text.splitlines(keepends=True):
        if re.search(r"\b(loki|prometheus|grafana|tempo|tempo-init|memcached|pyroscope)\b", line):
            stripped = line.strip()
            if stripped.startswith("-") or stripped.endswith(":") or "condition:" in stripped:
                # keep workload lines that merely mention those words in comments? skip backend depends
                if any(x in stripped for x in ("loki", "prometheus", "grafana", "tempo", "memcached", "pyroscope")):
                    if "image:" not in stripped and "container_name:" not in stripped:
                        continue
        cleaned.append(line)
    return "".join(cleaned)


ALLOY_INJECT = """    env_file:
      - ../.env
    environment:
      GC_DESTINATIONS_FILE: /etc/alloy/cloud/destinations.alloy
"""

DEST_VOLUME = "      - ../_cloud/destinations.alloy:/etc/alloy/cloud/destinations.alloy\n"


def inject_alloy_cloud(text: str) -> str:
    if "GC_DESTINATIONS_FILE" in text:
        return text
    lines = text.splitlines(keepends=True)
    out = []
    in_alloy = False
    alloy_indent = "  "
    injected_env = False
    injected_vol = False
    for i, line in enumerate(lines):
        if re.match(r"^  alloy(-[a-z0-9]+)?\s*:\s*$", line):
            in_alloy = True
            injected_env = False
            injected_vol = False
            out.append(line)
            continue
        if in_alloy and re.match(r"^  [A-Za-z0-9_-]+\s*:\s*$", line):
            in_alloy = False
        if in_alloy and (not injected_env) and re.match(r"^    image:", line):
            out.append(line)
            # inject after image line if env_file missing
            if "env_file:" not in "".join(lines[max(0, i - 5) : i + 25]):
                out.append(ALLOY_INJECT)
                injected_env = True
            continue
        if in_alloy and re.match(r"^    volumes:\s*$", line):
            out.append(line)
            if DEST_VOLUME not in text:
                out.append(DEST_VOLUME)
                injected_vol = True
            continue
        out.append(line)
    text = "".join(out)
    if "GC_DESTINATIONS_FILE" not in text:
        # fallback: append under every alloy image
        text = re.sub(
            r"(^  alloy(?:-[a-z0-9]+)?:\n(?:.*\n)*?    image:.*\n)",
            r"\1" + ALLOY_INJECT,
            text,
            count=1,
            flags=re.M,
        )
    if "../_cloud/destinations.alloy" not in text:
        text = re.sub(
            r"(    volumes:\n)",
            r"\1" + DEST_VOLUME,
            text,
            count=1,
        )
    return text


def convert_compose(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    original = src
    src = strip_compose_backends(src)
    src = inject_alloy_cloud(src)
    # collapse extra blank lines
    src = re.sub(r"\n{3,}", "\n\n", src)
    if src != original:
        path.write_text(src, encoding="utf-8", newline="\n")
        return True
    return False


def convert_otel_yaml(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    if "GC_OTLP_URL" in src or "grafana_cloud" in src:
        return False
    original = src
    src = src.replace("endpoint: tempo:4317", "endpoint: ${env:GC_OTLP_URL}")
    src = src.replace("endpoint: http://loki:3100/otlp", "endpoint: ${env:GC_OTLP_URL}")
    src = src.replace("endpoint: http://prometheus:9090/api/v1/otlp", "endpoint: ${env:GC_OTLP_URL}")
    src = src.replace("insecure: true", "insecure: false")
    if src != original:
        # prepend auth extension note as comments; env on exporter is enough for syntax
        path.write_text(src, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    alloy_changed = []
    compose_changed = []
    otel_changed = []
    for path in ROOT.rglob("config.alloy"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or rel.parts[0] == "k8s":
            continue
        if rel.parts[0] in ALREADY:
            continue
        if convert_alloy(path):
            alloy_changed.append(str(rel))
    for name in ("docker-compose.yml", "docker-compose.yaml", "docker-compose-otel.yml"):
        for path in ROOT.rglob(name):
            rel = path.relative_to(ROOT)
            if rel.parts[0] in SKIP_DIRS or rel.parts[0] == "k8s":
                continue
            if rel.parts[0] in ALREADY:
                continue
            if convert_compose(path):
                compose_changed.append(str(rel))
    for path in ROOT.rglob("config-otel.yaml"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        if convert_otel_yaml(path):
            otel_changed.append(str(rel))
    print(f"alloy {len(alloy_changed)}")
    for x in alloy_changed:
        print("  ", x)
    print(f"compose {len(compose_changed)}")
    for x in compose_changed:
        print("  ", x)
    print(f"otel-yaml {len(otel_changed)}")
    for x in otel_changed:
        print("  ", x)


if __name__ == "__main__":
    main()
