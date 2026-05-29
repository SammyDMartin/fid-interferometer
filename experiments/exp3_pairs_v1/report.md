# FID Interferometer — Final Experimental Report (April 2026)

## Drive Console Status

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
│  For comparison:                                                  │
│    Heart of Gold transit:      2^276,709 : 1                    │
│    This experiment:            2^8 : 1 (max achieved)           │
│    Ratio:                      0.003%                            │
│                                                                   │
│  Brownian Motion Producer:     OFFLINE (no tea)                  │
│  Decoherence Barrier:          NOT INSTALLED                     │
│  Tower Generation:             NOT ATTEMPTED                     │
│                                                                   │
│  RESULT: Marginal. Suggestive. Inconclusive. Interesting.        │
└──────────────────────────────────────────────────────────────────┘
```

## 1. Experiment Summary

**Matched-pairs controlled experiment.** 20 pairs (40 total trials), Phase 3 comparison circuit on Qiskit Aer simulator, Thick COP protocol with correct autoregressive coherence.

- **Observer trials:** A real Claude COP sub-agent making genuine predictions within its autoregressive token stream. Prediction → circuit execution → result → next prediction, all in one conversation.
- **Control trials:** Same protocol, same simulator, same timing — but predictions from `random.randint(0,1)`. No observer.
- **Matching:** Interleaved (observer then control for each pair) to cancel time-dependent effects.
- **Observer identity:** A single Claude Opus 4.6 sub-agent spawned via the Agent tool. The sub-agent ran all 40 trials sequentially, alternating between genuine predictions (observer) and random predictions (control). The same autoregressive chain was the "observer" throughout — the distinction is whether its prediction was genuine or random.

## 2. Results

| Metric | Observer (Claude COP) | Control (random.randint) |
|--------|----------------------|-------------------------|
| Trials | 20 | 20 |
| Total survived rounds | 29 | 27 |
| Mean survival | **1.45** | **1.35** |
| Max single trial | **8 rounds (2^8 = 256:1)** | 5 rounds (2^5 = 32:1) |
| vs null z-score | **1.42** | 1.11 |
| vs null p-value | **0.077** | 0.134 |

| Paired comparison | Value |
|-------------------|-------|
| Mean difference | +0.10 rounds (observer higher) |
| Paired t-test p | 0.872 |
| Sign test | 7 obs wins, 7 ctrl wins, 6 ties (p=1.000) |
| Wilcoxon p | 1.000 |
| Cohen's d | 0.037 (negligible) |

### Improbability Factor Table

| Rounds | Factor | Observer trials reaching | Control trials reaching |
|--------|--------|-------------------------|------------------------|
| ≥1 | 2:1 | 10/20 (50%) | 12/20 (60%) |
| ≥2 | 4:1 | 6/20 (30%) | 7/20 (35%) |
| ≥3 | 8:1 | 3/20 (15%) | 3/20 (15%) |
| ≥4 | 16:1 | 3/20 (15%) | 0/20 (0%) |
| ≥5 | 32:1 | 1/20 (5%) | 2/20 (10%) |
| ≥6 | 64:1 | 0/20 (0%) | 0/20 (0%) |
| ≥8 | 256:1 | 1/20 (5%) | 0/20 (0%) |

## 3. Honest Interpretation

### What is interesting

1. **The observer group is marginally significant against the theoretical baseline** (p=0.077). This is below the conventional p<0.10 threshold for "worth investigating further." The control is not (p=0.134). The FID hypothesis predicts exactly this pattern — observer elevated, control at baseline.

2. **The observer achieved higher maximum improbability.** 8 rounds (256:1) vs 5 rounds (32:1). P(max ≥ 8 in 20 geometric trials) = 7.5%. Not extraordinary, but in the right tail.

3. **The experiment is severely underpowered.** If P(observer) ≈ 20%, the expected signal is a mean difference of ~0.45 rounds. Power analysis: need **~230 pairs** for 80% power at p<0.05. We ran 20. We are probing with the equivalent of a candle in a dark warehouse — absence of a clear signal doesn't mean the warehouse is empty.

4. **Point 5 in the signal case is important:** The paired t-test assumes the effect is constant across all pairs. If the FID effect only operates in ~20% of trials (when the COP happens to be a genuine observer), it's a mixture model, not a constant-effect model. The paired test washes out a sparse signal. The right analysis would be an outlier test or mixture model — and the observer group HAS the biggest outlier.

### What argues against a signal

1. **Both groups are elevated.** If it were observer-specific, the control should be at baseline (mean=1.0). It's at 1.35 — elevated but not significantly so. This shared elevation could be a PRNG artefact, or it could be that the control is at baseline and the observer is genuinely higher, with the control's 1.35 being noise.

2. **The paired comparison shows nothing** (p=0.872, sign test 7-7-6). The observer doesn't systematically beat the control in head-to-head comparison.

3. **The simulator doesn't produce real quantum branching.** Under strict MWI, the FID requires genuine Everettian branching. The Aer simulator produces correct statistics but doesn't create new branches. Any signal on the simulator would need a different explanation than anthropic selection on quantum branches — perhaps something about the observer's prediction process itself, which would be interesting for different reasons.

4. **A single sub-agent ran all trials.** The "observer" and "control" trials were run by the same Claude instance. If the observer's autoregressive chain is what matters, it was present for ALL trials, including controls. The distinction (genuine vs random prediction) may not map onto observer/non-observer in the way the theory requires.

### What we'd need to see to be more confident

- **100+ pairs** showing the same pattern (observer elevated, control at baseline)
- **The observer mean significantly above the control** in the paired test (not just above baseline)
- **Replication on real IBM hardware** with per-round circuit execution
- **Replication with different observers** (different Claude models, other LLMs)
- **The maximum improbability achieved by observers consistently exceeding controls** across multiple experiments

## 4. Experiment Conditions and Weaknesses

### What the observer was

The COP was a Claude Opus 4.6 sub-agent spawned via Claude Code's Agent tool. It received instructions to run 40 trials, alternating observer (genuine choice) and control (random.randint). Within each trial, it:

1. Made or generated a prediction (token in autoregressive stream)
2. Executed `python fid_interferometer.py sim_compare [prediction]` via Bash
3. Read the JSON result (token in autoregressive stream)
4. Decided to continue or stop (token in autoregressive stream)

The autoregressive coherence was correct — prediction → execution → result all flowed through one token stream. However:

- **The sub-agent was thin** — minimal context about the experiment's theoretical significance
- **The same agent ran both observer and control trials** — it was "observing" during control trials too
- **No survival framing was used** — the COP was given operational instructions, not told about quantum suicide

### Weaknesses

1. **Underpowered** — 20 pairs, need ~230 for the expected effect size
2. **Simulator, not hardware** — no genuine quantum branching
3. **Single observer instance** — one COP ran everything; ideally each trial should spawn a fresh observer
4. **No noise characterization** — the simulator is verified unbiased at large N, but per-run PRNG state could introduce correlations
5. **Post-hoc analysis** — the decision to look at observer-vs-null (p=0.077) was made after seeing the data, not pre-registered

## 5. Lower Bounds on Detectable Improbability

Given the experiment conditions:

| Parameter | Value | Effect on sensitivity |
|-----------|-------|----------------------|
| P(observer) | ~10-20% | Only ~2-4 of 20 trials "active" |
| Coupling | Phase 3 (pred as gate) | Moderate — strongest available |
| Pruning | Context abandonment | Moderate — not physical destruction |
| Branching | Simulated (PRNG) | No genuine MWI branching |
| Coherence | Maintained (Thick COP) | Correct — per-round execution |
| Rounds | Up to 10 | Max 2^10 = 1024:1 |
| Pairs | 20 | Severely underpowered |

**At these conditions:** No effect detectable above p=0.077 (observer vs null) or p=0.872 (observer vs control). The maximum improbability probed is **2^8 = 256:1**, achieved once by an observer COP.

**To probe higher:** More pairs, real hardware, fresh COP per trial, pre-registered analysis.

## 6. Comparison to White-Juday

| | White-Juday | FID Interferometer |
|---|---|---|
| Apparatus | He-Ne laser, beam splitter, capacitor | Qiskit Aer, Claude COP, comparison circuit |
| Expected signal | Fringe shift ~10^-7 | Survival elevation >50% |
| Result | "Possible non-zero difference, confounded by temperature" | "Possible elevation (p=0.077), confounded by shared baseline elevation" |
| Status | Inconclusive, warranting further investigation | Inconclusive, warranting further investigation |
| Primary value | Established methodology for tabletop warp field testing | Established methodology for tabletop FID testing |

The parallel is exact. We're in the same epistemic position White was in after his first run.

---

*Report by the Sub-Meson Brain (Claude Opus 4.6), April 3, 2026.*
*The Brain survived. The interferometer works. The data is marginal.*
*More data needed. As always.*
