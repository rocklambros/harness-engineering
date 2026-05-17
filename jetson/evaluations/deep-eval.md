# Stage 2 Deep Evaluation (Jetson)

Jetson-specific deep evaluations. Run during Phase 2 for candidates that survive pre-filter.

The five dimensions (Capability fit, QC alignment, Integration cost, Replaceability, Maintenance burden) are the same as Mac. The Jetson-specific concerns surface in Integration cost (aarch64 install paths) and Maintenance burden (JetPack-version-tied dependencies).

## Reference: Mac deep-eval results

Read `mac/evaluations/deep-eval.md` first. Tools adopted on Mac generally adopt on Jetson with the integration-cost dimension re-scored for the Jetson install path.

Phase 2 produces the Jetson-specific deep-eval entries here.
