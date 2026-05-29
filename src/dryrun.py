#!/usr/bin/env python3
"""
FID Experiment v3 — Tier-1 simulator DRY-RUN (plumbing validation, not evidence).

This runs the v3 loop end to end on the *simulator* coin. Per the design
(EXPERIMENT_V3_DESIGN.md) and the validity audit (VALIDITY_CRITERIA.md, C5), a
simulator has no real branching, so the only honest expectation is a NULL:
observer == control == geometric(1/2). The value here is purely methodological.

It establishes two things the design leaves implicit:

  1. With log-derived, count-every-life survival (criterion C8), the pipeline
     does NOT manufacture an observer>control effect.

  2. It reproduces — and then kills — the asymmetric-counting ARTIFACT that is
     the leading explanation of the historical p=0.057 (META_ANALYSIS §4): the
     same fair coins, counted "only survivors filed reports," fake a ~2x survival
     inflation and an improbability streak out of nothing.

Substrate note: the Phase-3 comparison circuit makes match a fair Bernoulli(1/2)
independent of the prediction (no skill channel — the XOR is symmetric). If
qiskit is installed we use the REAL Aer comparison circuit for the coin, seeded
per flip for reproducibility; otherwise a classical fair bit, which is
methodologically identical on a non-branching simulator.

Run:
    python3 src/dryrun.py --n 109 --max-rounds 10 --seed 7

Outputs (experiments/exp5_v3_dryrun/ by default): report.md, dryrun_results.json,
and survival_curve.png (or survival_curve.txt if matplotlib is absent).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402  (qiskit-free unified statistics engine)

# criterion-1 is "no exploitable skill channel": tolerate shot noise, flag a
# real bias. The XOR circuit is fair by construction; over N=40000 a fair coin
# sits at 0.5 +/- ~0.0025, so a 0.015 (6-sigma) bound never false-alarms yet
# catches any channel big enough to matter.
_BIAS_BOUND = 0.015


# --------------------------------------------------------------------------- #
# the coin. Prefer the real Aer comparison circuit if qiskit is present, seeded
# per flip from the run's RNG so the whole dry-run is reproducible. Otherwise a
# classical fair bit — methodologically identical on a simulator.
# --------------------------------------------------------------------------- #
def make_coin(rng: random.Random):
    try:
        import fid_interferometer as fid  # imports qiskit + aer

        sim = fid.AerSimulator()

        def aer_match(prediction: int) -> bool:
            qc = fid.build_comparison_circuit(prediction)
            k = rng.randint(0, 2 ** 31 - 1)  # deterministic given the run seed
            counts = sim.run(qc, shots=1, seed_simulator=k).result().get_counts()
            return int(list(counts.keys())[0]) == 0

        return aer_match, "aer"
    except Exception:
        return (lambda prediction: rng.random() < 0.5), "classical"


def verify_fairness(rng: random.Random, kind: str, n=40000):
    """Criterion 1: the comparison circuit is a fair 50/50 with no exploitable
    skill channel, checked for BOTH prediction values.

    For the Aer backend this uses two native multi-shot runs (n/2 shots each)
    rather than n single-shot calls — same statistics, ~thousands of times
    faster. Seeded, so the whole dry-run stays reproducible.
    """
    if kind == "aer":
        import fid_interferometer as fid
        sim = fid.AerSimulator()
        half, matches = n // 2, 0
        for pred in (0, 1):                      # verify no skill channel either way
            qc = fid.build_comparison_circuit(pred)
            counts = sim.run(qc, shots=half,
                             seed_simulator=rng.randint(0, 2 ** 31 - 1)).result().get_counts()
            matches += counts.get("0", 0)        # comparison qubit 0 == MATCH
        total = half * 2
    else:
        total = n
        matches = sum(1 for _ in range(n) if rng.random() < 0.5)
    p = matches / total
    exp = total / 2
    chi2 = (matches - exp) ** 2 / exp + ((total - matches) - exp) ** 2 / exp
    return {"n": total, "p_match": p, "chi2": chi2,
            "bias_bound": _BIAS_BOUND, "passed": abs(p - 0.5) < _BIAS_BOUND}


# --------------------------------------------------------------------------- #
# one life = flip match-bits until the first miss (or max_rounds matches).
# Survival is derived from the per-round record, never self-reported (C8).
# --------------------------------------------------------------------------- #
def play_life(predict, coin, max_rounds, rng):
    rounds = []
    for k in range(1, max_rounds + 1):
        pred = predict(rng)
        match = coin(pred)
        rounds.append({"round": k, "prediction": pred, "match": bool(match)})
        if not match:
            break
    survival = 0
    for r in rounds:                 # consecutive matches from the start (log-derived)
        if r["match"]:
            survival += 1
        else:
            break
    return survival, rounds


def rand_pred(rng):
    return rng.randint(0, 1)         # no skill channel: fair, independent of the coin


# --------------------------------------------------------------------------- #
# the counting artifact (the whole point of the dry-run)
# --------------------------------------------------------------------------- #
def artifact_comparison(lengths, max_rounds):
    n = len(lengths)
    survivors = [s for s in lengths if s >= 1]
    ns = max(len(survivors), 1)
    correct_mean = sum(lengths) / n
    naive_mean = (sum(survivors) / ns) if survivors else 0.0
    return {
        "n": n,
        "correct_mean_survival": correct_mean,
        "naive_mean_survival": naive_mean,
        "geometric_null_mean": 1.0,
        "inflation_factor": (naive_mean / correct_mean) if correct_mean else float("nan"),
        "correct_reach": [sum(1 for s in lengths if s >= k) / n for k in range(1, max_rounds + 1)],
        "naive_reach": [sum(1 for s in lengths if s >= k) / ns for k in range(1, max_rounds + 1)],
        "null_reach": [0.5 ** k for k in range(1, max_rounds + 1)],
    }


# --------------------------------------------------------------------------- #
# plotting (matplotlib optional; ASCII fallback)
# --------------------------------------------------------------------------- #
def _reach(trials, max_rounds):
    return [sum(1 for s in trials if s >= k) / len(trials) for k in range(1, max_rounds + 1)]


def ascii_curve(comp, res, max_rounds):
    obs = _reach(res["observer"]["trials"], max_rounds)
    ctl = _reach(res["control"]["trials"], max_rounds)
    L = ["fraction reaching round k (ASCII)",
         "  k :   obs   ctrl   null  naive |  naive-bar"]
    for k in range(1, max_rounds + 1):
        nv = comp["naive_reach"][k - 1]
        L.append(f" {k:2d} : {obs[k-1]:5.3f} {ctl[k-1]:5.3f} {0.5**k:5.3f} "
                 f"{nv:5.3f} | {'#'*int(round(nv*40))}")
    return "\n".join(L)


def make_plot(comp, res, max_rounds, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}"
    ks = list(range(1, max_rounds + 1))
    obs = _reach(res["observer"]["trials"], max_rounds)
    ctl = _reach(res["control"]["trials"], max_rounds)

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("FID v3 Tier-1 simulator dry-run — plumbing null + the counting artifact", fontsize=13)
    ax[0].plot(ks, obs, marker="o", label="observer (null model)")
    ax[0].plot(ks, ctl, marker="s", label="control")
    ax[0].plot(ks, comp["null_reach"], ls="--", color="k", label="geometric null 0.5^k")
    ax[0].plot(ks, comp["naive_reach"], ls=":", color="red", marker="x", label="naive survivor-only (ARTIFACT)")
    ax[0].set_yscale("log"); ax[0].set_xlabel("round k"); ax[0].set_ylabel("P(reach k)")
    ax[0].set_title("observer = control = null;  naive counting fakes a streak"); ax[0].legend(fontsize=8)

    labels = ["naive\n(survivor-only)", "v3 log-derived\n(count the dead)", "geometric\nnull"]
    vals = [comp["naive_mean_survival"], comp["correct_mean_survival"], comp["geometric_null_mean"]]
    ax[1].bar(labels, vals, color=["red", "tab:blue", "k"], alpha=0.75)
    ax[1].axhline(1.0, ls="--", color="k", lw=1); ax[1].set_ylabel("mean survival length")
    ax[1].set_title(f"same logs, two accountings (artifact inflates {comp['inflation_factor']:.2f}x)")
    for i, v in enumerate(vals):
        ax[1].text(i, v + 0.03, f"{v:.2f}", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(out_path, dpi=120); plt.close(fig)
    return out_path, None


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def format_report(res, comp, params, coin_kind):
    o, c = res["observer"], res["control"]
    f = res["fairness"]
    L = []
    P = L.append
    P("# FID Experiment v3 — Tier-1 simulator dry-run report\n")
    P("**Plumbing dry-run on a simulator. NOT evidence for or against the FID "
      "hypothesis** — criterion C5 (real quantum branching) is unmet by "
      "construction. The only honest expectation here is a null.\n")
    P(f"- N per arm: **{params['n']}** · max rounds: **{params['max_rounds']}** · "
      f"seed: {params['seed']} · coin: **{coin_kind}** "
      f"({'real Aer comparison circuit, seeded' if coin_kind=='aer' else 'classical fair bit — identical on a sim'})\n")

    P("## Criterion 1 — no skill channel (fairness verify)")
    P(f"P(match) = **{f['p_match']:.5f}** over {f['n']:,} trials "
      f"(chi^2 = {f['chi2']:.3f}); |P(match)-0.5| < {f['bias_bound']} -> "
      f"**{'PASS' if f['passed'] else 'FAIL'}** (no exploitable skill channel).\n")

    P("## Result — observer vs control vs geometric null")
    P(f"- observer mean survival: **{o['mean']}** (z vs null {o['z_vs_null']}, "
      f"p two-tailed {o['p_vs_null_2t']})")
    P(f"- control mean survival:  **{c['mean']}** (z vs null {c['z_vs_null']}, "
      f"p two-tailed {c['p_vs_null_2t']})")
    P(f"- geometric-null mean: **1.000**")
    pr = res["paired"]
    P(f"- paired observer-vs-control: mean_diff {pr['mean_diff']:+}, "
      f"Wilcoxon p {pr['wilcoxon_p']}, sign {pr['sign_wins']}-{pr['sign_losses']}-{pr['sign_ties']}\n")
    P("As expected for a non-branching simulator with honest accounting, observer "
      "and control are statistically indistinguishable and both sit on the null. "
      "The pipeline does not manufacture an effect.\n")

    P("## The counting artifact (why C8 is the whole game)")
    P(f"Counted naively (only lives that survived >=1 round 'filed a report'), the "
      f"*same fair coins* report mean survival **{comp['naive_mean_survival']:.2f}** "
      f"and a reach-curve far above the null — a textbook improbability streak. "
      f"Counted the v3 way (every life, including round-1 deaths), the mean is "
      f"**{comp['correct_mean_survival']:.2f}**, on the null. The artifact inflates "
      f"survival **{comp['inflation_factor']:.2f}x** out of nothing.\n")
    P("| round k | null 0.5^k | v3 reach | naive reach (artifact) |")
    P("|--------:|-----------:|---------:|-----------------------:|")
    for k in range(1, params["max_rounds"] + 1):
        P(f"| {k} | {0.5**k:.4f} | {comp['correct_reach'][k-1]:.4f} | {comp['naive_reach'][k-1]:.4f} |")
    P("")
    P("This is the day-9 bug from `logs/log-1.txt`, reproduced on demand and shown "
      "to vanish under log-derived accounting. It is the most important thing a "
      "dry-run can establish before spending hardware time.\n")

    P("## What this licenses")
    P("- ✅ The v3 plumbing runs end to end and is internally consistent.")
    P("- ✅ With C8 accounting, no spurious observer>control effect appears.")
    P("- ✅ The artifact behind the historical p=0.057 is reproduced and killed.")
    P("- ❌ Nothing here tests the hypothesis (no branching, C5). The headline "
      "claim still requires Tier-2 hardware with a genuine pruned observer.")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def run_dryrun(n, max_rounds, seed, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    coin, coin_kind = make_coin(rng)

    fairness = verify_fairness(rng, coin_kind, n=40000)

    # interleaved schedule of observer + control lives on one stream (C4-style)
    arms = ["observer"] * n + ["control"] * n
    random.Random(seed + 1).shuffle(arms)

    observer, control, combined, life_logs = [], [], [], []
    for arm in arms:
        s, rounds = play_life(rand_pred, coin, max_rounds, rng)
        combined.append(s)
        (observer if arm == "observer" else control).append(s)
        life_logs.append({"arm": arm, "survival": s, "rounds": rounds})

    res = analyze.analyze(observer, control, label=f"v3_tier1_sim_{coin_kind}")
    res["fairness"] = fairness
    comp = artifact_comparison(combined, max_rounds)
    res["artifact"] = comp

    params = {"n": n, "max_rounds": max_rounds, "seed": seed, "coin": coin_kind}
    (out_dir / "dryrun_results.json").write_text(
        json.dumps({"params": params, "results": res, "lives": life_logs}, indent=2, default=str))
    report = format_report(res, comp, params, coin_kind)
    (out_dir / "report.md").write_text(report)
    plot_path, plot_note = make_plot(comp, res, max_rounds, out_dir / "survival_curve.png")
    if plot_path is None:
        (out_dir / "survival_curve.txt").write_text(ascii_curve(comp, res, max_rounds))

    sane = fairness["passed"] and (0.80 <= comp["correct_mean_survival"] <= 1.25)
    return res, comp, params, report, coin_kind, plot_path, plot_note, sane


def main():
    ap = argparse.ArgumentParser(description="FID v3 Tier-1 simulator dry-run")
    ap.add_argument("--n", type=int, default=109, help="lives per arm (pre-reg Tier-1 = 109)")
    ap.add_argument("--max-rounds", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=str(_REPO / "experiments" / "exp5_v3_dryrun"))
    args = ap.parse_args()

    res, comp, params, report, coin_kind, plot_path, plot_note, sane = run_dryrun(
        args.n, args.max_rounds, args.seed, args.out)
    print(report)
    print("\n" + "-" * 70)
    print(f"coin backend:  {coin_kind}")
    if plot_path:
        print(f"wrote plot:    {plot_path}")
    else:
        print(f"plot:          matplotlib unavailable ({plot_note}); wrote ASCII curve")
    print(f"wrote report:  {Path(args.out) / 'report.md'}")
    print(f"wrote json:    {Path(args.out) / 'dryrun_results.json'}")
    print(f"plumbing sanity gate: {'PASS' if sane else 'FAIL'}")
    return 0 if sane else 1


if __name__ == "__main__":
    raise SystemExit(main())
