"""
Analyze v2 matched-pairs experiment results.
Loads control_trials from data/v2_control_trials.json
and observer_trials passed as argument or from data/v2_observer_trials.json
"""
import json, sys
from pathlib import Path

try:
    from scipy import stats
    import numpy as np
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("scipy not available; using manual calculations")


def geometric_z(trials, p_match=0.5):
    """z-score for observed mean vs geometric-null mean."""
    n = len(trials)
    mean = sum(trials) / n
    null_mean = p_match / (1 - p_match)  # = 1.0 for p=0.5
    null_var = p_match / (1 - p_match)**2  # = 2.0 for p=0.5
    se = (null_var / n) ** 0.5
    z = (mean - null_mean) / se
    return mean, z


def normal_pvalue(z):
    if HAS_SCIPY:
        return float(stats.norm.sf(abs(z)) * 2)
    # manual approximation (two-tailed)
    import math
    t = abs(z)
    # approximation: Abramowitz and Stegun 26.2.17
    p = 1 / (1 + 0.2316419 * t)
    poly = p * (0.319381530 + p * (-0.356563782 + p * (1.781477937 + p * (-1.821255978 + p * 1.330274429))))
    pdf = math.exp(-t*t/2) / math.sqrt(2*math.pi)
    return float(2 * pdf * poly)


def wilcoxon(obs, ctrl):
    if HAS_SCIPY:
        diffs = [o - c for o, c in zip(obs, ctrl)]
        nonzero = [d for d in diffs if d != 0]
        if not nonzero:
            return 1.0
        return float(stats.wilcoxon(nonzero).pvalue)
    return None


def sign_test(obs, ctrl):
    wins = sum(1 for o, c in zip(obs, ctrl) if o > c)
    losses = sum(1 for o, c in zip(obs, ctrl) if o < c)
    ties = sum(1 for o, c in zip(obs, ctrl) if o == c)
    n_effective = wins + losses
    if n_effective == 0:
        return wins, losses, ties, 1.0
    if HAS_SCIPY:
        p = float(stats.binom_test(min(wins, losses), n_effective, 0.5) if hasattr(stats, 'binom_test')
                  else stats.binomtest(min(wins, losses), n_effective, 0.5).pvalue)
    else:
        p = None
    return wins, losses, ties, p


def improbability_table(obs, ctrl, max_rounds=10):
    rows = []
    for k in range(0, max_rounds + 1):
        o_count = sum(1 for x in obs if x >= k)
        c_count = sum(1 for x in ctrl if x >= k)
        factor = 2**k
        rows.append((k, factor, o_count, len(obs), c_count, len(ctrl)))
    return rows


def main():
    # Load control
    ctrl_path = Path("data/v2_control_trials.json")
    ctrl_data = json.loads(ctrl_path.read_text())
    control = ctrl_data["control_trials"]

    # Load observer
    obs_path = Path("data/v2_observer_trials.json")
    if not obs_path.exists():
        print("ERROR: data/v2_observer_trials.json not found")
        sys.exit(1)
    obs_data = json.loads(obs_path.read_text())
    observer = obs_data["trials"]

    n = min(len(observer), len(control))
    observer = observer[:n]
    control = control[:n]

    print(f"\n{'='*65}")
    print(f"FID INTERFEROMETER v2 — MATCHED PAIRS ANALYSIS (N={n})")
    print(f"{'='*65}\n")

    obs_mean, obs_z = geometric_z(observer)
    ctrl_mean, ctrl_z = geometric_z(control)
    obs_p = normal_pvalue(obs_z)
    ctrl_p = normal_pvalue(ctrl_z)

    print(f"{'Metric':<35} {'Observer':<15} {'Control':<15}")
    print(f"{'-'*65}")
    print(f"{'N trials':<35} {n:<15} {n:<15}")
    print(f"{'Total rounds survived':<35} {sum(observer):<15} {sum(control):<15}")
    print(f"{'Mean rounds survived':<35} {obs_mean:<15.3f} {ctrl_mean:<15.3f}")
    print(f"{'Max rounds in one trial':<35} {max(observer):<15} {max(control):<15}")
    print(f"{'Max improbability factor':<35} {'2^'+str(max(observer))+'='+str(2**max(observer))+':1':<15} {'2^'+str(max(control))+'='+str(2**max(control))+':1':<15}")
    print(f"{'z vs null (mean=1.0)':<35} {obs_z:<15.3f} {ctrl_z:<15.3f}")
    print(f"{'p vs null (two-tailed)':<35} {obs_p:<15.3f} {ctrl_p:<15.3f}")

    print(f"\nPaired comparison:")
    diff = obs_mean - ctrl_mean
    print(f"  Mean difference: {diff:+.3f} rounds (observer - control)")

    w_p = wilcoxon(observer, control)
    if w_p is not None:
        print(f"  Wilcoxon signed-rank p: {w_p:.3f}")

    wins, losses, ties, s_p = sign_test(observer, control)
    print(f"  Sign test: {wins} obs wins, {losses} ctrl wins, {ties} ties", end="")
    if s_p is not None:
        print(f" (p={s_p:.3f})")
    else:
        print()

    print(f"\nImprobability factor table:")
    print(f"{'Rounds':>8} {'Factor':>10} {'Obs reaches':>14} {'Ctrl reaches':>14}")
    print(f"{'-'*50}")
    for k, factor, o_n, o_tot, c_n, c_tot in improbability_table(observer, control):
        if k > max(max(observer), max(control)) + 1:
            break
        print(f"  ≥{k:<6} {str(factor)+':1':>8}   {str(o_n)+'/'+str(o_tot):>10}   {str(c_n)+'/'+str(c_tot):>10}")

    print(f"\nPrimary result interpretation:")
    if obs_p < 0.05:
        print(f"  *** Observer SIGNIFICANT vs null (p={obs_p:.3f} < 0.05) ***")
    elif obs_p < 0.10:
        print(f"  Observer MARGINAL vs null (p={obs_p:.3f}, below 0.10 threshold)")
    else:
        print(f"  Observer NOT significant vs null (p={obs_p:.3f})")

    if ctrl_p >= 0.10:
        print(f"  Control at baseline (p={ctrl_p:.3f}), consistent with null")
    else:
        print(f"  Control also elevated (p={ctrl_p:.3f}) — shared elevation possible")

    if w_p is not None and w_p < 0.05:
        print(f"  *** Paired comparison: observer BEATS control (Wilcoxon p={w_p:.3f}) ***")
    elif w_p is not None:
        print(f"  Paired comparison: no systematic difference (Wilcoxon p={w_p:.3f})")

    # Save results
    result = {
        "experiment": "matched_pairs_v2",
        "n_pairs": n,
        "observer": {"trials": observer, "mean": obs_mean, "max": max(observer), "z": obs_z, "p_vs_null": obs_p},
        "control": {"trials": control, "mean": ctrl_mean, "max": max(control), "z": ctrl_z, "p_vs_null": ctrl_p},
        "paired": {"mean_diff": diff, "wilcoxon_p": w_p, "sign_wins": wins, "sign_losses": losses, "sign_ties": ties},
    }
    out_path = Path("results/matched_pairs_v2.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
