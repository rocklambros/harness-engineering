# Hooks (Jetson) — SCAFFOLDED

Phase 3 of the Jetson build produces the validated hook scripts. The hook scripts are expected to be byte-identical to Mac (same bash, same jq, same Semgrep invocations) but this expectation needs hardware validation.

See `mac/harness/hooks/README.md` for the canonical hook documentation. Jetson differences, if any, are documented per-hook in the script header comments after Phase 3 validation.

The post-tool-use Semgrep hook implements the SecureForge Appendix C pattern (R.2.1) identically across all three platforms. Layer 2 of the three-layer security stack.
