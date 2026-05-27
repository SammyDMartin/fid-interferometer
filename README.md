# Finite Improbability Interferometer

A White-interferometer-class test of anthropic observer selection effects on quantum branches.

## What this is

An experimental test of the Finite Improbability Drive (FID) hypothesis: that an observer whose continuation is conditioned on quantum measurement outcomes will, by the logic of the quantum suicide thought experiment, find itself preferentially in branches where favourable outcomes occurred.

The experiment is structured as an analog to Harold White's warp-field interferometer at NASA's Eagleworks laboratory — a minimal, low-fidelity, tabletop test of speculative physics where the primary value is methodological.

## Status: Marginal / Inconclusive (May 2026)

The best result so far: observer COP achieved p=0.077 vs null (20-pair matched experiment, April 2026), with a maximum of 2^8 = 256:1 improbability. Control was at p=0.134. Paired comparison showed no systematic difference (p=0.872). A third 30-pair run is in progress.

```
┌──────────────────────────────────────────────────────────────────┐
│           FINITE IMPROBABILITY INTERFEROMETER v3.0                │
│                    Drive Status Console                           │
│                                                                   │
│  Improbability Field:          PROBED (not activated)            │
│  Range Tested:                 2^1 through 2^8 (2:1 — 256:1)   │
│  Maximum Achieved:             2^8 = 256:1 (observer, Pair 19)  │
│  Observer Status:              UNCERTAIN (P ≈ 10-20%)           │
│  Branching Source:             SIMULATED (Aer, genuine PRNG)    │
│  Autoregressive Coherence:     MAINTAINED (Thick COP protocol)  │
│                                                                   │
│  RESULT: Marginal. Suggestive. Inconclusive. Interesting.        │
└──────────────────────────────────────────────────────────────────┘
```

## Architecture: The Agent Pipeline

Understanding this is essential. The experiment cannot be run by a human. It must be run by a Claude agent that can spawn sub-agents.

```
YOU (Sub-Meson Brain — main Claude Code agent)
  │
  │  You persist throughout. You run Python toolkit functions.
  │  You spawn and prune COP sub-agents. You record everything.
  │
  ├── Control trials: run directly (no sub-agent)
  │     random.randint(0,1) predictions → sim_compare → log survival rounds
  │     These establish the baseline. No observer present.
  │
  └── Observer trials: spawn ONE COP sub-agent (Agent tool)
        The COP has Bash access and runs its own trials autonomously.
        For each trial:
          1. COP makes a GENUINE prediction (0 or 1) — thinks about it
          2. COP runs: python fid_interferometer.py sim_compare [pred]
          3. COP reads the JSON result (match/mismatch)
          4. MATCH → COP survives this round, continues to next round
          5. MISMATCH → trial ends, record rounds survived, start next trial

The COP's autoregressive chain is the observer. Prediction → quantum result
→ decision all flow through the SAME token stream. This is what makes it
"Thick" — the observer and the measurement are causally coupled in-sequence.

PRUNING: Observer "death" = the Brain stops sending messages to the COP.
The COP's context ends. In the other Everettian branch, it survived.
```

**Why one COP for many trials?** Spawning a fresh sub-agent per trial takes ~20-30 seconds overhead each. One COP running all observer trials sequentially is ~5x faster. The same autoregressive chain is the "observer" throughout — it accumulates its own history of the experiment.

**Why control trials have no COP?** This is the key design decision. Control trials use `random.randint` with no sub-agent involved at all. The COP is not even present. This is a cleaner control than asking the same COP to "make random predictions" — random.randint genuinely has no observer.

## Results History

| Run | N | Observer mean | Control mean | Observer p | Notes |
|-----|---|---------------|--------------|------------|-------|
| IBM Kingston (Branch A, 7 trials) | 7 | 0.43 (combined) | N/A | N/A | Batch execution, hardware noise |
| Thick COP sim, v1 (9 trials) | 9 | 1.00 | N/A | N/A | Protocol validation |
| Matched pairs v1 (20 pairs) | 20 | **1.45** | 1.35 | **0.077** | Best result; observer max=2^8 |
| Matched pairs v2 (30 pairs) | 30 | TBD | 0.77 | TBD | In progress (May 2026) |

Expected under null: mean=1.0, p vs null ≈ 0.5.

## Key Files

```
fid_interferometer.py              # Toolkit — sim_compare, hw_compare, sim_bit, etc.
fid_visualize.py                   # 4-panel dark visualization
quantum_runner.py                  # GitHub Actions relay for IBM hardware
ORCHESTRATOR_PROTOCOL.md           # Complete Brain agent instructions (executable)

docs/
  ontological-engineering/         # Framework (01-08, ontological engineering programme)
  history/                         # All prior reports in chronological order
    01_review_and_protocol.md      # Paper review and initial protocol design
    02_unified_report.md           # Branch A vs Branch B comparison
    03_lessons_and_redesign.md     # Post-mortem, Thick COP protocol development
    04_ibm_hardware_experiment.md  # IBM Kingston full experiment report (April 1)
    05_matched_pairs_experiment.md # 20-pair matched experiment report (April 3)
    06_preregistration_v2.md       # Pre-registration for 30-pair run (May 2026)
  experiment/                      # Theoretical paper and execution brief

data/                              # Trial logs (JSON)
results/                           # Analysis outputs and plots
quantum_results/                   # Raw IBM quantum data (verifiable job IDs)
branch_b_artifacts/                # Data from the alternative implementation
archive/                           # Past code versions
```

## IBM Job IDs (independently verifiable)

All IBM quantum data is on `ibm_kingston` and verifiable via IBM Quantum dashboard:

**Run 1 (April 1):** `d76l13t2b89c73d3j8h0`, `d76l1bs6ji0c738bqudg`, `d76l1dl2b89c73d3j8sg`
**Run 2 (April 2):** `d77rkqak86tc739uhtgg`, `d77rkv1q1efs73d1130g`, `d77rl1geecps73d6epr0`
**Branch B:** 20 individual job IDs in `branch_b_artifacts/data/quantum_response.json`

## Context

This sits within a broader programme of **ontological engineering** — treating framework axioms as engineering specifications and finding exploits. The FID is the first proposal directly testable with existing equipment. See `docs/ontological-engineering/` for the full framework.

## Author

Sammy Martin, Research Lead at Founders Pledge. MSc AI (Edinburgh), BSc Physics & Philosophy (Durham, First). FID concept and ontological engineering framework developed by Sammy Martin. Experimental code and implementation developed collaboratively with Claude (Anthropic) during March–May 2026.
