#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <example-directory>"
    echo "Available examples:"
    ls -d */ | grep -v "k8s\|img\|.git\|_cloud" | tr -d '/'
    exit 1
fi

EXAMPLE_DIR=$1

if [ ! -d "$EXAMPLE_DIR" ]; then
    echo "Error: Example directory '$EXAMPLE_DIR' not found."
    exit 1
fi

if [ ! -f "$EXAMPLE_DIR/docker-compose.yml" ] && [ ! -f "$EXAMPLE_DIR/docker-compose.yaml" ]; then
    echo "Error: No docker-compose.yml or docker-compose.yaml found in '$EXAMPLE_DIR'."
    exit 1
fi

if [ ! -f "image-versions.env" ]; then
    echo "Error: image-versions.env file not found."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "Error: .env is missing. Copy .env.sample to .env and fill in Grafana Cloud credentials:"
    echo "  cp .env.sample .env"
    exit 1
fi

echo "Starting example: $EXAMPLE_DIR"
(cd "$EXAMPLE_DIR" && docker compose --env-file ../image-versions.env --env-file ../.env up -d)

GRAFANA_URL="$(grep -E '^GC_GRAFANA_URL=' .env | cut -d= -f2- || true)"

echo "Example started successfully."
echo "Alloy UI: http://localhost:12345"
if [ -n "$GRAFANA_URL" ]; then
    echo "Cloud Grafana: $GRAFANA_URL"
fi
echo "Verify ingest with gcx (see _cloud/pov-index.yaml)."
echo "To stop the example, run: cd $EXAMPLE_DIR && docker compose down"
