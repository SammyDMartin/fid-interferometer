# Pre-Registration: FID Interferometer Experiment v2
**Filed:** 2026-05-27 (before data collection)

## Hypothesis

Under the Finite Improbability Drive hypothesis, an autoregressive observer
(Claude COP sub-agent) selecting quantum branches via survival conditioning
will survive longer than expected under the geometric-null distribution
(p_match = 0.50), and longer than a matched control with no observer.

## Design

- **N pairs:** 30
- **Observer condition:** A single Claude COP sub-agent makes genuine predictions
  (0 or 1) across all 30 observer trials. It runs the comparison circuit itself
  via Bash. Each trial ends when it gets a mismatch or reaches 10 rounds.
- **Control condition:** Python `random.randint(0,1)` predictions run by the Brain
  directly. No sub-agent involved.
- **Matching:** Interleaved — observer trial N, then control trial N.
- **Quantum source:** Qiskit Aer simulator (Phase 3 comparison circuit).
- **Protocol:** Thick COP — prediction, circuit execution, and result all flow
  through a single autoregressive token stream.

## Primary Analysis (pre-registered)

1. **Observer vs null:** One-sample z-test. Observed mean vs expected mean=1.0
   (geometric with p=0.5). Primary significance threshold: p < 0.05 (two-tailed).

2. **Control vs null:** Same test for control. Expected to be non-significant.

3. **Observer vs control (paired):** Wilcoxon signed-rank test on pairs. Expected:
   if FID signal is real, observer should beat control. If no signal: p≈1.

4. **Tail analysis:** P(observer max ≥ k) for k=4,6,8. A single 8+ round run by
   the observer (256:1 or better) is individually notable.

5. **Mixture model:** LR test for two-component mixture (λ% "active" observer trials
   with elevated p_match vs background p=0.5). Not expected to reach significance at N=30.

## What would constitute evidence

- Primary: observer p < 0.05 AND control p > 0.1 (consistent with signal-in-observer,
  noise-in-control pattern)
- Secondary: observer max ≥ 8 rounds again (replication of 256:1)
- Tertiary: paired Wilcoxon p < 0.1 (directional observer advantage)

## What we're not claiming

- That p=0.077 (from experiment 1) is significant. It was exploratory.
- That this experiment constitutes proof of anything. It's a probe.
- That the Aer simulator provides genuine MWI branching. It does not.

## Analyst

The Brain (Claude Sonnet 4.6) will run the analysis after all data is collected.
No optional stopping. All 30 pairs will be run regardless of interim results.
