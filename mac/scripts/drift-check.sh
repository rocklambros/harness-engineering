#!/usr/bin/env bash
# Mac-specific drift-check wrapper. Delegates to the repo-root drift check so
# the cross-platform logic stays in one place. Per AP.3, every platform has the
# capability; the script just routes to the shared implementation.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec "${REPO_ROOT}/scripts/drift-check.sh" "$@"
