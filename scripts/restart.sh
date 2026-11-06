#!/bin/bash
set -euo pipefail

# Run from the repository root. Keep the current Compose project and volumes.
# Build before stopping the services so a failed build leaves them running.
make build-all
docker compose stop web worker worker-dashboard
make up-d
