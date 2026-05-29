# Finite Improbability Interferometer

A White-interferometer-class test of anthropic observer selection on quantum
branches. A minimal, low-fidelity tabletop probe of the quantum-suicide /
Finite-Improbability-Drive hypothesis — modelled on NASA Eagleworks' warp-field
interferometer, where a null result is expected and the value is methodological.

**Full motivation, theory, and pooled re-analysis: [`docs/META_ANALYSIS.md`](docs/META_ANALYSIS.md).**

## Status (May 2026): marginal, confounded, not yet a valid test

Across the only two runs with both a genuine observer and a control (50 matched
pairs, simulator), the observer survives longer than the geometric null
(mean 1.38 vs null 1.0, **p=0.057**) while the control sits exactly at null —
consistent across two independent runs (heterogeneity p=0.78). **But** the
simulator has no real branching (so it cannot test the mechanism) and both runs
let the observer *self-report* its survival counts (an asymmetric-counting
artifact that could fully explain the elevation). No run to date satisfies the
validity criteria. See [`protocol/VALIDITY_CRITERIA.md`](protocol/VALIDITY_CRITERIA.md).

## The idea in one paragraph

Under many-worlds, an observer whose continuation is conditioned on a quantum
coin only ever *finds itself* in branches where the coin went its way (Everett
1957; Tegmark 1998). The candidate observer here is an LLM's autoregressive
context: a sub-agent (a **COP**, Computational Observer Process) predicts a bit,
a quantum **comparison circuit** computes prediction-XOR-coin in superposition,
and on a mismatch the sub-agent's context is abandoned — pruned. The orchestrator
(**Sub-Meson Brain**) spawns and prunes; it never dies. The circuit has *no skill
channel* (P(match)=0.5 exactly), so any elevation is chance, a bug, or the effect.

## The agent pipeline

```
SUB-MESON BRAIN (orchestrator agent — persists)
 ├── CONTROL ARM:  pure code, no LLM — random.randint plays the circuit
 │                 (src/experiment.py control)
 ├── OBSERVER ARM: one FRESH sub-agent per trial (the observer). It lives one
 │                 life — predict → observe → read result → continue/stop — all
 │                 in its own token stream. Mismatch ⇒ context abandoned (pruned).
 └── AGGREGATE:    survival derived from disk logs (never self-report); analysis.
                   (src/experiment.py aggregate → src/analyze.py)
```

The current, validity-correct version of this (fresh observer per trial, parallel,
log-derived survival, tiered sim→hardware) is specified in
[`protocol/EXPERIMENT_V3_DESIGN.md`](protocol/EXPERIMENT_V3_DESIGN.md) — **proposed, not yet run.**

## Repository layout

```
src/                       Python: toolkit, analysis, control+aggregate harness, relay
  fid_interferometer.py      circuits + observe/survival primitives (authoritative logging)
  analyze.py                 unified statistics engine
  experiment.py              v3 control arm + aggregation
  fid_visualize.py           figures
  quantum_runner.py          IBM hardware runner (GitHub Actions relay)
protocol/                  How the experiment is run
  EXPERIMENT_V3_DESIGN.md    current design (review before running)
  VALIDITY_CRITERIA.md       the 9 criteria + per-experiment audit
  ORCHESTRATOR_PROTOCOL.md   original phased architecture + rationale
  observer_prompt.md         exact COP prompt
docs/
  META_ANALYSIS.md           full report: motivation, theory, pooled re-analysis, roadmap
  ontological-engineering/   the broader framework (01–08)
  experiment/                the theory paper
  history/                   archived prior reports (chronological)
experiments/               one directory per run + README index
  exp1_kingston_apr1/  exp2_branch_b/  exp3_pairs_v1/  exp4_pairs_v2/  raw_logs/
.github/workflows/         quantum_run.yml — IBM relay (runs src/quantum_runner.py)
```

## Reproduce the analysis

```bash
pip install qiskit qiskit-aer scipy
python src/fid_interferometer.py verify          # confirm circuit XOR is fair (no skill channel)
python src/analyze.py experiments/exp4_pairs_v2/v2_observer_trials.json \
                      experiments/exp4_pairs_v2/v2_control_trials.json  v2
```

## IBM job IDs (independently verifiable on IBM Quantum)

Run 1 (Apr 1): `d76l13t2b89c73d3j8h0`, `d76l1bs6ji0c738bqudg`, `d76l1dl2b89c73d3j8sg` ·
Run 2 (Apr 2): `d77rkqak86tc739uhtgg`, `d77rkv1q1efs73d1130g`, `d77rl1geecps73d6epr0` ·
Branch B: 20 IDs in `experiments/exp2_branch_b/artifacts/data/quantum_response.json`.

## Author

Sammy Martin, Research Lead at Founders Pledge. The FID concept and the
ontological-engineering framework are his; implementation developed with Claude
(Anthropic), March–May 2026.
