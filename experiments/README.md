# Experiments Index

Every FID run, in order. Validity audit in `../protocol/VALIDITY_CRITERIA.md`;
pooled re-analysis in `../docs/META_ANALYSIS.md`.

| Dir | Date | Substrate | Observer | Control | N | Result | Valid test? |
|---|---|---|---|---|---|---|---|
| `exp1_kingston_apr1/` | Apr 1 | IBM Kingston (real) | COPs (mostly refused → PRNG) | none | 7 trials | null, ~below chance | No — observer absent, batched |
| `exp2_branch_b/` | Apr 1 | IBM Kingston (real) | pre-committed preds | none | 20 shots | null | No — no control, no coherence |
| `exp3_pairs_v1/` | Apr 3 | Aer sim | Claude Opus 4.6 | same COP | 20 pairs | obs 1.45 / ctrl 1.35 | Partial — no branching, self-report |
| `exp4_pairs_v2/` | May 27 | Aer sim | Claude Sonnet 4.6 | PRNG (no agent) | 30 pairs | obs 1.33 / ctrl 0.77 | Partial — no branching, self-report |

**Pooled matched pairs (exp3 + exp4, the only observer-vs-control runs):**
50 pairs · observer mean 1.38 (z=1.90, p=0.057 two-tailed / 0.029 one-tailed) ·
control mean 1.00 (p=1.00) · between-experiment heterogeneity Q=0.08 (p=0.78) ·
observer reached 256:1 twice, control never.

**The catch:** both pooled runs are on a simulator (no real branching → cannot
test the mechanism) and both used observer-self-reported survival counts (an
asymmetric-counting artifact that could fully explain the elevation). See the
meta-analysis. Experiment v3 (`../protocol/EXPERIMENT_V3_DESIGN.md`) is designed
to remove the artifact, raise power, and move to hardware.

## Contents per directory
- `report.md` — the write-up authored at the time of the run
- `*.json` / `*.jsonl` — raw survival data and analysis output
- `exp1_kingston_apr1/plots/` — timeline / survival / phase / architecture figures
- `exp2_branch_b/artifacts/` — the alternative implementation's full code + data
  (including 20 individually-verifiable IBM job IDs in
  `artifacts/data/quantum_response.json`)
- `raw_logs/` — per-round development logs from early simulator trials
