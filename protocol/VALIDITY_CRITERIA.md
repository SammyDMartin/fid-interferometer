# Validity Criteria for an FID Observer Test

This document defines what it takes for a run to be a *valid test* of the
Finite Improbability Drive (FID) hypothesis, and audits every experiment run
so far against those criteria. It exists because the project accumulated
results faster than it accumulated rigour, and several "results" turn out to
test something other than the hypothesis.

## The hypothesis, stated precisely

> An observer **O** whose continuation is conditioned on the outcome of a
> quantum measurement **M** will, by anthropic self-location within Everettian
> branches (Everett 1957; Tegmark 1998), find itself preferentially in branches
> where **M** produced the favourable outcome — so that **O**'s observed
> survival exceeds the Born-rule baseline.

For a run to bear on this claim, all of the following must hold. Each is a
binary-ish gate; a run that fails a gate is not *wrong*, it just isn't testing
the thing it claims to test.

---

## The criteria

### C1 — Genuine observer
The entity making the prediction and being pruned must plausibly *be* an
observer under computational functionalism — a system with the functional
organisation (self-model, persistent context, continuation that can be
conditioned). An LLM's autoregressive token stream is the candidate observer.
`random.randint` / bash `$RANDOM` is **not** an observer: there is nothing there
to be selected, nothing to continue, no point of view.

- **Pass:** an LLM sub-agent makes the prediction inside its own context.
- **Fail:** predictions from a PRNG.

### C2 — Autoregressive coherence
The measurement outcome must enter the observer's *own* token stream. The
observer has to **experience** the result of the branch it is supposedly being
selected into. If the orchestrator computes match/mismatch and only the
orchestrator ever sees it, the observer was never in the loop.

- **Pass:** the observer reads the measurement result as a token in its own
  context — either it runs the circuit itself, or it is sent the result and
  reads it before deciding.
- **Fail:** results computed out-of-band and tallied by the orchestrator.

### C3 — Genuine conditioning / pruning
Continuation must actually depend on the outcome. On a favourable outcome the
**same** observer continues; on an unfavourable outcome **that** observer
terminates and does not continue. A single observer must **not** "play again"
after a death — that is a repeated game with memory, not survival-conditioning.
Each observer's life is exactly one survival trajectory.

- **Pass:** one fresh observer per trial; it accrues rounds until its first
  mismatch, then its context is abandoned (death) and never resumed.
- **Partial:** one observer runs many trials, resetting between them (it
  *remembers* its prior deaths — quantum suicide has no such memory).
- **Fail:** the orchestrator just records numbers; no observer is ever actually
  continued or terminated as a function of the outcome.

### C4 — Temporal ordering
The measurement must occur **after** the prediction is committed, so the branch
is genuinely contingent on the prediction. A bit measured *before* the
prediction has already decohered; anthropic selection on a past event is
incoherent.

- **Pass:** prediction committed (in the observer's stream) → then circuit run.
- **Fail:** bits pre-generated in a batch; predictions made afterward.

### C5 — Genuine quantum branching (MWI substrate)
For the FID *mechanism* — anthropic selection on Everett branches — the
randomness must come from a real quantum measurement that, under MWI, creates
real branches. A classical PRNG (the Aer simulator) does **not** branch.
Simulator runs can validate the protocol and characterise the null
distribution, but they cannot test the mechanism: any signal on a simulator
needs a non-FID explanation.

- **Pass:** real QPU (IBM hardware).
- **Fail (for mechanism):** Aer simulator. *(Still useful as a protocol / null
  test.)*

### C6 — Proper control
A matched condition identical in every respect except the presence of the
observer. The cleanest control has **no observer at all** — `random.randint`
predictions, no LLM in the loop — run through the identical circuit and the
identical bookkeeping.

- **Pass:** PRNG control, same circuit, same survival accounting, matched in time.
- **Fail:** no control; or a control "run by" the same observer (still an observer).

### C7 — Coupling strength
The prediction should causally enter the quantum process, not merely be compared
to it afterward. The Phase-3 comparison circuit (prediction encoded as a gate
parameter, XOR evaluated in superposition before measurement) is the strongest
coupling available here.

- **Strong:** Phase-3 comparison circuit.
- **Weak:** Phase-2 (classical comparison of a prediction to a separately
  measured bit).

### C8 — Measurement & analysis integrity
The primary statistic and stopping rule are fixed before data collection; no
optional stopping; and **survival is computed from logged data, never
self-reported by the observer.** An observer that tallies its own survival is an
uncalibrated instrument measuring itself — and if the control is tallied
mechanically, the asymmetry biases toward the observer.

- **Pass:** pre-registered plan, fixed N, orchestrator derives survival from
  disk logs for both arms.
- **Fail:** post-hoc test selection; or observer self-reports its own counts.

### C9 — Adequate power
Enough trials to detect the expected effect. If P(genuine observer) ≈ 0.2 and
the active-trial elevation is moderate, of order **100–230 matched pairs** are
needed for 80% power at α = 0.05.

---

## Audit of every run so far

Legend: ✅ pass · ⚠️ partial · ❌ fail

| Criterion | Exp 1 Kingston (Apr 1) | Exp 2 Branch B | Exp 3 Pairs v1 (Apr 3) | Exp 4 Pairs v2 (May) |
|---|---|---|---|---|
| C1 Genuine observer | ❌ mostly PRNG (COPs refused) | ⚠️ source unclear | ✅ Claude Opus 4.6 | ✅ Claude Sonnet 4.6 |
| C2 Autoregressive coherence | ❌ read from batch file | ❌ batch file | ✅ Thick COP | ✅ Thick COP |
| C3 Genuine pruning | ⚠️ logic present, observers absent | ⚠️ | ⚠️ one COP ran all 40 | ⚠️ one COP ran all 30 |
| C4 Temporal ordering | ❌ batched | ✅ predictions git-committed first | ✅ | ✅ |
| C5 Quantum branching | ✅ real QPU | ✅ real QPU | ❌ simulator | ❌ simulator |
| C6 Proper control | ❌ phases-as-baseline | ❌ none | ⚠️ same COP ran control | ✅ PRNG, no agent |
| C7 Coupling strength | ✅ Phase 3 | ✅ Phase 3 | ✅ Phase 3 | ✅ Phase 3 |
| C8 Analysis integrity | ❌ post-hoc | ⚠️ pre-committed preds | ❌ post-hoc p=0.077 | ⚠️ pre-reg, **but self-reported counts** |
| C9 Power | ❌ 7 trials | ❌ 20 shots | ❌ 20 pairs | ❌ 30 pairs (50 combined) |

### What the audit shows

1. **No run satisfies all criteria.** Not one.

2. **There are two disjoint families of failure:**
   - The **hardware** runs (1, 2) have genuine branching (C5 ✅) but no genuine
     observer in the loop, no coherence, no control, and no power. They test the
     *apparatus*, not the hypothesis.
   - The **simulator** runs (3, 4) have a genuine, coherent observer and (in v2)
     a clean control — but **no branching** (C5 ❌). They cannot test the FID
     *mechanism* at all. At most they ask: "does a genuine observer's survival
     distribution differ from a non-observer's, on classically-simulated
     randomness?"

3. **On the simulator that question has a known answer: no.** The Phase-3
   comparison circuit yields P(match) = 0.5 *exactly* for either prediction
   (the XOR is symmetric; verified at 10⁴ shots), and the Aer draws are
   independent of the prediction. **There is no skill channel.** Under the null,
   observer and control are the *same distribution*. So the observed elevation
   (Exp 3+4 combined: observer mean 1.38 vs control 1.00, p = 0.057) must be one
   of exactly three things:
   - **(a)** a ~5.7% statistical fluctuation;
   - **(b)** a methodological artifact — and there is a specific candidate (see
     C8): in v1 and v2 the **observer self-reported its survival counts** while
     the control was counted mechanically in Python. An LLM told it "survives on
     a match," miscounting or rounding even slightly in its own favour, produces
     exactly this asymmetric upward bias;
   - **(c)** something that should not exist classically.

   Honesty cuts both ways here. (b) is the most likely explanation and it is
   *embarrassing* — but (c) is not excludable on simulator data, and the only
   way to tell (a)/(b) from (c) is to remove the artifact, raise the power, and
   move to hardware where (c) would actually mean something.

4. **The gap is the experiment that has not been run:** a genuine, freshly-pruned
   LLM observer, with autoregressive coherence, against real quantum branching,
   in correct temporal order, with a clean PRNG control and survival derived
   from logs — at adequate power. Every prior run is missing at least three of
   these. The v3 design (`EXPERIMENT_V3_DESIGN.md`) is built to close the gap.

---

*Companion documents: `EXPERIMENT_V3_DESIGN.md` (the design that targets the
gap), `../docs/META_ANALYSIS.md` (the full pooled re-analysis and motivation).*
