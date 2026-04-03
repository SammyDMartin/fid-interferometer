# Code Version Archive

Past versions of the experimental code, preserved for reference.

## v1.0 (Branch A, first refactor)
- `fid_interferometer.py` — Monolithic script with `ExperimentRunner` class
- Had the four control flow bugs identified in the post-mortem:
  1. Orchestrator kills itself on mismatch
  2. Phase 2 pre-batches all quantum bits
  3. Predictions via plain function (no observer lifecycle)
  4. Can't be run by humans (but also can't properly be run by AI)
- Commit: `145a071` (April 1, 2026)

## v2.0_cli (Branch A, CLI toolkit)
- `fid_interferometer.py` — Atomic CLI functions (sim_bit, hw_bit, etc.)
- `fid_visualize.py` — Separate visualization module
- `ORCHESTRATOR_PROTOCOL.md` — Step-by-step Brain agent instructions
- Fixed all four bugs but introduced temporal displacement via batching
- Commit: `3fdc394` (April 1, 2026)

## v2.0_branch_b (Branch B, monolithic module)
- `fid_interferometer.py` — Per-round functions (phase2_round, phase3_round)
- `quantum_runner.py` — GitHub Actions quantum relay (20 single-shot jobs)
- Same architectural fix as v2.0_cli, different code style
- Notable: committed COP predictions to git before measurements
- Branch: `claude/review-code-feasibility-fvwU1`, commit: `01cfc28`

## Current (v3.0 — Thick COP protocol)
- See root `fid_interferometer.py` and `ORCHESTRATOR_PROTOCOL.md`
- Key change: COP runs circuits ITSELF within its autoregressive chain
- Prediction → execute circuit → read result all in one token stream
- Fixes the autoregressive coherence problem identified in the post-mortem
