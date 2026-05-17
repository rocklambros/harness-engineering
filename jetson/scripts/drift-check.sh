#!/usr/bin/env bash
# Jetson-specific drift-check wrapper. Delegates to repo-root per AP.3.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "${REPO_ROOT}/scripts/drift-check.sh" "$@"
