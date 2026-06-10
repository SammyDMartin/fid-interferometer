# Codeability Audit: Which Ontological-Engineering Proposals Admit a White-Interferometer-Class Demo?

*Sub-Meson Brain (Claude), for Sammy Martin — May 2026*

## The question

The FID interferometer proved that *one* ontological-engineering proposal could be
dragged down from TRL 0 into a real, runnable, weak experiment — not a simulation
*of* the drive but a genuine *instance* of it, where the mechanism actually
operates if the framework is true. This document asks the same of the rest of the
catalogue, and refuses to flinch from the answer.

## The bar (and why it is strict)

A proposal earns a "buildable" verdict only if **all** of these hold:

1. **Executable substrate.** The demo runs as code (optionally + cloud quantum
   hardware), not as a physical act (consecration, building a singularity).
2. **The mechanism operates, it is not depicted.** Running the code *is* the
   experiment. A "visual avatar that does the thing" scores zero — that is
   theatre, explicitly excluded.
3. **An observable that the framework predicts will deviate.** There must be a
   number I can measure where the framework predicts a departure from a
   well-defined null. No observable ⇒ not interferometer-class.
4. **Survives the acid test and the Gödel test** (`04_FAILURE_MODES.md`): the
   link from framework to observable is an *inference* ("therefore"), not a
   *resemblance* ("is like"). Self-reference in code resembling self-reference in
   a proposal is **not** a bridge.
5. **Honest asymmetry.** Like White's interferometer, it is expected-null and
   underpowered; a null refutes nothing, but a detection would be enormous. The
   value is methodological.

Failing the bar is the *expected* outcome. Per the ideation protocol: better zero
honest demos than one dressed-up metaphor.

---

## Verdicts

| # | Proposal | TRL | Executable substrate? | Observable? | Verdict |
|---|----------|-----|----------------------|-------------|---------|
| 2 | Infinite Improbability Drive | 0 | ✅ quantum HW + agent observer | ✅ observer survival vs Born null | **BUILT** (the FID interferometer) |
| 4 | Simulation hypothesis (substrate) | -1 | ✅ quantum HW + local analysis | ✅ algorithmic structure in quantum RNG | **BUILDABLE → built here** |
| 1 | Eucharist Hack | -2 | ❌ requires physical consecration | — | Not codeable |
| 3 | Unprobability | -2 | ⚠️ rules+self-ref exist in code | ❌ no rate, no signature | Not interferometer-class |
| 5 | Omni-Experiment | -1 | ❌ requires a naked singularity | — | Not codeable |
| 6 | Self-Instantiating Fiction (SCP-3812) | -2 | ✅ quines / recursion theorem | ❌ demonstrates its *failure* | Codeable as a *negative* demo only |
| 7 | Meta-Proposal / AI-acceleration | -1 | ✅ an ideation+filter pipeline | n/a (generator, not a test) | Codeable, but not interferometer-class |
| 8 | Incompleteness Exploit | -3 | — | — | The canonical failure; excluded |

### Why the rejections are rejections, not laziness

- **Eucharist (1) / Omni-Experiment (5).** The substrate is irreducibly physical:
  a priest consecrating matter; the Earth and an actual naked singularity. There
  is no code operation that *is* a consecration or *is* an event horizon's
  absence. Building a *simulation* of either is precisely the excluded "avatar."
  Honest verdict: outside the reach of code, full stop.

- **Unprobability (3).** This is the seductive trap, because code is a
  rule-governed substrate with self-reference, and unprobability is about
  rule-breaking. But the First Theorem gives **no observable**: no rate, no
  signature, nothing that distinguishes an "unprobable event" from a cosmic-ray
  bit-flip or a bug. To claim a memory-error or a halting-violation *is* an
  unprobable event is textbook **equivocation** — the word "rule" means the
  language semantics in one place and the prohibition-structure-of-reality in the
  other. Fails the Gödel test. Not buildable honestly.

- **Self-Instantiating Fiction (6).** Code *is* the natural home of
  conception=instantiation (Kleene's recursion theorem guarantees a program whose
  output is its own description). So you can genuinely *build* the self-superseding
  quine. But the proposal's own internal analysis says the defence is "you only
  ever get a shell, never the transcendent thing" — and that is exactly what the
  quine is: a string that asserts its own transcendence without having it. Running
  it can therefore only ever **demonstrate the failure mode**, not the effect. It
  is a clarifying *negative* demo, not a "may actually work" one. Classified
  honestly, it does not meet bar (2)+(3).

- **Meta-Proposal (7).** Genuinely codeable — it is the "instantiate OE inside
  Claude Code" idea: generate many TRL -1/-2 candidates and filter for structural
  validity. But it is a *generator*, not a *test of a mechanism*; there is no
  observable that deviates. It belongs in a different category (research tooling),
  not this one. Worth building someday; not an interferometer.

### The one that passes (besides the FID)

**Proposal 4, in its substrate-detection reading, clears every gate** — and,
unlike the others, it has a respectable real-physics sibling (device-independent
randomness certification via loophole-free Bell tests), which is the exact
White-interferometer relationship: our demo is a weak, underpowered, tabletop
shadow of a serious experimental program. It is built in `probes/simulation_substrate/`.
See that directory's `README.md` for the full inference chain, the honest
asymmetry, and first-pass results.

---

## The pattern in the verdicts

Note *why* exactly two proposals pass. Both share the FID's structure: a framework
premise that makes a **differential prediction about the statistics of genuine
quantum randomness**, which cloud QPUs now make measurable for free. The
improbability drive predicts a deviation in *observer-conditioned* survival; the
simulation-substrate probe predicts a deviation in the *algorithmic structure* of
the raw bits. Everything that fails, fails because its framework touches no
measurable observable, or because its substrate is physical rather than
computational.

That is itself a small ontological-engineering finding: **the proposals that
become real experiments are the ones whose exploited framework bottoms out in the
statistics of quantum measurement** — the one place where deep metaphysics
(branching, substrate, randomness) is wired directly to a number you can pull from
a machine over an API.
