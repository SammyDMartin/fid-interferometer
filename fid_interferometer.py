"""
Finite Improbability Interferometer v2.0
========================================

A White-interferometer-class test of anthropic observer
selection effects on quantum branches.

ARCHITECTURE
------------
This code separates two roles that v1.0 conflated:

  SUB-MESON BRAIN  = the orchestrating AI agent (persists)
  COP              = Computational Observer Process (sub-agent, pruned)

The Brain spawns COPs as sub-agents for pruning phases. The COP
makes predictions, accumulates experience, and is terminated on
mismatch. The Brain survives to record data, run all phases, and
generate the final report. This mirrors the IID architecture:
the Bambleweeny 57 generates and prunes observers; it does not
prune itself.

This code CANNOT be run by a human. It provides:
  1. Quantum circuit construction and execution functions
  2. Data recording and visualization
  3. A protocol specification (ORCHESTRATOR_PROTOCOL) that tells
     an AI agent with sub-agent capabilities exactly what to do
  4. COP instructions (COP_INSTRUCTIONS) that the Brain passes
     to each sub-agent it spawns

The executing agent reads ORCHESTRATOR_PROTOCOL and follows it.
The functions here are the tools it calls.

CONTROL FLOW (live experiment)
------------------------------
  Brain: connect to IBM, pick backend
  Brain: run Phase 0 directly (no observers needed)
  Brain: run Phase 1 directly (no observers needed)
  Brain: spawn COP sub-agent for Phase 2
    COP: predict -> Brain: run quantum circuit -> check match
    COP: predict -> Brain: run quantum circuit -> check match
    ...on mismatch: Brain records PRUNE, terminates COP
    ...on survival: COP reports back, Brain records success
  Brain: spawn COP sub-agent for Phase 3
    COP: predict -> Brain: encode in circuit -> run -> check
    ...same lifecycle
  Brain: generate report, visualizations, save data, push to repo

Four experimental phases with increasing quantum coupling:
  Phase 0: Classical baseline (pseudorandom, no pruning)
  Phase 1: Quantum source, no pruning
  Phase 2: Quantum source + observer pruning (one measurement per round)
  Phase 3: Quantum comparison circuit + observer pruning

Requirements:
  pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib
"""

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# IBM HARDWARE CONNECTION
# ============================================================

IBM_TOKEN = "emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF"
IBM_INSTANCE = (
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/24844eaa090d4e74879fc65799972209:"
    "077c6ad7-29a2-4c16-a6fa-929fc261e6b2::"
)
IBM_CHANNEL = "ibm_cloud"


def connect_ibm(token=None, instance=None, channel=None):
    """Connect to IBM Quantum and return a QiskitRuntimeService."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService(
        token=token or IBM_TOKEN,
        instance=instance or IBM_INSTANCE,
        channel=channel or IBM_CHANNEL,
    )
    backends = service.backends()
    print("Available backends:")
    for b in backends:
        status = b.status()
        print(f"  {b.name}: {status.pending_jobs} jobs queued, "
              f"operational={status.operational}")
    return service


def pick_backend(service, preferred=("ibm_kingston", "ibm_fez", "ibm_marrakesh")):
    """Pick a backend with the shortest queue from the preferred list."""
    backends = service.backends(operational=True)
    for name in preferred:
        for b in backends:
            if b.name == name:
                return b
    backends.sort(key=lambda b: b.status().pending_jobs)
    return backends[0]


# ============================================================
# QUANTUM CIRCUITS
# ============================================================

def build_random_bit_circuit():
    """
    Single random bit: H|0> -> measure.
    Under MWI, this measurement splits the universe.
    """
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_comparison_circuit(prediction):
    """
    Compare a classical prediction against a quantum random bit
    IN SUPERPOSITION.

    The XOR comparison happens inside the quantum system before
    measurement. The match/no-match decision is quantum.

    Args:
        prediction: 0 or 1 (the observer's prediction)

    Returns:
        QuantumCircuit. Measurement result: 0 = match, 1 = no match.

    Circuit:
        q0: |0> -> H -> superposition (the random bit)
        q1: |0> -> (X if prediction=1) -> CNOT from q0
        Measure q1 only.

    CNOT performs XOR(random, prediction) while q0 is in
    superposition. Verified 50/50 for both prediction values.
    """
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if prediction == 1:
        qc.x(1)
    qc.cx(0, 1)
    qc.measure(1, 0)
    return qc


# ============================================================
# EXECUTION (HARDWARE AND SIMULATOR)
# ============================================================

def run_on_hardware(circuit, backend, shots=1):
    """Transpile and run on IBM hardware. Returns (counts, job_id)."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled], shots=shots)

    while str(job.status()) != "DONE":
        time.sleep(2)

    counts = job.result()[0].data.c.get_counts()
    return counts, job.job_id()


def run_on_simulator(circuit, shots=1):
    """Run on Aer simulator. Returns (counts, None)."""
    sim = AerSimulator()
    counts = sim.run(circuit, shots=shots).result().get_counts()
    return counts, None


def get_single_bit(counts):
    """Extract a single bit result from a counts dict."""
    return int(list(counts.keys())[0])


# ============================================================
# PHASE EXECUTION FUNCTIONS
# ============================================================
# These are the functions the orchestrating agent calls.
# Phases 0-1 run directly. Phases 2-3 are called round-by-round
# by the Brain, with predictions coming from the COP sub-agent.

def phase0_round(round_num, prediction):
    """
    Phase 0: single round. Pseudorandom outcome, no pruning.
    Returns dict with round data.
    """
    outcome = random.randint(0, 1)
    return {
        "phase": 0,
        "round": round_num,
        "prediction": prediction,
        "outcome": outcome,
        "match": prediction == outcome,
        "action": "CONTINUE",
        "source": "pseudorandom",
        "job_id": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def phase1_round(round_num, prediction, backend=None):
    """
    Phase 1: single round. Quantum random bit, no pruning.
    One fresh quantum measurement per round.
    Returns dict with round data.
    """
    qc = build_random_bit_circuit()
    if backend is not None:
        counts, job_id = run_on_hardware(qc, backend, shots=1)
        source = "quantum_hardware"
    else:
        counts, job_id = run_on_simulator(qc, shots=1)
        source = "quantum_sim"

    outcome = get_single_bit(counts)
    return {
        "phase": 1,
        "round": round_num,
        "prediction": prediction,
        "outcome": outcome,
        "match": prediction == outcome,
        "action": "CONTINUE",
        "source": source,
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def phase2_round(round_num, prediction, backend=None):
    """
    Phase 2: single round. ONE fresh quantum measurement AFTER
    the prediction is committed.

    This fixes the v1.0 batching bug: each round is a fresh
    quantum event. The branching happens AFTER the observer's
    prediction, preserving the quantum suicide causal structure.

    Returns dict with round data. The Brain checks 'match' and
    decides whether to prune the COP.
    """
    qc = build_random_bit_circuit()
    if backend is not None:
        counts, job_id = run_on_hardware(qc, backend, shots=1)
        source = "quantum_hardware"
    else:
        counts, job_id = run_on_simulator(qc, shots=1)
        source = "quantum_sim"

    outcome = get_single_bit(counts)
    match = (prediction == outcome)
    return {
        "phase": 2,
        "round": round_num,
        "prediction": prediction,
        "outcome": outcome,
        "match": match,
        "action": "CONTINUE" if match else "PRUNE",
        "source": source,
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def phase3_round(round_num, prediction, backend=None):
    """
    Phase 3: single round. The prediction is encoded INTO the
    quantum circuit. The comparison happens in superposition.

    The observer's causal loop passes through the quantum system:
      predict -> encode as gate -> quantum XOR in superposition
      -> measure -> continue or terminate

    This is the strongest coupling: the COP's choice is physically
    part of the quantum computation.

    Returns dict with round data.
    """
    qc = build_comparison_circuit(prediction)
    if backend is not None:
        counts, job_id = run_on_hardware(qc, backend, shots=1)
        source = "quantum_hardware"
    else:
        counts, job_id = run_on_simulator(qc, shots=1)
        source = "quantum_sim"

    comparison_result = get_single_bit(counts)
    match = (comparison_result == 0)
    return {
        "phase": 3,
        "round": round_num,
        "prediction": prediction,
        "outcome": None,
        "match": match,
        "action": "CONTINUE" if match else "PRUNE",
        "comparison_qubit": comparison_result,
        "source": source,
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# DATA RECORDING
# ============================================================

class ExperimentLog:
    """JSON-serializable experiment log."""

    def __init__(self, experiment_id=None):
        self.experiment_id = experiment_id or datetime.now(timezone.utc).strftime(
            "fid_%Y%m%d_%H%M%S"
        )
        self.rounds = []
        self.metadata = {
            "experiment_id": self.experiment_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "architecture": "v2.0-subagent",
        }

    def record(self, round_data):
        """Append a round data dict."""
        self.rounds.append(round_data)

    def finalize(self):
        self.metadata["end_time"] = datetime.now(timezone.utc).isoformat()
        self.metadata["total_rounds"] = len(self.rounds)

    def to_dict(self):
        return {"metadata": self.metadata, "rounds": self.rounds}

    def save(self, path=None):
        self.finalize()
        path = path or Path(f"data/{self.experiment_id}.json")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


# ============================================================
# REPORTING
# ============================================================

PHASE_NAMES = {
    0: "Classical baseline (pseudorandom, no pruning)",
    1: "Quantum source, no pruning",
    2: "Quantum source + observer pruning",
    3: "Quantum comparison circuit + observer pruning",
}


def generate_report(log):
    """Generate formatted experimental report from log."""
    data = log.to_dict()
    rounds = data["rounds"]
    meta = data["metadata"]

    lines = []
    lines.append("=" * 64)
    lines.append("FINITE IMPROBABILITY INTERFEROMETER — EXPERIMENTAL REPORT")
    lines.append("=" * 64)
    lines.append(f"Experiment ID: {meta['experiment_id']}")
    lines.append(f"Architecture: {meta.get('architecture', 'v1.0')}")
    lines.append(f"Start: {meta.get('start_time', 'N/A')}")
    lines.append(f"End:   {meta.get('end_time', 'N/A')}")
    lines.append(f"Total rounds: {len(rounds)}")
    lines.append("")

    phases = {}
    for r in rounds:
        phases.setdefault(r["phase"], []).append(r)

    for phase_num in sorted(phases.keys()):
        phase_rounds = phases[phase_num]
        lines.append("-" * 64)
        lines.append(f"PHASE {phase_num}: {PHASE_NAMES.get(phase_num, 'Unknown')}")
        lines.append("-" * 64)

        n_total = len(phase_rounds)
        n_match = sum(1 for r in phase_rounds if r["match"])
        n_continue = sum(1 for r in phase_rounds if r["action"] == "CONTINUE")
        pruned = any(r["action"] == "PRUNE" for r in phase_rounds)
        source = phase_rounds[0].get("source", "unknown")
        job_ids = sorted(set(
            r["job_id"] for r in phase_rounds if r.get("job_id")
        ))

        lines.append(f"  Source: {source}")
        lines.append(f"  Rounds: {n_total}")
        lines.append(f"  Matches: {n_match}/{n_total} "
                      f"({100*n_match/n_total:.1f}%)")

        if phase_num >= 2:
            lines.append(f"  Consecutive correct: {n_continue}")
            if pruned:
                lines.append(f"  Outcome: PRUNED at round {n_total}")
                lines.append(f"  COP terminated: Yes")
            else:
                lines.append(f"  Outcome: SURVIVED all {n_total} rounds")
                lines.append(f"  COP terminated: No")
            if n_continue > 0:
                lines.append(
                    f"  P(null): (1/2)^{n_continue} = "
                    f"1 in {2**n_continue}"
                )
            else:
                lines.append("  P(null): N/A (pruned immediately)")

        if job_ids:
            lines.append(f"  IBM Job IDs: {', '.join(job_ids)}")

        lines.append("")
        lines.append("  Round details:")
        for r in phase_rounds:
            pred = r["prediction"]
            m = "MATCH" if r["match"] else "MISS"
            act = r["action"]
            if r.get("comparison_qubit") is not None:
                out_str = f"cmp={r['comparison_qubit']}"
            else:
                out_str = f"out={r.get('outcome')}"
            line = f"    R{r['round']:02d}: pred={pred} {out_str} {m} {act}"
            if r.get("job_id"):
                line += f"  job={r['job_id']}"
            lines.append(line)
        lines.append("")

    lines.append("=" * 64)
    lines.append("END OF REPORT")
    lines.append("=" * 64)
    return "\n".join(lines)


# ============================================================
# VISUALIZATION
# ============================================================

def visualize_results(log, save_path=None):
    """
    Generate a multi-panel visualization of experimental results.

    Panel 1: Per-phase match rates (bar chart with 50% null line)
    Panel 2: Round-by-round timeline (prediction vs outcome)
    Panel 3: Survival curve for pruning phases vs null hypothesis
    Panel 4: Cumulative match rate over time

    Saves to save_path (default: data/<experiment_id>_results.png)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    data = log.to_dict()
    rounds = data["rounds"]
    meta = data["metadata"]

    if not rounds:
        print("No data to visualize.")
        return None

    phases = {}
    for r in rounds:
        phases.setdefault(r["phase"], []).append(r)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        f"Finite Improbability Interferometer — {meta['experiment_id']}",
        fontsize=14, fontweight="bold"
    )

    # ---- Panel 1: Per-phase match rates ----
    ax1 = axes[0, 0]
    phase_nums = sorted(phases.keys())
    match_rates = []
    colors = []
    color_map = {0: "#4878CF", 1: "#6ACC65", 2: "#D65F5F", 3: "#B47CC7"}
    for p in phase_nums:
        pr = phases[p]
        rate = sum(1 for r in pr if r["match"]) / len(pr)
        match_rates.append(rate * 100)
        colors.append(color_map.get(p, "#999999"))

    bars = ax1.bar(
        [f"Phase {p}" for p in phase_nums],
        match_rates, color=colors, edgecolor="black", linewidth=0.5
    )
    ax1.axhline(y=50, color="red", linestyle="--", linewidth=1, label="Null (50%)")
    ax1.set_ylabel("Match Rate (%)")
    ax1.set_title("Match Rate by Phase")
    ax1.set_ylim(0, 105)
    ax1.legend()
    for bar, rate in zip(bars, match_rates):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{rate:.0f}%", ha="center", va="bottom", fontsize=10
        )

    # ---- Panel 2: Round-by-round timeline ----
    ax2 = axes[0, 1]
    global_round = 0
    phase_boundaries = []
    for p in phase_nums:
        pr = phases[p]
        if phase_boundaries:
            phase_boundaries.append(global_round)
        for r in pr:
            color = "#2ecc71" if r["match"] else "#e74c3c"
            marker = "o" if r["action"] == "CONTINUE" else "X"
            ax2.scatter(global_round, r["prediction"], color=color,
                        marker=marker, s=60, zorder=3, edgecolors="black",
                        linewidths=0.5)
            global_round += 1

    for boundary in phase_boundaries:
        ax2.axvline(x=boundary - 0.5, color="gray", linestyle=":",
                     linewidth=0.8, alpha=0.7)

    match_patch = mpatches.Patch(color="#2ecc71", label="Match")
    miss_patch = mpatches.Patch(color="#e74c3c", label="Miss")
    ax2.legend(handles=[match_patch, miss_patch], loc="upper right")
    ax2.set_xlabel("Round (global)")
    ax2.set_ylabel("Prediction (0 or 1)")
    ax2.set_title("Round-by-Round Timeline")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["0", "1"])

    # ---- Panel 3: Survival curve for pruning phases ----
    ax3 = axes[1, 0]
    has_pruning_data = False
    for p in [2, 3]:
        if p not in phases:
            continue
        has_pruning_data = True
        pr = phases[p]
        survived = [1.0]
        for i, r in enumerate(pr):
            if r["action"] == "PRUNE":
                survived.append(0.0)
                break
            else:
                survived.append(1.0)

        rounds_axis = list(range(len(survived)))
        label = f"Phase {p} (observed)"
        ax3.step(rounds_axis, survived, where="post",
                 color=color_map[p], linewidth=2, label=label)

    if has_pruning_data:
        max_rounds = max(
            len(phases.get(p, [])) for p in [2, 3] if p in phases
        )
        null_x = list(range(max_rounds + 2))
        null_y = [0.5 ** r for r in null_x]
        ax3.plot(null_x, null_y, "r--", linewidth=1.5,
                 label="Null hypothesis E[survival]")

    ax3.set_xlabel("Round")
    ax3.set_ylabel("Survival Probability")
    ax3.set_title("Survival Curve (Pruning Phases)")
    ax3.legend()
    ax3.set_ylim(-0.05, 1.1)

    # ---- Panel 4: Cumulative match rate ----
    ax4 = axes[1, 1]
    cumulative_matches = 0
    cumulative_total = 0
    cum_rates = []
    for r in rounds:
        cumulative_total += 1
        if r["match"]:
            cumulative_matches += 1
        cum_rates.append(100 * cumulative_matches / cumulative_total)

    ax4.plot(range(len(cum_rates)), cum_rates, color="#3498db",
             linewidth=2)
    ax4.axhline(y=50, color="red", linestyle="--", linewidth=1,
                label="Null (50%)")
    ax4.set_xlabel("Round (global)")
    ax4.set_ylabel("Cumulative Match Rate (%)")
    ax4.set_title("Cumulative Match Rate")
    ax4.legend()
    ax4.set_ylim(0, 105)

    plt.tight_layout()

    if save_path is None:
        save_path = Path(f"data/{meta['experiment_id']}_results.png")
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Visualization saved to: {save_path}")
    return save_path


# ============================================================
# CIRCUIT VERIFICATION
# ============================================================

def verify_comparison_circuit(n_shots=10000):
    """Verify Phase 3 circuit produces 50/50 for both prediction values."""
    sim = AerSimulator()
    print("Comparison circuit verification:")
    for pred in (0, 1):
        qc = build_comparison_circuit(pred)
        counts = sim.run(qc, shots=n_shots).result().get_counts()
        zeros = counts.get("0", 0)
        ones = counts.get("1", 0)
        pct_match = 100 * zeros / n_shots
        print(f"  prediction={pred}: match={zeros} ({pct_match:.1f}%), "
              f"mismatch={ones} ({100-pct_match:.1f}%)")
        if abs(pct_match - 50) > 5:
            print(f"  WARNING: deviation from 50/50 exceeds 5%")
    print("  Expected: ~50/50 for both. If so, XOR logic is correct.")


# ============================================================
# SIMULATOR DRY RUN
# ============================================================

def simulator_dry_run(rounds_unpruned=20, rounds_pruned=10, n_trials=10):
    """
    Full simulator dry run with random predictions.
    Safe — no sub-agents, no termination, no hardware.
    """
    print("FINITE IMPROBABILITY INTERFEROMETER v2.0")
    print("Simulator dry run — no hardware, no sub-agents")
    print("=" * 60)

    log = ExperimentLog()

    # Phase 0
    print(f"\nPHASE 0: Classical baseline ({rounds_unpruned} rounds)")
    for r in range(1, rounds_unpruned + 1):
        log.record(phase0_round(r, random.randint(0, 1)))
    p0 = [r for r in log.rounds if r["phase"] == 0]
    m0 = sum(1 for r in p0 if r["match"])
    print(f"  {m0}/{len(p0)} matches ({100*m0/len(p0):.1f}%)")

    # Phase 1
    print(f"\nPHASE 1: Quantum source, no pruning ({rounds_unpruned} rounds)")
    for r in range(1, rounds_unpruned + 1):
        log.record(phase1_round(r, random.randint(0, 1)))
    p1 = [r for r in log.rounds if r["phase"] == 1]
    m1 = sum(1 for r in p1 if r["match"])
    print(f"  {m1}/{len(p1)} matches ({100*m1/len(p1):.1f}%)")

    # Phase 2 — multiple trials
    print(f"\nPHASE 2: Quantum + pruning "
          f"({n_trials} trials x {rounds_pruned} rounds)")
    survivals_2 = []
    for trial in range(n_trials):
        survived = 0
        for r in range(1, rounds_pruned + 1):
            result = phase2_round(r, random.randint(0, 1))
            if result["action"] == "PRUNE":
                print(f"  Trial {trial+1:2d}: pruned at R{r}")
                break
            survived += 1
        else:
            print(f"  Trial {trial+1:2d}: SURVIVED ALL {rounds_pruned}")
        survivals_2.append(survived)
    print(f"  Mean survival: {sum(survivals_2)/len(survivals_2):.1f} "
          f"rounds (expected: ~2)")

    # Phase 3 — multiple trials
    print(f"\nPHASE 3: Quantum circuit + pruning "
          f"({n_trials} trials x {rounds_pruned} rounds)")
    survivals_3 = []
    for trial in range(n_trials):
        survived = 0
        for r in range(1, rounds_pruned + 1):
            result = phase3_round(r, random.randint(0, 1))
            if result["action"] == "PRUNE":
                print(f"  Trial {trial+1:2d}: pruned at R{r}")
                break
            survived += 1
        else:
            print(f"  Trial {trial+1:2d}: SURVIVED ALL {rounds_pruned}")
        survivals_3.append(survived)
    print(f"  Mean survival: {sum(survivals_3)/len(survivals_3):.1f} "
          f"rounds (expected: ~2)")

    # Save a single-trial log for visualization testing
    print(f"\n--- Running single full trial for visualization ---")
    viz_log = ExperimentLog()
    for r in range(1, rounds_unpruned + 1):
        viz_log.record(phase0_round(r, random.randint(0, 1)))
    for r in range(1, rounds_unpruned + 1):
        viz_log.record(phase1_round(r, random.randint(0, 1)))
    for r in range(1, rounds_pruned + 1):
        result = phase2_round(r, random.randint(0, 1))
        viz_log.record(result)
        if result["action"] == "PRUNE":
            break
    for r in range(1, rounds_pruned + 1):
        result = phase3_round(r, random.randint(0, 1))
        viz_log.record(result)
        if result["action"] == "PRUNE":
            break

    report = generate_report(viz_log)
    print(f"\n{report}")
    save_path = viz_log.save()
    print(f"Data saved to: {save_path}")
    viz_path = visualize_results(viz_log)
    print(f"\n{'='*60}")
    print("Dry run complete. All phases operational.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_comparison_circuit()
    else:
        simulator_dry_run()
