# Experiment v3 — Design (for review before running)

This design closes the validity gaps identified in `VALIDITY_CRITERIA.md` and the
artifact identified in `../docs/META_ANALYSIS.md`. **It has not been run.** It is
here for you to judge first.

---

## What was wrong before, and what changes

| Problem in v1/v2 | Fix in v3 | Criterion |
|---|---|---|
| One COP ran all 30 trials → never actually pruned; remembered its "deaths" | **One fresh observer (sub-agent) per trial.** A trial = one observer's entire life. | C3 |
| Observer **self-reported** its survival counts; control counted mechanically → asymmetric upward bias | **Survival derived from disk logs** written by the toolkit; observer never counts itself. Identical path for both arms. | C8 |
| "Control" was the same COP making random picks → an observer was still present | **Control has no LLM at all** (PRNG via the same `observe` primitive). | C6 |
| Slow if done correctly (sub-agent per trial, serial) | **Parallel** fresh observers; optionally a **cheaper model**. | efficiency |
| Simulator only → can't test the mechanism | **Tiered**: fast sim for power, then real hardware for the mechanism. | C5 |

The one thing v3 deliberately does **not** change: the comparison circuit. It is
the strongest coupling we have and its no-skill-channel property (P(match)=0.5
exactly) is a feature — it means nothing but chance, a bug, or the real effect
can move the needle.

---

## Architecture

```
SUB-MESON BRAIN (me, the orchestrator — persists, never pruned)
│
├── CONTROL ARM  (pure code, no LLM — runs first, ~seconds)
│     src/experiment.py control runs/<exp>/control  N  sim
│     N trials. Each: random.randint plays the comparison circuit round by
│     round via `fid_interferometer observe` until first mismatch. One JSONL
│     log per trial. NO observer is ever present.
│
├── OBSERVER ARM  (N fresh LLM sub-agents — the actual observers)
│     For each trial t in 1..N:
│       • I spawn a NEW sub-agent (the COP). Fresh context = a new observer.
│       • Its whole task is to live ONE life:
│           repeat (up to 10 rounds):
│             1. commit a genuine prediction p ∈ {0,1}   (a token in ITS stream)
│             2. run:  python src/fid_interferometer.py observe <its_log> p sim
│             3. read stdout: "MATCH — survive" or "MISMATCH — pruned"   (C2)
│             4. MATCH → next round.  MISMATCH → stop. Its life is over.
│       • The toolkit writes the authoritative result to <its_log> each round.
│       • When it mismatches it simply ends — context abandoned = pruned (C3).
│     Sub-agents are spawned in PARALLEL batches (efficiency, below).
│
└── AGGREGATE  (pure code)
      src/experiment.py aggregate runs/<exp>/observer runs/<exp>/control <label> <out>
      Reads EVERY trial log from both dirs, derives survival = consecutive
      MATCH-from-start, runs the unified analysis (src/analyze.py), writes result.
      Survival is ground truth from disk; no self-report enters the statistics.
```

The observer literally cannot inflate its score: it decides only *continue/stop*;
the count comes from the log the toolkit wrote.

---

## Efficiency analysis (the "don't run for hours" problem)

The validity-correct design — one fresh observer per trial — is the expensive
one. The cost is **sub-agent spawn + a few short turns**, not compute. Options,
in the order they buy time:

1. **Parallelism (biggest win).** Trials are independent, so spawn observers
   concurrently as background agents in batches of ~10. 109 trials ≈ 11 batches.
   Wall-clock drops from ~109 × (spawn+rounds) serial to ~11 × that. Estimated
   **~10–20 min** for the full Tier-1 run instead of a couple of hours.
2. **Cheaper observer model.** A Haiku-class COP is still a genuine autoregressive
   observer under computational functionalism — there is no principled reason the
   observer must be Opus. It is several times faster and cheaper per trial. Model
   capability then becomes an *explicit variable* (Tier 3), not a hidden cost.
3. **Short lives are cheap.** Mean survival ≈ 1 round, so most observers make 1–3
   `observe` calls and stop. The long tail (8 rounds) is rare. Average trial is a
   handful of tool calls.
4. **Subprocess overhead is the floor, not the model.** Each `observe` is a fresh
   Python process (~0.3 s for qiskit import). For sim runs this dominates round
   latency far more than the LLM. If we ever need 1000s of rounds, a persistent
   server mode is the next optimisation — not needed at N≈109.

Net: the **fast path** is parallel Haiku observers on the simulator. That is what
Tier 1 uses.

---

## The three tiers

### Tier 1 — Simulator power run (run this first)
- **Goal:** reach adequate power (~**109 pairs**) with the artifact fixed, to see
  whether the v1/v2 elevation survives honest log-derived counting. If the signal
  was the self-report artifact, it should **vanish** here. If it persists, that is
  genuinely interesting (and demands Tier 2).
- Substrate: Aer simulator. **Cannot test the FID mechanism** (no branching) — by
  design. This tier tests the *protocol and the artifact*, not the physics.
- Observer: parallel Haiku-class COPs, one per trial.

### Tier 2 — Hardware confirmation run
- **Goal:** the only valid test of the mechanism. Real branching (C5), correct
  temporal order (C4), coherence (C2).
- Substrate: IBM hardware via the GitHub-Actions relay. Because the relay is
  ~75 s per circuit, the observer's loop is **Brain-mediated**: the observer
  commits a prediction → I trigger the relay → I send the result back → the
  observer *reads it in its own stream* → decides. Coherence preserved, just slow.
- N is modest here (e.g. 20–30) — confirmation, not power.
- **Caveat already known:** Kingston's comparison circuit runs ~39% match (CNOT
  error), biasing Phase 3 *against* survival. Either characterise and correct for
  it, or pick a lower-error backend / qubit pair first.

### Tier 3 — Cross-observer replication
- Repeat Tier 1 with **non-Claude** observers (and Haiku vs Opus) to test whether
  any residual effect is Claude-specific (which would point to an artifact in the
  observer rather than the substrate).

---

## Pre-registration (Tier 1)

- **N = 109 matched pairs** (powers the observed +0.38-round effect at 80%, α=.05).
- **Primary statistic:** observer mean survival vs the geometric null (mean 1.0),
  one-tailed (directional: the hypothesis predicts elevation). Significant if
  **p < 0.05**.
- **Key control check:** control mean must be consistent with null (p > 0.1). If
  the control is *also* elevated, the result is a shared artifact, not a signal.
- **Pre-registered secondary:** tail test at ≥4 rounds (16:1), one-sided Fisher,
  observer vs control — this is where the v1/v2 signal concentrated.
- **Stopping rule:** run all 109; no peeking, no optional stopping.
- **Survival source:** disk logs only.
- **Analyst:** the Brain, after all data is in.

### What each outcome would mean
- **Control at null, observer not elevated (p > 0.05):** the v1/v2 signal was the
  self-report artifact (or chance). Clean negative. Most likely outcome. Good.
- **Control at null, observer elevated (p < 0.05) on the *simulator*:** something
  classically inexplicable — not the FID mechanism (no branching), so a residual
  artifact in the *observer itself* is the prime suspect → Tier 3 to localise it.
- **Both arms elevated:** shared PRNG/instrumentation artifact → debug the harness.

Only a Tier-2 hardware run can turn an elevation into evidence *for the mechanism*.

---

## Files

- `src/fid_interferometer.py` — `observe`/`survival` primitives (authoritative logging)
- `src/experiment.py` — `control` arm + `aggregate`
- `src/analyze.py` — unified statistics
- `protocol/observer_prompt.md` — the exact COP prompt
- Run artifacts will live under `runs/<exp_id>/{observer,control}/trial_*.jsonl`

Nothing here runs until you approve the design.
