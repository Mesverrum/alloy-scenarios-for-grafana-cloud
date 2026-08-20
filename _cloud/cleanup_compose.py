#!/usr/bin/env python3
"""Remove empty depends_on: keys left after stripping LGTM services."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def remove_empty_depends_on(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)depends_on:\s*$", lines[i])
        if m:
            indent = len(m.group(1))
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j >= len(lines):
                i += 1
                continue
            next_indent = len(lines[j]) - len(lines[j].lstrip(" "))
            if next_indent <= indent:
                i += 1
                continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def main() -> None:
    n = 0
    for path in list(ROOT.rglob("docker-compose.yml")) + list(ROOT.rglob("docker-compose.yaml")) + list(
        ROOT.rglob("docker-compose-otel.yml")
    ):
        src = path.read_text(encoding="utf-8")
        dst = remove_empty_depends_on(src)
        dst = re.sub(r"\n{3,}", "\n\n", dst)
        if dst != src:
            path.write_text(dst, encoding="utf-8", newline="\n")
            n += 1
            print(path.relative_to(ROOT))
    print(f"updated {n}")


if __name__ == "__main__":
    main()
