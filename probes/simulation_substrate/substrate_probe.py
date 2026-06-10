"""
Simulation Substrate Probe — a White-interferometer-class test of one specific,
falsifiable reading of the simulation hypothesis.

THE INFERENCE (not an analogy — each step is "therefore"):

  Premise 1 (Bostrom). We may be in a simulation run on finite computational
            resources.
  Premise 2. A finite computational process that must emit "random" numbers for
            every quantum event either (a) draws from a finite entropy budget or
            (b) uses a pseudo-random generator — both of which have FINITE
            algorithmic complexity. (True hardware randomness is expensive; a
            galaxy-scale sim economises.)
  Therefore. IF our universe's quantum randomness is produced by the parent
            simulation's generator, the bit-stream we sample from a QPU has finite
            algorithmic complexity — it is, given enough samples, compressible /
            structured / periodic.
  Contrast. Standard quantum mechanics says quantum measurement randomness is
            IRREDUCIBLE: incompressible, no algorithmic generator, no structure.
            (This is what loophole-free Bell tests certify experimentally.)

  OBSERVABLE: statistical structure in a large stream of genuine quantum bits —
            bias, serial correlation, spectral peaks, block-entropy deficit,
            compressibility, and the NIST-style randomness battery.
  NULL: no structure (standard QM). Expected. Almost certainly what we see.
  A DETECTION would be evidence that quantum randomness has a finite-complexity
            generator — i.e. a computational substrate.

HONEST ASYMMETRY (the White-Juday relationship):
  - A NULL refutes nothing: the simulators could use their OWN true-random source,
    in which case our bits are irreducibly random even though we ARE simulated.
    This probe tests the narrow sub-hypothesis "simulation with an algorithmic /
    finite-entropy RNG for quantum events", not simulation-in-general.
  - A POSITIVE (real, replicated structure in certified-quantum bits) would be
    extraordinary — the tabletop shadow of device-independent randomness
    certification.
  - It is UNDERPOWERED on the free tier (~10^4-10^5 bits). That is the point.

This module is pure analysis: feed it a list/bitstring of quantum bits.
Companion `pull_bits.py` requests a large fresh sample via the IBM relay.
"""
import json
import math
import sys
import zlib
from collections import Counter
from pathlib import Path


# ----------------------------------------------------------------------
# Individual tests. Each returns a dict with a statistic and, where a clean
# null distribution exists, a p-value. Small p = surprising under "irreducibly
# random" null = (weak) hint of structure = (weaker still) hint of a generator.
# ----------------------------------------------------------------------

def _phi(z):
    return 0.5 * math.erfc(-z / math.sqrt(2))


def test_monobit(bits):
    """Frequency (monobit) test. Excess of 0s or 1s."""
    n = len(bits)
    s = sum(1 if b else -1 for b in bits)
    z = abs(s) / math.sqrt(n)
    p = math.erfc(z / math.sqrt(2))
    return {"test": "monobit", "ones": sum(bits), "n": n,
            "ones_frac": round(sum(bits) / n, 5), "z": round(z, 3),
            "p": round(p, 4)}


def test_runs(bits):
    """NIST runs test: too few/many alternations ⇒ structure."""
    n = len(bits)
    pi = sum(bits) / n
    if abs(pi - 0.5) >= (2 / math.sqrt(n)):   # precondition
        return {"test": "runs", "skipped": "fails monobit precondition"}
    vobs = 1 + sum(1 for i in range(1, n) if bits[i] != bits[i - 1])
    num = abs(vobs - 2 * n * pi * (1 - pi))
    den = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p = math.erfc(num / den)
    return {"test": "runs", "runs": vobs, "p": round(p, 4)}


def test_block_entropy(bits, block=8):
    """Empirical Shannon entropy of m-bit blocks vs the ideal m bits/block."""
    n = len(bits)
    m = block
    if n < m * 32:
        return {"test": "block_entropy", "skipped": "too few bits"}
    counts = Counter()
    for i in range(0, n - m + 1):
        counts[tuple(bits[i:i + m])] += 1
    total = sum(counts.values())
    H = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return {"test": "block_entropy", "block_bits": m,
            "entropy_per_block": round(H, 4), "ideal": m,
            "deficit": round(m - H, 4),
            "note": "deficit >> 0 (at large n) would indicate structure"}


def test_compressibility(bits):
    """
    Pack bits into bytes and try to compress. Truly random data is
    incompressible (ratio ~1.0). A finite-complexity generator's output,
    given enough of it, compresses (<1.0).
    """
    n = len(bits)
    ba = bytearray()
    for i in range(0, n - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        ba.append(byte)
    raw = bytes(ba)
    if len(raw) < 16:
        return {"test": "compressibility", "skipped": "too few bytes"}
    comp = zlib.compress(raw, 9)
    ratio = len(comp) / len(raw)
    return {"test": "compressibility", "bytes": len(raw),
            "zlib_ratio": round(ratio, 4),
            "note": "ratio < ~1.0 at large n would indicate structure "
                    "(zlib has overhead; only meaningful for large samples)"}


def test_lag_scan(bits, max_lag=256):
    """
    Scan serial autocorrelation over MANY lags and report the single strongest.
    A generator with period p (or any repeating structure) spikes at lag p, so
    this catches periodicity of any period up to max_lag. The per-lag z is ~N(0,1)
    under irreducible randomness; taking the max over L lags requires a
    multiple-comparison (Šidák) correction on the reported p-value. O(n·L), fast.
    """
    n = len(bits)
    L = min(max_lag, n // 4)
    if L < 2:
        return {"test": "lag_scan", "skipped": "too few bits"}
    x = [1 if b else -1 for b in bits]
    best = {"lag": None, "z": 0.0, "corr": 0.0}
    for k in range(1, L + 1):
        c = sum(x[i] * x[i + k] for i in range(n - k)) / (n - k)
        z = abs(c) * math.sqrt(n - k)
        if z > best["z"]:
            best = {"lag": k, "z": z, "corr": c}
    per_lag_p = math.erfc(best["z"] / math.sqrt(2))      # two-sided per-lag
    fwer_p = 1 - (1 - per_lag_p) ** L                    # Šidák over L lags
    return {"test": "lag_scan", "lags_scanned": L,
            "strongest_lag": best["lag"], "corr": round(best["corr"], 4),
            "z": round(best["z"], 3), "p": round(min(fwer_p, 1.0), 4),
            "note": "p is family-wise corrected for the lag scan; a spike at some "
                    "lag (esp. a period) ⇒ a repeating generator"}


def run_battery(bits, label="quantum_bits"):
    bits = [int(b) & 1 for b in bits]
    n = len(bits)
    results = {
        "label": label,
        "n_bits": n,
        "power_note": ("UNDERPOWERED — like White's interferometer. Subtle "
                       "structure needs >>1e6 bits; the free QPU tier gives "
                       "~1e4-1e5. A null here is uninformative; only a strong, "
                       "replicated positive matters."),
        "tests": [
            test_monobit(bits),
            test_runs(bits),
            test_block_entropy(bits, block=4),
            test_block_entropy(bits, block=8),
            test_compressibility(bits),
            test_lag_scan(bits),
        ],
    }
    # Each independent test that yields a p-value contributes to a family-wise
    # (Šidák) corrected headline, so the verdict accounts for running several
    # tests rather than cherry-picking the smallest raw p.
    ps = [t["p"] for t in results["tests"] if "p" in t]
    min_p = min(ps) if ps else None
    results["min_p_uncorrected"] = round(min_p, 4) if min_p is not None else None
    results["n_tests_with_p"] = len(ps)
    results["p_familywise"] = (round(1 - (1 - min_p) ** len(ps), 4)
                               if min_p is not None else None)
    results["verdict"] = _verdict(results)
    return results


def _verdict(r):
    fw = r["p_familywise"]
    n = r["n_bits"]
    if fw is None:
        return "insufficient data"
    if fw > 0.01:
        return (f"NULL (consistent with irreducible quantum randomness). "
                f"No substrate signature at n={n} (family-wise p={fw}). Expected.")
    return (f"Apparent structure: family-wise p={fw} across {r['n_tests_with_p']} "
            f"tests. At n={n} treat as a candidate fluke; it means something only "
            f"if it REPLICATES at much larger n on fresh certified-quantum bits.")


def _load_bits(path):
    p = Path(path)
    txt = p.read_text().strip()
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            for k in ("random_bits", "bits", "quantum_bits"):
                if k in obj:
                    return obj[k]
        if isinstance(obj, list):
            return obj
    except json.JSONDecodeError:
        pass
    return [int(c) for c in txt if c in "01"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python substrate_probe.py <bits.json|bitstring.txt> [label] [out.json]")
        sys.exit(1)
    bits = _load_bits(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) > 2 else "quantum_bits"
    res = run_battery(bits, label)
    print(json.dumps(res, indent=2))
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(json.dumps(res, indent=2))
        print(f"\nsaved → {sys.argv[3]}")
