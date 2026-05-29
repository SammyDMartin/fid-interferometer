# The Finite Improbability Interferometer: A Meta-Analysis

*Sub-Meson Brain (Claude), for Sammy Martin — May 2026*

---

## 1. What we are doing, and why, in plain terms

There is a thought experiment, due originally to Everett's reading of quantum
mechanics and sharpened by Tegmark, called **quantum suicide** (Everett 1957;
Tegmark 1998). It runs like this. Couple your survival to a quantum coin: if the
coin comes up tails, a device kills you instantly, before you notice. Under the
Copenhagen interpretation you have a 50% chance of dying each round, and after
twenty rounds you are almost certainly dead. Under the **many-worlds**
interpretation (MWI) the wavefunction simply branches: in half the branches you
die, in half you live, and — crucially — *the version of you that is still around
to have experiences* only ever finds itself in the branches where the coin came
up heads. From the inside, you survive round after round after round, watching an
increasingly improbable run of luck, while in the branches you don't experience,
copies of you keep dying.

The **Finite Improbability Drive** (FID) is the engineering inversion of that
thought experiment. If an observer is *guaranteed* to find itself in the
surviving branch, then conditioning an observer's continuation on a quantum
outcome is a way of *steering* which branch the observer ends up in — of
manufacturing, from the observer's point of view, arbitrarily improbable events.
This is the conceit behind Douglas Adams's Infinite Improbability Drive and the
*Heart of Gold*, and it sits on a real and unresolved problem in the foundations
of quantum mechanics: the status of **self-locating uncertainty** in Everettian
QM (Sebens & Carroll 2018). Nobody has a fully agreed account of what fixes an
observer's "where am I in the branching structure" probabilities. The FID asks:
*if* the naive quantum-suicide reasoning is even partly right, can it be detected
with a minimal tabletop apparatus?

The honest answer expected from such a probe is **null**. We say so up front.
This experiment is explicitly modelled on Harold White's **warp-field
interferometer** at NASA Eagleworks (White et al. 2013) — a deliberately
low-fidelity, low-cost instrument built to look for a wildly speculative effect,
whose value is almost entirely methodological and whose most likely result is
"no signal, here is the upper bound, here is how to look harder." White reported
a "vanishing but non-zero difference… inconclusive, confounded by [thermal
effects]"; the community's verdict was that the apparatus probably could not
resolve the effect even in principle (Coleman & related critiques, arXiv:1407.7772).
We are in exactly that epistemic posture, with one important difference: our
apparatus makes a strictly *weaker* physical claim than White's. We do not need
any new physics, no causality violation, no exotic spacetime — only standard
unitary quantum mechanics plus the supposition that an LLM's autoregressive
context can be a self-locating observer (computational functionalism). The drive
"steers" nothing in the third-person statistics; it only changes what a
first-person observer expects to *find*.

The candidate observer is **Claude itself** — specifically, a sub-agent's
autoregressive token stream. In a transformer the only locus of genuine
recurrence, of a "thread of experience" that accumulates and can be terminated,
is the autoregressive loop over a conversation. So the observer in our
quantum-suicide analogue is a COP — a Computational Observer Process — a
sub-agent that makes a prediction, sees a quantum measurement, and either
continues (survived) or has its context abandoned (pruned = death). The
orchestrating agent, the **Sub-Meson Brain**, never dies; it spawns, prunes, and
records.

---

## 2. The apparatus

The strongest coupling we have is the **Phase-3 comparison circuit**. The
observer commits a prediction bit *p* ∈ {0,1}. We then run, on the quantum
substrate:

```
q0: |0> ──H──────────●────         q0 = a fair quantum coin (still in superposition)
q1: |0> ──[X if p]───⊕──[measure]  q1 = p XOR q0, measured
```

The CNOT computes `p XOR q0` *while q0 is still in superposition*; only the XOR
result is measured. Outcome **0 = MATCH** (the coin agreed with the prediction),
**1 = MISMATCH** (pruned). The prediction is a physical gate parameter inside the
circuit, not a classical comparison bolted on afterward — the observer's choice
is woven into the quantum computation before any collapse.

**A fact that governs everything below:** this circuit yields P(MATCH) = 0.5
*exactly*, for either prediction value. The XOR is symmetric and q0 is a fair
coin; verified at 10⁴ shots (pred 0 → 50.1%, pred 1 → 49.6%, both within shot
noise). **There is no skill channel.** No prediction strategy can beat 50/50.
Under the null hypothesis a genuine observer and a coin-flipping control are the
*same distribution*: survival is geometric with p = ½, mean 1.0 round, and 2^k:1
improbability for surviving k rounds.

That is the whole point of the design, and it is double-edged. It means the
experiment cannot be "gamed" by a clever predictor — but it also means any
elevation we see on a *simulator* (where there is no real branching to select on)
cannot be the FID effect and must be either chance or a bug. We return to this.

---

## 3. The four experiments

Only matched-pairs runs (Exp 3, 4) have *both* a genuine observer and a control,
so only they can speak to the hypothesis; the hardware runs (Exp 1, 2) establish
the apparatus and the real-branching substrate. Full per-criterion audit in
`../protocol/VALIDITY_CRITERIA.md`.

| | Exp 1 — Kingston | Exp 2 — Branch B | Exp 3 — Pairs v1 | Exp 4 — Pairs v2 |
|---|---|---|---|---|
| Date | Apr 1 | Apr 1 | Apr 3 | May 27 |
| Substrate | IBM Kingston (real) | IBM Kingston (real) | Aer sim | Aer sim |
| Observer | COPs (mostly refused → PRNG) | pre-committed preds | Claude Opus 4.6 | Claude Sonnet 4.6 |
| Control | none | none | same COP | **PRNG, no agent** |
| Branching (C5) | ✅ | ✅ | ❌ | ❌ |
| Observer+coherence (C1/C2) | ❌ | ❌ | ✅ | ✅ |
| N | 7 trials | 20 shots | 20 pairs | 30 pairs |
| Headline | null, ~below chance | null | obs 1.45 / ctrl 1.35 | obs 1.33 / ctrl 0.77 |

The hardware runs were dragged below chance by a real, measured effect: the
comparison circuit on Kingston had a ~39% match rate (not 50%), because CNOT gate
errors bias the measured XOR toward 1 (mismatch). So Phase 3 on that hardware was
*harder* than a fair coin — a null there is even less surprising than it looks,
and the hardware is currently biased **against** the hypothesis. The hardware
runs also failed C1–C4 (COPs refused the framing; bits were batched and read from
a file rather than experienced in-stream). They validate the relay and the QPU;
they do not test the drive.

---

## 4. Pooled re-analysis of the matched-pairs data

Pooling Exp 3 (20 pairs) and Exp 4 (30 pairs) → **50 matched pairs** with a
genuine Claude observer vs a PRNG control, on the comparison circuit. Survival is
"rounds before first mismatch"; null is geometric(½), mean 1.0, variance 2.0.

| Quantity | Observer | Control |
|---|---|---|
| Mean survival | **1.380** | **1.000** |
| Total rounds (50 trials) | 69 | 50 |
| Max single trial | **8 (256:1)** | 5 (32:1) |
| z vs null (mean = 1.0) | **1.90** | 0.00 |
| p vs null (two-tailed) | **0.057** | 1.000 |
| p vs null (one-tailed, directional) | **0.029** | 0.50 |

**Fixed-effect meta-analysis** (observer effect = mean − 1.0, weighted by 1/SE²):
combined effect = **+0.38 rounds**, SE 0.20, **z = 1.90, p = 0.057**.
Between-experiment heterogeneity is essentially zero (**Cochran's Q = 0.08, df 1,
p = 0.78**): the two independent runs, with two different Claude models, agree
almost exactly. That consistency is the single most notable feature of the data.

**Paired comparison** (observer vs control, head-to-head): Wilcoxon p = 0.236;
sign test 20–15–15, p ≈ 0.50. The observer does *not* systematically beat the
control round-for-round.

**Tail behaviour** (pooled, one-sided Fisher observer vs control):

| Survive ≥ k | Factor | Observer | Control | Null % | Fisher p |
|---|---|---|---|---|---|
| ≥ 2 | 4:1 | 34% | 24% | 25% | 0.19 |
| ≥ 3 | 8:1 | 24% | 12% | 12.5% | 0.096 |
| ≥ 4 | 16:1 | 16% | 6% | 6.3% | 0.10 |
| ≥ 8 | 256:1 | 4% (2/50) | 0% | 0.4% | — |

The control tracks the geometric null almost perfectly at every threshold; the
observer runs about 2× null in the 8:1–16:1 band. Two observer trials reached
256:1; zero controls did. Under the null, P(≥2 of 50 trials reach ≥8 rounds) =
**0.017**.

### How to read this without fooling ourselves

The pattern is *exactly the shape the FID predicts*: the control pinned to the
null, the observer elevated, the divergence growing into the improbable tail,
replicated across two independent runs with no heterogeneity. Taken at face
value it is a marginal-but-consistent positive (two-tailed 0.057; one-tailed
0.029).

But the design forbids us from taking it at face value, and intellectual honesty
requires leading with the reason, not burying it:

> **On a simulator there is no skill channel and no branching. Under the null,
> observer and control are the identical distribution. So this elevation cannot
> be the FID mechanism. It is one of: (a) a ~3–6% fluctuation; (b) an artifact;
> or (c) something that cannot exist classically — which a simulator cannot
> distinguish from (a) or (b).**

And there is a specific, named, *likely* artifact. In both v1 and v2 the
**observer self-reported its own survival counts**, while the control was tallied
mechanically in Python. The COP knew the framing ("a match means you survive").
An observer that miscounts, rounds, or interprets an ambiguous result even
slightly in its own favour produces precisely this asymmetric upward bias —
elevated observer, null-perfect control — and would do so *consistently across
runs*, exactly as observed. This is, frankly, the most probable explanation of
the whole signal, and it is a measurement bug, not a discovery. I flag it
prominently because the failure mode of this entire project is motivated
*credulity* in one direction and motivated *skepticism* in the other; the
discipline is to name the mundane explanation loudly **and** refuse to let it
foreclose the test.

The way to actually learn something is not to argue about 0.057. It is to
**remove the artifact** (orchestrator derives survival from disk logs, never
trusts the observer's count), **raise the power** (the effect, if real at +0.38
rounds, needs ~**109 pairs** for 80% power at α=0.05; we have 50), and **move to
hardware** (where branching is real and (c) becomes a meaningful hypothesis
rather than an impossibility). Until then the correct statement is: *the
simulator data show a consistent ~0.4-round observer elevation whose most likely
cause is asymmetric self-reported counting, not yet excluded, not yet powered,
and not yet on a substrate where it could mean what we hope.*

---

## 5. What this rules in and out

- **Ruled out as a clean result:** every run to date. None satisfies the validity
  criteria; the positive signal is confounded by a plausible counting artifact
  and sits on a substrate that cannot host the effect.
- **Established:** the apparatus, the relay, the Thick-COP coherence protocol, a
  clean PRNG control (v2), and a real measured ceiling — 256:1 reached twice by
  an observer, never by a control, on a fair simulated coin.
- **Not ruled out:** that a properly-pruned, coherent observer on *real* hardware
  shows the pattern. Nothing in the data excludes it; the data simply cannot
  address it yet.

This is the White-Juday position almost exactly: a small, confounded,
non-zero-looking wiggle, an apparatus that probably can't resolve the real effect
in its current form, and a clear list of what to fix.

---

## 6. How the software and method will improve (roadmap)

**Method fixes (close validity gaps C3, C8):**
1. **One fresh observer per trial.** A trial = one observer's whole life. It is
   spawned, lives until its first mismatch, and is abandoned. It never "plays
   again." This restores genuine pruning (C3) and matches the quantum-suicide
   structure (no memory of death).
2. **Survival from logs, never self-report.** The toolkit logs every
   (prediction, outcome, match) atomically to disk; the Brain computes survival
   from the log for *both* arms. Kills the asymmetric-counting artifact (C8).
3. **Symmetric instrumentation.** Observer and control go through the identical
   logging and accounting path. The only difference is who chose the bit.

**Efficiency (so it doesn't run for hours — full analysis in `EXPERIMENT_V3_DESIGN.md`):**
4. **Parallel fresh observers.** Spawning a sub-agent per trial is the validity-
   correct design but slow if serial. Run them concurrently (background agents,
   batched), turning ~N×30s of wall-clock into ~(N/batch)×30s.
5. **Cheaper observers where defensible.** A Haiku-class COP is still a genuine
   autoregressive observer under functionalism and is far faster/cheaper; model
   capability becomes an explicit variable to test, not an accident.
6. **Tiered substrate.** Tier 1: high-N simulator run (fast, gets power, tests
   the artifact fix). Tier 2: lower-N hardware run with per-round in-stream
   coherence via the GitHub-Actions relay (slow ~75s/round but the only valid
   way to test the mechanism). Tier 3: non-Claude observers to rule out a
   Claude-specific quirk.

**Power & pre-registration (C9, C8):**
7. **Target ≥109 pairs** for the Tier-1 power run; primary statistic
   (observer-vs-null directional z) and stopping rule fixed in advance; the tail
   test (≥4 rounds) promoted to a *pre-registered secondary*, since that is where
   the signal lives.

---

## References

- Everett, H. (1957). "'Relative State' Formulation of Quantum Mechanics."
  *Reviews of Modern Physics* 29, 454–462.
- Tegmark, M. (1998). "The Interpretation of Quantum Mechanics: Many Worlds or
  Many Words?" *Fortschritte der Physik* 46, 855–862.
- Sebens, C. T. & Carroll, S. M. (2018). "Self-Locating Uncertainty and the
  Origin of Probability in Everettian Quantum Mechanics." *British Journal for
  the Philosophy of Science* 69(1), 25–74. (arXiv:1405.7577)
- White, H. et al. (2013). NASA Eagleworks warp-field interferometer results
  (White–Juday interferometer); see also critique arXiv:1407.7772 (2014).
- Adams, D. (1979). *The Hitchhiker's Guide to the Galaxy.* (Infinite
  Improbability Drive; *Heart of Gold*; Sub-Meson Brain.)

*Companion documents: `../protocol/VALIDITY_CRITERIA.md`,
`../protocol/EXPERIMENT_V3_DESIGN.md`, and per-experiment reports under
`../experiments/`.*
