#!/usr/bin/env bash
# pre-flight.sh - One-time setup to move existing research docs into research/.
#
# Run this once after the initial repo seed. The three research documents
# currently live in the repo root (legacy state). This script moves them to
# research/ and normalizes the SAGE doc filename (which has a space).
#
# Idempotent: safe to re-run; only acts on files that exist in the wrong place.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p research

# Move Claude_Architecture.md if it's in root.
if [[ -f "Claude_Architecture.md" ]]; then
  echo "moving Claude_Architecture.md to research/"
  mv "Claude_Architecture.md" research/
fi

# Move and rename the SAGE doc (note the space in the original filename).
if [[ -f "Harness_Engineering_for_Claude_Code_A_Systems_Architecture Analysis.md" ]]; then
  echo "moving and renaming SAGE doc to research/"
  mv "Harness_Engineering_for_Claude_Code_A_Systems_Architecture Analysis.md" \
     "research/Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md"
elif [[ -f "Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md" ]]; then
  echo "moving SAGE doc (already normalized name) to research/"
  mv "Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md" research/
fi

# Move NIST doc if it's in root.
if [[ -f "NIST.SP.800-218-Secure-Software-Development-Framework.md" ]]; then
  echo "moving NIST.SP.800-218 to research/"
  mv "NIST.SP.800-218-Secure-Software-Development-Framework.md" research/
fi

# Verify the expected files are now in research/.
echo ""
echo "research/ contents after pre-flight:"
ls -la research/ 2>/dev/null || echo "  (research/ is empty)"

# Make scripts executable.
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x mac/scripts/*.sh 2>/dev/null || true
chmod +x mac/harness/hooks/*.sh 2>/dev/null || true
chmod +x jetson/scripts/*.sh 2>/dev/null || true
chmod +x jetson/harness/hooks/*.sh 2>/dev/null || true
chmod +x windows/scripts/*.sh 2>/dev/null || true
chmod +x windows/harness/hooks/*.sh 2>/dev/null || true

echo ""
echo "pre-flight complete"
