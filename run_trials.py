"""
Run multiple full FID trials on the simulator to gather statistics.
Each trial: Phase 2 (up to 10 rounds) + Phase 3 (up to 10 rounds).
Simulates what the COP sub-agents would do (random predictions).
Records all data for visualization.
"""
import json, random, subprocess, sys
from pathlib import Path

def run_cmd(args):
    r = subprocess.run(
        ["python", "fid_interferometer.py"] + args,
        capture_output=True, text=True
    )
    return r.stdout.strip()

def parse_json(s):
    # Find the first JSON object in the output
    for line in s.split("\n"):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    return {}

N_TRIALS = 30

all_results = []

for trial in range(1, N_TRIALS + 1):
    # Init log
    out = run_cmd(["init_log", "simulator"])
    log_info = parse_json(out)
    log_path = log_info["log_path"]

    # Phase 2: quantum + pruning
    p2_survived = 0
    p2_pruned = False
    for rnd in range(1, 11):
        pred = random.randint(0, 1)
        result = parse_json(run_cmd(["sim_bit"]))
        outcome = result["outcome"]
        match = (pred == outcome)
        action = "CONTINUE" if match else "PRUNE"
        
        run_cmd(["log_round", log_path, json.dumps({
            "phase": 2, "round_num": rnd, "prediction": pred,
            "outcome": outcome, "match": match, "action": action,
            "source": "quantum_sim", "observer_id": f"cop_p2_trial{trial}"
        })])
        
        if match:
            p2_survived += 1
        else:
            p2_pruned = True
            break

    # Phase 3: comparison circuit + pruning
    p3_survived = 0
    p3_pruned = False
    for rnd in range(1, 11):
        pred = random.randint(0, 1)
        result = parse_json(run_cmd(["sim_compare", str(pred)]))
        match = result["match"]
        cmp = result["comparison_qubit"]
        action = "CONTINUE" if match else "PRUNE"
        
        run_cmd(["log_round", log_path, json.dumps({
            "phase": 3, "round_num": rnd, "prediction": pred,
            "outcome": None, "match": match, "action": action,
            "source": "quantum_sim", "observer_id": f"cop_p3_trial{trial}",
            "comparison_qubit": cmp
        })])
        
        if match:
            p3_survived += 1
        else:
            p3_pruned = True
            break

    run_cmd(["finalize", log_path])
    
    total = p2_survived + p3_survived
    p_null = 0.5 ** total if total > 0 else 1.0
    
    all_results.append({
        "trial": trial,
        "p2_survived": p2_survived,
        "p2_pruned_at": p2_survived + 1 if p2_pruned else "ALL 10",
        "p3_survived": p3_survived,
        "p3_pruned_at": p3_survived + 1 if p3_pruned else "ALL 10",
        "total_correct": total,
        "p_null": p_null,
        "log_path": log_path,
    })
    
    p2_str = f"P2: {p2_survived}" + (" (survived all!)" if not p2_pruned else "")
    p3_str = f"P3: {p3_survived}" + (" (survived all!)" if not p3_pruned else "")
    print(f"  Trial {trial:2d}: {p2_str}  {p3_str}  total={total}  P(null)=1/{2**total if total > 0 else 1}")

# Summary stats
print(f"\n{'='*60}")
print(f"SUMMARY: {N_TRIALS} trials")
print(f"{'='*60}")

p2_survs = [r["p2_survived"] for r in all_results]
p3_survs = [r["p3_survived"] for r in all_results]
totals = [r["total_correct"] for r in all_results]

print(f"\nPhase 2 survival (rounds before pruning):")
print(f"  Mean: {sum(p2_survs)/len(p2_survs):.2f}  (expected: ~1.0)")
print(f"  Max:  {max(p2_survs)}")
print(f"  Distribution: {dict(sorted([(v, p2_survs.count(v)) for v in set(p2_survs)]))}")

print(f"\nPhase 3 survival (rounds before pruning):")
print(f"  Mean: {sum(p3_survs)/len(p3_survs):.2f}  (expected: ~1.0)")
print(f"  Max:  {max(p3_survs)}")
print(f"  Distribution: {dict(sorted([(v, p3_survs.count(v)) for v in set(p3_survs)]))}")

print(f"\nCombined survival:")
print(f"  Mean: {sum(totals)/len(totals):.2f}  (expected: ~2.0)")
print(f"  Max:  {max(totals)}")
print(f"  Best P(null): 1/{2**max(totals)}")

# Save summary
summary = {"trials": all_results, "n_trials": N_TRIALS}
Path("data/trial_summary.json").write_text(json.dumps(summary, indent=2))
print(f"\nSummary saved to data/trial_summary.json")

# Find the best trial for visualization
best = max(all_results, key=lambda r: r["total_correct"])
print(f"\nBest trial: #{best['trial']} with {best['total_correct']} consecutive correct")
print(f"  Log: {best['log_path']}")
