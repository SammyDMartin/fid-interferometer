# Simulation Substrate Probe

A White-interferometer-class test of one specific, falsifiable reading of the
simulation hypothesis. The second ontological-engineering proposal (after the
FID) to survive the codeability audit (`../../docs/ontological-engineering/CODEABILITY_AUDIT.md`)
and become a real, runnable, weak experiment.

## The inference (every step is "therefore", not "is like")

1. **Premise (Bostrom).** We may be in a simulation on finite computational
   resources.
2. **Premise.** A finite process emitting a "random" number for every quantum
   event must use either a finite entropy budget or a pseudo-random generator —
   both of **finite algorithmic complexity**. True hardware randomness is
   expensive; a galaxy-scale simulation economises.
3. **Therefore.** If our quantum randomness comes from the parent simulation's
   generator, a bit-stream sampled from a QPU has finite algorithmic complexity —
   given enough samples it is compressible / periodic / structured.
4. **Contrast.** Standard quantum mechanics says measurement randomness is
   **irreducible**: incompressible, no generator, no structure. This is exactly
   what loophole-free Bell tests certify (Hensen et al. 2015; device-independent
   randomness).

**Observable:** statistical structure in genuine quantum bits — bias, serial
correlation, spectral peaks, block-entropy deficit, compressibility, runs.
**Null:** no structure (standard QM). **A detection** would be evidence that
quantum randomness has a finite-complexity generator — a computational substrate.

## Honest asymmetry (the White-Juday relationship)

- A **null refutes nothing**: the simulators could use their own *true*-random
  source, leaving our bits irreducibly random even though we are simulated. This
  probe tests only the narrow sub-hypothesis **"simulation with a detectably-weak
  RNG for quantum events."**
- A **strong, replicated positive** in certified-quantum bits would be
  extraordinary — the tabletop shadow of device-independent randomness
  certification.
- It is **underpowered by design**: subtle structure needs ≫10⁶ bits; the free
  QPU tier gives ~10⁴–10⁵. A null is uninformative. Only a large, replicated
  positive matters. This *is* the White interferometer's epistemic position.

## Apparatus characterization (does the instrument detect structure?)

Before trusting a null, the battery was characterized for both false-positive
rate and sensitivity. The verdict uses a **family-wise (Šidák) corrected** p
across the independent tests, so running several tests does not manufacture
significance.

| Input stream | n | Verdict | Meaning |
|---|---|---|---|
| OS true randomness (`secrets`) | 20000 ×20 runs | **0/20 false positives** | calibrated null ✓ |
| Period-8 pattern | 20000 | **flagged** (fw p≈0, lag=4) | catches periodicity ✓ |
| Period-16 pattern | 20000 | **flagged** (fw p≈0) | catches periodicity ✓ |
| 60% bias | 20000 | **flagged** (fw p≈0) | catches bias ✓ |
| Weak LCG (low bit) | 20000 | **flagged** (fw p≈0, lag=8) | catches a weak generator ✓ |
| Mersenne Twister | 20000 | **null** (fw p≈0.37) | a *good* PRNG passes |
| IBM Kingston quantum | 100 | **null** (fw p=0.118) | underpowered, as expected |

**Resolution limit (stated honestly):** the probe reliably catches bias,
periodicity, low block-entropy, and crude/weak generators, but **not** a
cryptographic PRNG (Mersenne and stronger pass as null). So a simulator using a
strong CSPRNG for quantum events would pass undetected — just as White's
interferometer could not resolve a real warp field. The probe meaningfully tests
only the *detectably-weak-generator* corner of the simulation hypothesis. That
narrowness is the honest scope, not a hidden caveat.

Battery: monobit (bias), NIST runs, 4- and 8-bit block entropy, zlib
compressibility, and a multi-lag autocorrelation scan (catches any period up to
lag 256, Šidák-corrected for the scan).

## Files

- `substrate_probe.py` — pure analysis battery. `python substrate_probe.py <bits.json> [label] [out.json]`
- `harvest_bits.py` — bulk bit harvester via the IBM relay (one H-circuit × N shots
  = N genuine bits for ~seconds of QPU). `request` writes the relay request;
  `run` (executed by the relay) pulls the bits. Triggering a harvest spends QPU
  budget and is left to a deliberate decision — not run automatically.
- `result_kingston_n100.json` — first weak pass on the 100 bits already on hand.

## Status

First pass on n=100 genuine IBM Kingston bits: **NULL** (expected; far too few
bits — entropy and compressibility tests can't even run). To do a real (still
weak) pass: harvest ~10⁵ bits via `harvest_bits.py request 100000` → push →
analyse. Almost certainly null. That is the point.
