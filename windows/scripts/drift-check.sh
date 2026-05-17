#!/usr/bin/env bash
# Windows-specific drift-check wrapper. Runs inside WSL2.
# Delegates to repo-root per AP.3.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "${REPO_ROOT}/scripts/drift-check.sh" "$@"
