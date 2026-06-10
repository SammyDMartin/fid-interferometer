"""
FID Interferometer v3 — control arm + aggregation harness.

The OBSERVER arm is run by the Sub-Meson Brain spawning one fresh LLM sub-agent
per trial (see ../protocol/EXPERIMENT_V3_DESIGN.md). This script handles the two
parts that are pure code:

  control   run the matched PRNG control arm — no LLM, no observer — through the
            EXACT same `observe` logging primitive the observers use, so the two
            arms are instrumented identically (validity criterion C8).

  aggregate read every per-trial JSONL log from the observer dir and the control
            dir, derive authoritative survival counts from the logs (never from
            self-report), and run the unified analysis.

Trial logs are JSONL: one round per line, written by `fid_interferometer observe`.
Survival = consecutive MATCH rounds from the start before the first MISMATCH.

Usage:
    python src/experiment.py control  runs/<exp>/control 109 sim
    python src/experiment.py aggregate runs/<exp>/observer runs/<exp>/control "v3_sim" runs/<exp>/result.json
"""
import json
import random
import subprocess
import sys
from pathlib import Path

TOOLKIT = str(Path(__file__).with_name("fid_interferometer.py"))
MAX_ROUNDS = 10


def _observe(log_path, prediction, source):
    """Call the toolkit's authoritative observe primitive (one round)."""
    out = subprocess.run(
        [sys.executable, TOOLKIT, "observe", str(log_path), str(prediction), source],
        capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{") and "match" in line:
            return json.loads(line)
    return {"match": False}


def run_control(out_dir, n, source="sim"):
    """
    Run n control trials. Each trial: a NON-observer (random.randint) plays the
    comparison circuit round by round until its first mismatch (or MAX_ROUNDS),
    through the identical `observe` log path. One JSONL log per trial.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    survivals = []
    for t in range(1, n + 1):
        log = out_dir / f"trial_{t:03d}.jsonl"
        log.unlink(missing_ok=True)
        survived = 0
        for _ in range(MAX_ROUNDS):
            pred = random.randint(0, 1)          # no observer — pure PRNG
            res = _observe(log, pred, source)
            if res.get("match"):
                survived += 1
            else:
                break
        survivals.append(survived)
        if t % 10 == 0:
            print(f"  control {t}/{n} (last survived={survived})")
    (out_dir / "_survivals.json").write_text(json.dumps({"trials": survivals, "n": n}))
    print(f"control done: mean={sum(survivals)/len(survivals):.3f} max={max(survivals)} → {out_dir}")
    return survivals


def survival_from_log(log_path):
    """Consecutive MATCH rounds from the start before the first MISMATCH."""
    p = Path(log_path)
    if not p.exists() or not p.stat().st_size:
        return 0
    s = 0
    for line in p.open():
        line = line.strip()
        if not line:
            continue
        if json.loads(line).get("match"):
            s += 1
        else:
            break
    return s


def collect(trial_dir):
    """Authoritative survival counts from every trial_*.jsonl in a directory."""
    files = sorted(Path(trial_dir).glob("trial_*.jsonl"))
    return [survival_from_log(f) for f in files]


def aggregate(observer_dir, control_dir, label="v3", out=None):
    sys.path.insert(0, str(Path(__file__).parent))
    from analyze import analyze, print_report

    observer = collect(observer_dir)
    control = collect(control_dir)
    print(f"collected {len(observer)} observer + {len(control)} control trials (from logs)")
    r = analyze(observer, control, label=label)
    print_report(r)
    if out:
        Path(out).write_text(json.dumps(r, indent=2))
        print(f"\nsaved → {out}")
    return r


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "control":
        run_control(sys.argv[2], int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "sim")
    elif cmd == "aggregate":
        out = sys.argv[5] if len(sys.argv) > 5 else None
        aggregate(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "v3", out)
    else:
        print(__doc__)
