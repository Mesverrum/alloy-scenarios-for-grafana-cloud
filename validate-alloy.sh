#!/usr/bin/env bash
# Syntax-check Alloy configs with grafana/alloy (Docker in Linux/WSL).
# Does not need Postgres, Grafana Cloud credentials, or a running stack.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

IMAGE="grafana/alloy:${GRAFANA_ALLOY_VERSION:-v1.17.1}"
if [ -f image-versions.env ]; then
	ver="$(grep -E '^GRAFANA_ALLOY_VERSION=' image-versions.env | tr -d '\r' | cut -d= -f2-)"
	if [ -n "$ver" ]; then
		IMAGE="grafana/alloy:${ver}"
	fi
fi

FILES=(
	_cloud/destinations.alloy
	postgres-monitoring/config.alloy
	mysql-monitoring/config.alloy
	redis-monitoring/config.alloy
	memcached-monitoring/config.alloy
	mongodb-monitoring/config.alloy
	elasticsearch-monitoring/config.alloy
	mssql-monitoring/config.alloy
	blackbox-probing/config.alloy
	self-monitoring/config.alloy
	nginx-monitoring/config.alloy
	rabbitmq-monitoring/config.alloy
	snmp/config.alloy
	docker-monitoring/config.alloy
	vcenter-monitoring/config.alloy
	alloy-pipeline-patterns/config.alloy
)

if [ $# -gt 0 ]; then
	FILES=("$@")
fi

echo "Using $IMAGE"
fail=0

for f in "${FILES[@]}"; do
	echo "=== fmt $f ==="
	if docker run --rm -v "$ROOT:/src:ro" "$IMAGE" fmt "/src/$f" >/dev/null; then
		echo OK
	else
		echo FAIL
		fail=1
	fi
done

# Load-check: evaluate imports + sys.env with dummy Cloud credentials.
# Exporter targets may be unreachable; success means the config graph built.
echo "=== load converted scenario configs ==="
LOAD_FILES=(
	postgres-monitoring/config.alloy
	mysql-monitoring/config.alloy
	redis-monitoring/config.alloy
	memcached-monitoring/config.alloy
	mongodb-monitoring/config.alloy
	elasticsearch-monitoring/config.alloy
	mssql-monitoring/config.alloy
	blackbox-probing/config.alloy
	self-monitoring/config.alloy
	nginx-monitoring/config.alloy
	rabbitmq-monitoring/config.alloy
	snmp/config.alloy
	docker-monitoring/config.alloy
	vcenter-monitoring/config.alloy
	alloy-pipeline-patterns/config.alloy
)
if [ $# -gt 0 ]; then
	LOAD_FILES=()
	for f in "$@"; do
		if [ "$f" != "_cloud/destinations.alloy" ]; then
			LOAD_FILES+=("$f")
		fi
	done
fi
for cfg in "${LOAD_FILES[@]}"; do
	echo "--- $cfg ---"
	cid="$(docker run -d --rm \
		-e GC_DESTINATIONS_FILE=/src/_cloud/destinations.alloy \
		-e GC_PROM_URL=https://prometheus.example.invalid/api/prom/push \
		-e GC_PROM_USER=0 \
		-e GC_LOKI_URL=https://logs.example.invalid/loki/api/v1/push \
		-e GC_LOKI_USER=0 \
		-e GC_TOKEN=syntax-check-only \
		-e VCENTER_ENDPOINT=https://vcenter.example.invalid \
		-e VCENTER_USERNAME=readonly \
		-e VCENTER_PASSWORD=syntax-check-only \
		-e MSSQL_CONNECTION_STRING='sqlserver://sa:x@localhost:1433' \
		-v "$ROOT:/src:ro" \
		-v "$ROOT/mssql-monitoring/mssql-queries.yaml:/etc/alloy/mssql-queries.yaml:ro" \
		-v "$ROOT/snmp/snmp.yml:/etc/alloy/snmp.yml:ro" \
		-v /var/run/docker.sock:/var/run/docker.sock \
		"$IMAGE" \
		run --server.http.listen-addr=127.0.0.1:12345 --storage.path=/tmp/alloy --stability.level=experimental "/src/$cfg")"
	sleep 8
	logs="$(docker logs "$cid" 2>&1 || true)"
	docker rm -f "$cid" >/dev/null 2>&1 || true
	if echo "$logs" | grep -qE "now listening for http traffic|HTTP server listening|finished node evaluation"; then
		echo OK
	else
		echo FAIL
		echo "$logs" | tail -n 80
		fail=1
	fi
done

exit "$fail"
