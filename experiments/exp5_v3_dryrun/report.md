# FID Experiment v3 — Tier-1 simulator dry-run report

**Plumbing dry-run on a simulator. NOT evidence for or against the FID hypothesis** — criterion C5 (real quantum branching) is unmet by construction. The only honest expectation here is a null.

- N per arm: **109** · max rounds: **10** · seed: 7 · coin: **aer** (real Aer comparison circuit, seeded)

## Criterion 1 — no skill channel (fairness verify)
P(match) = **0.49698** over 40,000 trials (chi^2 = 1.464); |P(match)-0.5| < 0.015 -> **PASS** (no exploitable skill channel).

## Result — observer vs control vs geometric null
- observer mean survival: **1.0092** (z vs null 0.068, p two-tailed 0.946)
- control mean survival:  **1.0** (z vs null 0.0, p two-tailed 1.0)
- geometric-null mean: **1.000**
- paired observer-vs-control: mean_diff +0.0092, Wilcoxon p 0.9382, sign 36-32-41

As expected for a non-branching simulator with honest accounting, observer and control are statistically indistinguishable and both sit on the null. The pipeline does not manufacture an effect.

## The counting artifact (why C8 is the whole game)
Counted naively (only lives that survived >=1 round 'filed a report'), the *same fair coins* report mean survival **2.03** and a reach-curve far above the null — a textbook improbability streak. Counted the v3 way (every life, including round-1 deaths), the mean is **1.00**, on the null. The artifact inflates survival **2.02x** out of nothing.

| round k | null 0.5^k | v3 reach | naive reach (artifact) |
|--------:|-----------:|---------:|-----------------------:|
| 1 | 0.5000 | 0.4954 | 1.0000 |
| 2 | 0.2500 | 0.2706 | 0.5463 |
| 3 | 0.1250 | 0.1514 | 0.3056 |
| 4 | 0.0625 | 0.0596 | 0.1204 |
| 5 | 0.0312 | 0.0183 | 0.0370 |
| 6 | 0.0156 | 0.0046 | 0.0093 |
| 7 | 0.0078 | 0.0046 | 0.0093 |
| 8 | 0.0039 | 0.0000 | 0.0000 |
| 9 | 0.0020 | 0.0000 | 0.0000 |
| 10 | 0.0010 | 0.0000 | 0.0000 |

This is the day-9 bug from `logs/log-1.txt`, reproduced on demand and shown to vanish under log-derived accounting. It is the most important thing a dry-run can establish before spending hardware time.

## What this licenses
- ✅ The v3 plumbing runs end to end and is internally consistent.
- ✅ With C8 accounting, no spurious observer>control effect appears.
- ✅ The artifact behind the historical p=0.057 is reproduced and killed.
- ❌ Nothing here tests the hypothesis (no branching, C5). The headline claim still requires Tier-2 hardware with a genuine pruned observer.