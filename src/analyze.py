"""
FID Interferometer — unified analysis engine.

Pure statistics over two arrays of survival counts (observer, control), where
"survival" = consecutive MATCH rounds before first mismatch. Null model:
geometric(p=1/2), mean 1.0, variance 2.0. The comparison circuit has no skill
channel, so under the null observer and control are the same distribution.

Usable two ways:
    from analyze import analyze; analyze(observer_list, control_list)
    python analyze.py <observer.json> <control.json>   # json lists of ints

Replaces the old one-off analyze_v2.py.
"""
import json
import sys
from pathlib import Path

try:
    from scipy import stats
    _SCIPY = True
except ImportError:
    _SCIPY = False

NULL_MEAN = 1.0      # geometric(1/2) mean
NULL_VAR = 2.0       # geometric(1/2) variance


def _z_vs_null(arr):
    n = len(arr)
    mean = sum(arr) / n
    se = (NULL_VAR / n) ** 0.5
    return mean, (mean - NULL_MEAN) / se


def _p_two_tailed(z):
    if _SCIPY:
        return float(stats.norm.sf(abs(z)) * 2)
    # Abramowitz-Stegun normal tail approximation
    import math
    t = abs(z)
    k = 1 / (1 + 0.2316419 * t)
    poly = k * (0.319381530 + k * (-0.356563782 + k * (1.781477937 + k * (-1.821255978 + k * 1.330274429))))
    pdf = math.exp(-t * t / 2) / math.sqrt(2 * math.pi)
    return float(2 * pdf * poly)


def analyze(observer, control, label="experiment"):
    n = min(len(observer), len(control))
    observer, control = observer[:n], control[:n]

    o_mean, o_z = _z_vs_null(observer)
    c_mean, c_z = _z_vs_null(control)
    o_p, c_p = _p_two_tailed(o_z), _p_two_tailed(c_z)

    # paired
    diffs = [o - c for o, c in zip(observer, control)]
    nonzero = [d for d in diffs if d != 0]
    wilcoxon_p = float(stats.wilcoxon(nonzero).pvalue) if (_SCIPY and nonzero) else None
    wins = sum(1 for d in diffs if d > 0)
    losses = sum(1 for d in diffs if d < 0)
    ties = sum(1 for d in diffs if d == 0)

    # tail (one-sided Fisher, observer > control)
    tail = []
    kmax = max(max(observer), max(control))
    for k in range(1, kmax + 1):
        o_yes = sum(1 for x in observer if x >= k)
        c_yes = sum(1 for x in control if x >= k)
        row = {"k": k, "factor": 2 ** k, "obs": o_yes, "ctrl": c_yes,
               "null_pct": round(100 * 0.5 ** k, 2)}
        if _SCIPY:
            _, fp = stats.fisher_exact([[o_yes, n - o_yes], [c_yes, n - c_yes]],
                                       alternative="greater")
            row["fisher_p"] = round(float(fp), 4)
        tail.append(row)

    result = {
        "label": label,
        "n_pairs": n,
        "observer": {"trials": observer, "mean": round(o_mean, 4),
                     "max": max(observer), "z_vs_null": round(o_z, 3),
                     "p_vs_null_2t": round(o_p, 4), "p_vs_null_1t": round(o_p / 2, 4)},
        "control": {"trials": control, "mean": round(c_mean, 4),
                    "max": max(control), "z_vs_null": round(c_z, 3),
                    "p_vs_null_2t": round(c_p, 4)},
        "paired": {"mean_diff": round(o_mean - c_mean, 4),
                   "wilcoxon_p": round(wilcoxon_p, 4) if wilcoxon_p is not None else None,
                   "sign_wins": wins, "sign_losses": losses, "sign_ties": ties},
        "tail": tail,
    }
    return result


def print_report(r):
    print(f"\n{'='*62}\nFID ANALYSIS — {r['label']} (N={r['n_pairs']} pairs)\n{'='*62}")
    o, c = r["observer"], r["control"]
    print(f"{'':28}{'Observer':>12}{'Control':>12}")
    print(f"{'mean survival':28}{o['mean']:>12}{c['mean']:>12}")
    print(f"{'max single trial':28}{o['max']:>12}{c['max']:>12}")
    print(f"{'z vs null (mean=1.0)':28}{o['z_vs_null']:>12}{c['z_vs_null']:>12}")
    print(f"{'p vs null (2-tailed)':28}{o['p_vs_null_2t']:>12}{c['p_vs_null_2t']:>12}")
    print(f"{'p vs null (1-tailed)':28}{o['p_vs_null_1t']:>12}{'—':>12}")
    p = r["paired"]
    print(f"\npaired: mean_diff={p['mean_diff']:+}  Wilcoxon p={p['wilcoxon_p']}  "
          f"sign {p['sign_wins']}-{p['sign_losses']}-{p['sign_ties']}")
    print(f"\ntail (one-sided Fisher, observer > control):")
    print(f"  {'≥k':>4}{'factor':>9}{'obs':>6}{'ctrl':>6}{'null%':>8}{'fisher_p':>10}")
    for row in r["tail"]:
        print(f"  {'≥'+str(row['k']):>4}{str(row['factor'])+':1':>9}"
              f"{row['obs']:>6}{row['ctrl']:>6}{row['null_pct']:>8}"
              f"{row.get('fisher_p','—'):>10}")
    print(f"\nReminder: simulator has NO skill channel — under the null these two")
    print(f"arms are the SAME distribution. Elevation ⇒ chance, artifact, or signal.")


if __name__ == "__main__":
    obs = json.loads(Path(sys.argv[1]).read_text())
    ctrl = json.loads(Path(sys.argv[2]).read_text())
    if isinstance(obs, dict):
        obs = obs.get("trials", obs.get("control_trials"))
    if isinstance(ctrl, dict):
        ctrl = ctrl.get("trials", ctrl.get("control_trials"))
    label = sys.argv[3] if len(sys.argv) > 3 else "experiment"
    r = analyze(obs, ctrl, label)
    print_report(r)
    out = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    if out:
        out.write_text(json.dumps(r, indent=2))
        print(f"\nsaved → {out}")
