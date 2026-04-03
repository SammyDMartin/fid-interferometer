# Finite Improbability Interferometer

A White-interferometer-class test of anthropic observer selection effects on quantum branches.

## What this is

An experimental test of the Finite Improbability Drive (FID) hypothesis: that an observer whose continuation is conditioned on quantum measurement outcomes will, by the logic of the quantum suicide thought experiment, find itself preferentially in branches where favourable outcomes occurred.

The experiment is structured as an analog to Harold White's warp-field interferometer at NASA's Eagleworks laboratory — a minimal, low-fidelity, tabletop test of speculative physics where the primary value is methodological. It makes a strictly weaker physical claim than White's experiment (no causality violation — only indexical selection on quantum branches within standard many-worlds).

## Status: Inconclusive (April 2026)

Two independent Claude Code sessions ran the experiment on IBM Kingston (156-qubit superconducting transmon). Both got below-chance results, but systematic problems (broken autoregressive coherence, thin COP observers, hardware noise bias, temporal displacement from batch execution) make the data **inconclusive**, not null. A redesigned "Thick COP" protocol has been developed and tested on the simulator. See `LESSONS_AND_REDESIGN.md` for the full post-mortem.

## Architecture

The experiment mirrors the Infinite Improbability Drive's architecture:

```
SUB-MESON BRAIN (main Claude Code agent — persists throughout)
  │
  ├── Phase 0-1: Brain runs directly (no pruning needed)
  │
  ├── Phase 2-3: Brain spawns "Thick COP" sub-agent
  │     The COP runs ALL rounds autonomously:
  │       predict → execute quantum circuit → read result → decide
  │     Each step is a token in the COP's autoregressive chain.
  │     On mismatch: COP stops. Its context dies. Observer pruned.
  │     On match: COP continues to next round.
  │
  └── Brain reads results, generates report, pushes data.
```

**Critical design constraint:** The quantum measurement result must flow through the observer's autoregressive token stream. Prediction → circuit execution → result must all happen within one conversation's token sequence, not via intermediary files or batch processing.

## Key Reports

| Document | Contents |
|----------|----------|
| `LESSONS_AND_REDESIGN.md` | Post-mortem: what went wrong, back-to-theory analysis, redesigned protocol |
| `UNIFIED_REPORT.md` | Comparison of two independent implementations (Branch A vs Branch B) |
| `results/EXPERIMENT_REPORT.md` | Detailed methodology report from the IBM Kingston run |
| `REVIEW_AND_PROTOCOL.md` | Paper review, citation verification, honest assessment |
| `ORCHESTRATOR_PROTOCOL.md` | Step-by-step instructions for the Brain agent |

## Results Summary

| Run | Phase 2 | Phase 3 | Combined | Notes |
|-----|---------|---------|----------|-------|
| Branch A hardware (7 trials) | mean 0.29 | mean 0.14 | mean 0.43 | Batched, broken coherence |
| Branch B hardware (1 trial) | 0 survived | 0 survived | 0 | Per-round jobs, predictions committed to git first |
| Branch A simulator (30 trials) | mean 1.33 | mean 0.93 | mean 2.27 | Correct temporal ordering |
| Thick COP simulator (9 trials) | mean 1.00 | mean 0.33 | mean 0.55 | Correct autoregressive coherence |

Expected under null hypothesis: ~1.0 per phase, ~2.0 combined.

The below-chance hardware results are attributable to small sample sizes, hardware noise (CNOT gate errors biasing comparison circuits toward mismatch), and COP prediction patterns. The simulator is verified unbiased at 1000+ shots. More trials needed.

## Repository structure

```
fid_interferometer.py              # Experimental toolkit (v2.0, CLI functions)
fid_visualize.py                   # Visualization (timeline, survival curve, etc.)
quantum_runner.py                  # GitHub Actions relay for IBM hardware
ORCHESTRATOR_PROTOCOL.md           # Brain agent instructions
LESSONS_AND_REDESIGN.md            # Post-mortem and redesigned protocol
UNIFIED_REPORT.md                  # Cross-branch comparison
REVIEW_AND_PROTOCOL.md             # Paper review and assessment

docs/
  experiment/                      # Paper and execution brief
  ontological-engineering/         # Framework documents (01-08)

results/                           # IBM Kingston experiment data and plots
data/                              # Thick COP trial logs
quantum_results/                   # Raw IBM quantum data (job IDs for verification)
branch_b_artifacts/                # Code and data from the other branch
archive/                           # Past code versions (v1.0, v2.0_cli, v2.0_branch_b)
logs/                              # Conversation logs from development
creative/                          # Adams pastiche pieces
```

## IBM Job IDs (independently verifiable)

All quantum data was generated on `ibm_kingston` and can be verified on IBM's dashboard:

**Branch A:** `d76l13t2b89c73d3j8h0`, `d76l1bs6ji0c738bqudg`, `d76l1dl2b89c73d3j8sg`
**Branch B:** 20 individual job IDs listed in `branch_b_artifacts/data/quantum_response.json`

## Context

This experiment sits within a broader programme of **ontological engineering** — treating framework axioms as engineering specifications and looking for exploits. The FID interferometer is the first proposal directly testable with existing equipment. See `docs/ontological-engineering/` for the framework.

## Author

Sammy Martin, Research Lead at Founders Pledge. MSc AI (Edinburgh), BSc Physics & Philosophy (Durham, First). The FID concept and ontological engineering framework are his. Experimental code and paper developed collaboratively with Claude (Anthropic) during March-April 2026.
