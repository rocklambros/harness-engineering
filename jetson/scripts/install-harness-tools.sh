#!/usr/bin/env bash
set -euo pipefail

# Installs the security tools required by the Jetson harness.
# Run this before Phase 3. Requires sudo for apt and gitleaks install.
# Phase 2 decision reference: jetson/phase-outputs/ANSWERS.md

SEMGREP_VERSION="1.163.0"
GITLEAKS_VERSION="8.21.2"

echo "=== Semgrep ${SEMGREP_VERSION} (conda base) ==="
pip install "semgrep==${SEMGREP_VERSION}"

echo ""
echo "=== Semgrep ${SEMGREP_VERSION} (system Python 3.10) ==="
/usr/bin/python3.10 -m pip install --user "semgrep==${SEMGREP_VERSION}"

echo ""
echo "=== pre-commit (conda base) ==="
pip install pre-commit

echo ""
echo "=== gitleaks v${GITLEAKS_VERSION} (binary to /usr/local/bin/) ==="
curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_arm64.tar.gz" \
  | sudo tar -xz -C /usr/local/bin/ gitleaks
sudo chmod +x /usr/local/bin/gitleaks

echo ""
echo "=== shellcheck (apt) ==="
sudo apt install -y shellcheck

echo ""
echo "=== Verification ==="
echo "semgrep:    $(semgrep --version 2>/dev/null || echo 'FAILED')"
echo "gitleaks:   $(gitleaks version 2>/dev/null || echo 'FAILED')"
echo "shellcheck: $(shellcheck --version 2>/dev/null | grep '^version:' || echo 'FAILED')"
echo "pre-commit: $(pre-commit --version 2>/dev/null || echo 'FAILED')"
echo "jq:         $(jq --version 2>/dev/null || echo 'FAILED')"
echo ""
echo "Install complete. Ready for Phase 3."
