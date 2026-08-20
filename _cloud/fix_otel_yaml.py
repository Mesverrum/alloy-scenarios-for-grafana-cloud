#!/usr/bin/env python3
"""Rewrite OTel Collector YAML exporters to Grafana Cloud OTLP HTTP + basic auth."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLOUD_EXPORTER = """  otlphttp/grafana_cloud:
    endpoint: ${env:GC_OTLP_URL}
    auth:
      authenticator: basicauth/grafana_cloud
    tls:
      insecure: false
"""

BASICAUTH = """  basicauth/grafana_cloud:
    client_auth:
      username: ${env:GC_OTLP_USER}
      password: ${env:GC_TOKEN}
"""

REWRITE_NAMES = {
    "otlp/tempo": "otlphttp/grafana_cloud",
    "otlp/tempo-primary": "otlphttp/grafana_cloud",
    "otlphttp/loki": "otlphttp/grafana_cloud",
    "otlphttp/prometheus": "otlphttp/grafana_cloud",
    "otlphttp/loki-team-a": "otlphttp/grafana_cloud",
    "otlphttp/loki-team-b": "otlphttp/grafana_cloud",
    "otlp/tempo-secondary": "debug",
}

KEEP_EXPORTERS = {"kafka", "debug"}


def split_top_keys(body: str, indent: int = 2) -> dict[str, str]:
    """Split a YAML mapping body into key -> block (including nested lines)."""
    lines = body.splitlines(keepends=True)
    blocks: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    key_re = re.compile(rf"^[ ]{{{indent}}}([^\s:#][^:]*):")
    for line in lines:
        m = key_re.match(line)
        if m:
            if current is not None:
                blocks[current] = "".join(buf)
            current = m.group(1)
            buf = [line]
        elif current is not None:
            buf.append(line)
    if current is not None:
        blocks[current] = "".join(buf)
    return blocks


def ensure_basicauth(text: str) -> str:
    if "basicauth/grafana_cloud:" in text:
        return text
    if re.search(r"^extensions:\s*$", text, re.M):
        return re.sub(
            r"^extensions:\s*$",
            "extensions:\n" + BASICAUTH.rstrip("\n"),
            text,
            count=1,
            flags=re.M,
        )
    if "extensions:" in text:
        return re.sub(
            r"(^extensions:\n)",
            r"\1" + BASICAUTH,
            text,
            count=1,
            flags=re.M,
        )
    # Insert extensions before service:
    return re.sub(
        r"^service:",
        "extensions:\n" + BASICAUTH + "\nservice:",
        text,
        count=1,
        flags=re.M,
    )


def ensure_service_extension(text: str) -> str:
    m = re.search(r"^(\s*)extensions:\s*\[([^\]]*)\]", text, re.M)
    if m:
        items = [x.strip() for x in m.group(2).split(",") if x.strip()]
        if "basicauth/grafana_cloud" not in items:
            items.append("basicauth/grafana_cloud")
        return text[: m.start()] + f"{m.group(1)}extensions: [{', '.join(items)}]" + text[m.end() :]
    # Add under service:
    return re.sub(
        r"^service:\n",
        "service:\n  extensions: [basicauth/grafana_cloud]\n",
        text,
        count=1,
        flags=re.M,
    )


def transform(text: str) -> str:
    m = re.search(r"^exporters:\n", text, re.M)
    if not m:
        return text
    start = m.end()
    rest = text[start:]
    next_m = re.search(r"^(service|receivers|processors|connectors|extensions):", rest, re.M)
    if not next_m:
        exp_body = rest
        after = ""
    else:
        exp_body = rest[: next_m.start()]
        after = rest[next_m.start() :]

    blocks = split_top_keys(exp_body)
    if not blocks:
        return text

    kept: list[str] = []
    need_cloud = False
    for name, block in blocks.items():
        if name in KEEP_EXPORTERS or name.startswith("debug"):
            kept.append(block.rstrip() + "\n")
            continue
        if name in REWRITE_NAMES or "GC_OTLP_URL" in block or "otlp-gateway" in block:
            need_cloud = True
            dest = REWRITE_NAMES.get(name, "otlphttp/grafana_cloud")
            if dest == "debug" and "debug:" not in "".join(kept) and "debug" not in blocks:
                kept.append("  debug:\n    verbosity: basic\n")
            continue
        # local leftover backends
        if re.search(r"endpoint:\s*(tempo|loki|prometheus|pyroscope)", block):
            need_cloud = True
            continue
        kept.append(block.rstrip() + "\n")

    if need_cloud:
        kept.insert(0, CLOUD_EXPORTER)

    new_exporters = "exporters:\n" + "".join(kept)
    if not new_exporters.endswith("\n"):
        new_exporters += "\n"
    text = text[: m.start()] + new_exporters + "\n" + after

    for old, new in REWRITE_NAMES.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)

    # Collapse duplicate exporter names in pipeline lists
    def dedupe_list(match: re.Match[str]) -> str:
        items = [x.strip() for x in match.group(1).split(",")]
        seen: list[str] = []
        for item in items:
            if item not in seen:
                seen.append(item)
        return "exporters: [" + ", ".join(seen) + "]"

    text = re.sub(r"exporters:\s*\[([^\]]+)\]", dedupe_list, text)
    text = ensure_basicauth(text)
    text = ensure_service_extension(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main() -> None:
    n = 0
    for path in sorted(ROOT.rglob("config-otel.yaml")):
        src = path.read_text(encoding="utf-8")
        dst = transform(src)
        if dst != src:
            path.write_text(dst, encoding="utf-8", newline="\n")
            n += 1
            print(path.relative_to(ROOT))
    print(f"updated {n}")


if __name__ == "__main__":
    main()
