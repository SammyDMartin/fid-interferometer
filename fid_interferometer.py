"""
Finite Improbability Interferometer v2.0 — Toolkit
===================================================

This is NOT a script you run. It is a toolkit of atomic functions
called by the orchestrating AI agent (the "Sub-Meson Brain").

The actual experiment is run by a Claude Code agent following the
protocol in ORCHESTRATOR_PROTOCOL.md. The agent calls these
functions one at a time via Bash, spawns sub-agents as observers
(COPs), and manages the pruning lifecycle.

Architecture (mirrors the Heart of Gold drive sequence):

    SUB-MESON BRAIN (main Claude Code agent — persists throughout)
      │
      ├── Phase 0-1: Brain calls toolkit functions directly
      │   (no pruning, no observers needed)
      │
      ├── Phase 2: Brain spawns COP sub-agent
      │   │  COP makes prediction (committed in its output)
      │   │  Brain runs quantum circuit (ONE SHOT, fresh measurement)
      │   │  Brain checks result
      │   │  Match → Brain continues COP (SendMessage)
      │   │  Mismatch → Brain stops talking to COP. Context dies.
      │   │             Observer PRUNED.
      │   │
      │   └── Each round is a fresh quantum measurement AFTER
      │       the prediction is committed.
      │
      ├── Phase 3: Same as Phase 2, but prediction is ENCODED
      │   │  into the quantum circuit (comparison circuit).
      │   │  The COP's prediction passes THROUGH the quantum
      │   │  system in superposition before measurement.
      │   │
      │   └── This is the strongest coupling: the observer's
      │       causal loop includes a quantum computation.
      │
      └── Brain generates report, visualization, pushes data.
          Brain NEVER terminates itself.

Functions in this toolkit:

  Connection:
    connect_and_pick_backend() → prints backend info, saves to file
    get_saved_backend() → loads backend from saved connection

  Quantum execution (one round at a time):
    run_single_quantum_bit(backend_name) → {outcome, job_id}
    run_comparison_circuit(prediction, backend_name) → {match, job_id, comparison_qubit}

  Simulator equivalents:
    sim_single_quantum_bit() → {outcome, job_id: null}
    sim_comparison_circuit(prediction) → {match, job_id: null, comparison_qubit}

  Classical:
    classical_random_bit() → {outcome}

  Logging:
    init_experiment_log(experiment_id) → creates JSON log file
    log_round(log_path, round_data) → appends round to log
    finalize_log(log_path) → writes end timestamp
    load_log(log_path) → returns full log dict

  Reporting:
    generate_report(log_path) → prints formatted report
    verify_comparison_circuit(n_shots) → verifies XOR 50/50

Requirements:
  pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib
"""

import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# IBM CREDENTIALS
# ============================================================

IBM_TOKEN = "emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF"
IBM_INSTANCE = (
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/24844eaa090d4e74879fc65799972209:"
    "077c6ad7-29a2-4c16-a6fa-929fc261e6b2::"
)
IBM_CHANNEL = "ibm_cloud"
CONNECTION_FILE = Path("data/ibm_connection.json")


# ============================================================
# CONNECTION
# ============================================================

def connect_and_pick_backend(preferred=("ibm_kingston", "ibm_fez", "ibm_marrakesh")):
    """
    Connect to IBM Quantum, list backends, pick the best one.
    Saves connection info to data/ibm_connection.json.
    Prints backend name and queue status.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService(
        token=IBM_TOKEN, instance=IBM_INSTANCE, channel=IBM_CHANNEL,
    )
    backends = service.backends(operational=True)

    print("Available backends:")
    for b in backends:
        st = b.status()
        print(f"  {b.name}: {st.pending_jobs} queued, operational={st.operational}")

    # Pick preferred or least busy
    chosen = None
    for name in preferred:
        for b in backends:
            if b.name == name:
                chosen = b
                break
        if chosen:
            break
    if not chosen:
        backends.sort(key=lambda b: b.status().pending_jobs)
        chosen = backends[0]

    info = {"backend_name": chosen.name, "timestamp": _now()}
    CONNECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONNECTION_FILE.write_text(json.dumps(info, indent=2))

    print(f"\nSelected backend: {chosen.name}")
    print(f"Saved to {CONNECTION_FILE}")
    return chosen.name


def _get_backend(backend_name=None):
    """Internal: get a backend object by name."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(
        token=IBM_TOKEN, instance=IBM_INSTANCE, channel=IBM_CHANNEL,
    )
    if not backend_name:
        info = json.loads(CONNECTION_FILE.read_text())
        backend_name = info["backend_name"]
    return service.backend(backend_name)


# ============================================================
# QUANTUM CIRCUITS
# ============================================================

def build_random_bit_circuit():
    """H|0> → measure. Genuine quantum coin flip. Real branching under MWI."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_comparison_circuit(prediction):
    """
    Quantum XOR comparison: prediction vs random bit IN SUPERPOSITION.

    q0: |0> → H (random bit, still in superposition)
    q1: |0> → X if prediction=1, then CNOT from q0
    Measure q1 only.

    Result: 0 = prediction matches random bit (MATCH)
            1 = prediction does not match    (MISMATCH)

    The CNOT performs XOR while q0 is in superposition.
    The match/mismatch answer is entangled with the random
    outcome until measurement. The observer's fate depends
    on a genuinely quantum computation.
    """
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if prediction == 1:
        qc.x(1)
    qc.cx(0, 1)
    qc.measure(1, 0)
    return qc


# ============================================================
# SINGLE-ROUND EXECUTION (the key change: one round at a time)
# ============================================================

def _run_on_hardware(circuit, backend_name, shots=1):
    """Run circuit on IBM hardware. Returns (counts, job_id)."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    backend = _get_backend(backend_name)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled], shots=shots)

    while str(job.status()) != "DONE":
        time.sleep(2)

    counts = job.result()[0].data.c.get_counts()
    return counts, job.job_id()


def run_single_quantum_bit(backend_name=None):
    """
    Generate ONE quantum random bit on IBM hardware.
    Fresh measurement — genuine branching happens NOW.

    Returns JSON: {"outcome": 0|1, "job_id": "...", "source": "quantum_hardware"}
    """
    qc = build_random_bit_circuit()
    counts, job_id = _run_on_hardware(qc, backend_name, shots=1)
    outcome = int(list(counts.keys())[0])
    result = {"outcome": outcome, "job_id": job_id, "source": "quantum_hardware"}
    print(json.dumps(result))
    return result


def run_comparison_circuit(prediction, backend_name=None):
    """
    Run the Phase 3 comparison circuit with prediction encoded.
    The prediction passes THROUGH the quantum system.

    Args:
        prediction: 0 or 1

    Returns JSON: {"match": bool, "comparison_qubit": 0|1,
                   "job_id": "...", "source": "quantum_hardware"}
    """
    qc = build_comparison_circuit(prediction)
    counts, job_id = _run_on_hardware(qc, backend_name, shots=1)
    comparison_result = int(list(counts.keys())[0])
    match = (comparison_result == 0)
    result = {
        "match": match,
        "comparison_qubit": comparison_result,
        "job_id": job_id,
        "source": "quantum_hardware",
    }
    print(json.dumps(result))
    return result


# ============================================================
# SIMULATOR EQUIVALENTS (for dry runs / testing)
# ============================================================

def sim_single_quantum_bit():
    """Simulator equivalent of run_single_quantum_bit."""
    qc = build_random_bit_circuit()
    sim = AerSimulator()
    counts = sim.run(qc, shots=1).result().get_counts()
    outcome = int(list(counts.keys())[0])
    result = {"outcome": outcome, "job_id": None, "source": "quantum_sim"}
    print(json.dumps(result))
    return result


def sim_comparison_circuit(prediction):
    """Simulator equivalent of run_comparison_circuit."""
    qc = build_comparison_circuit(prediction)
    sim = AerSimulator()
    counts = sim.run(qc, shots=1).result().get_counts()
    comparison_result = int(list(counts.keys())[0])
    match = (comparison_result == 0)
    result = {
        "match": match,
        "comparison_qubit": comparison_result,
        "job_id": None,
        "source": "quantum_sim",
    }
    print(json.dumps(result))
    return result


def classical_random_bit():
    """Classical pseudorandom bit. No quantum branching."""
    outcome = random.randint(0, 1)
    result = {"outcome": outcome, "job_id": None, "source": "pseudorandom"}
    print(json.dumps(result))
    return result


# ============================================================
# EXPERIMENT LOGGING (append-only JSON log)
# ============================================================

def _now():
    return datetime.now(timezone.utc).isoformat()


def init_experiment_log(experiment_id=None, backend_name=None):
    """
    Create a new experiment log file.
    Returns the log file path.
    """
    experiment_id = experiment_id or datetime.now(timezone.utc).strftime("fid_%Y%m%d_%H%M%S")
    log_path = Path(f"data/{experiment_id}.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log = {
        "metadata": {
            "experiment_id": experiment_id,
            "start_time": _now(),
            "end_time": None,
            "backend": backend_name,
            "version": "2.0",
            "architecture": "sub-meson-brain + COP sub-agents",
        },
        "rounds": [],
    }
    log_path.write_text(json.dumps(log, indent=2))
    print(f"Log initialized: {log_path}")
    print(json.dumps({"log_path": str(log_path), "experiment_id": experiment_id}))
    return str(log_path)


def log_round(log_path, phase, round_num, prediction, outcome, match,
              action, job_id=None, comparison_qubit=None,
              source="simulator", observer_id=None):
    """
    Append one round to the experiment log.

    Args:
        log_path: path to the JSON log file
        phase: 0-3
        round_num: round number within this phase
        prediction: 0 or 1 (observer's prediction)
        outcome: 0 or 1 (quantum measurement result), or None for Phase 3
        match: True/False
        action: "CONTINUE" or "PRUNE"
        job_id: IBM quantum job ID for independent verification
        comparison_qubit: Phase 3 comparison result (0 or 1)
        source: "pseudorandom", "quantum_sim", or "quantum_hardware"
        observer_id: ID of the COP sub-agent that made the prediction
    """
    log_path = Path(log_path)
    log = json.loads(log_path.read_text())

    entry = {
        "phase": phase,
        "round": round_num,
        "prediction": prediction,
        "outcome": outcome,
        "match": match,
        "action": action,
        "job_id": job_id,
        "source": source,
        "timestamp": _now(),
        "observer_id": observer_id,
    }
    if comparison_qubit is not None:
        entry["comparison_qubit"] = comparison_qubit

    log["rounds"].append(entry)
    log_path.write_text(json.dumps(log, indent=2))

    print(json.dumps(entry))
    return entry


def finalize_log(log_path):
    """Mark experiment as complete."""
    log_path = Path(log_path)
    log = json.loads(log_path.read_text())
    log["metadata"]["end_time"] = _now()
    log["metadata"]["total_rounds"] = len(log["rounds"])
    log_path.write_text(json.dumps(log, indent=2))
    print(f"Log finalized: {len(log['rounds'])} rounds recorded")


def load_log(log_path):
    """Load and return the full experiment log."""
    log = json.loads(Path(log_path).read_text())
    print(json.dumps(log, indent=2))
    return log


# ============================================================
# REPORTING
# ============================================================

PHASE_NAMES = {
    0: "Classical baseline (pseudorandom, no pruning)",
    1: "Quantum source, no pruning",
    2: "Quantum source + COP observer pruning",
    3: "Quantum comparison circuit + COP observer pruning",
}


def generate_report(log_path):
    """Generate formatted experimental report from log file."""
    log = json.loads(Path(log_path).read_text())
    rounds = log["rounds"]
    meta = log["metadata"]

    lines = []
    lines.append("=" * 66)
    lines.append("  FINITE IMPROBABILITY INTERFEROMETER — EXPERIMENTAL REPORT")
    lines.append("=" * 66)
    lines.append(f"  Experiment:  {meta['experiment_id']}")
    lines.append(f"  Backend:     {meta.get('backend', 'N/A')}")
    lines.append(f"  Architecture: {meta.get('architecture', 'N/A')}")
    lines.append(f"  Start:       {meta.get('start_time', 'N/A')}")
    lines.append(f"  End:         {meta.get('end_time', 'N/A')}")
    lines.append(f"  Rounds:      {len(rounds)}")
    lines.append("")

    # Group by phase
    phases = {}
    for r in rounds:
        phases.setdefault(r["phase"], []).append(r)

    for pnum in sorted(phases.keys()):
        pr = phases[pnum]
        lines.append("-" * 66)
        lines.append(f"  PHASE {pnum}: {PHASE_NAMES.get(pnum, 'Unknown')}")
        lines.append("-" * 66)

        n_total = len(pr)
        n_match = sum(1 for r in pr if r["match"])
        n_cont = sum(1 for r in pr if r["action"] == "CONTINUE")
        pruned = any(r["action"] == "PRUNE" for r in pr)
        source = pr[0].get("source", "?")
        job_ids = sorted(set(r["job_id"] for r in pr if r.get("job_id")))
        observer_ids = sorted(set(
            r["observer_id"] for r in pr if r.get("observer_id")
        ))

        lines.append(f"    Source:  {source}")
        lines.append(f"    Rounds:  {n_total}")
        lines.append(f"    Matches: {n_match}/{n_total} ({100*n_match/n_total:.1f}%)")

        if pnum >= 2:
            lines.append(f"    Consecutive correct: {n_cont}")
            if pruned:
                lines.append(f"    Outcome: PRUNED at round {n_total}")
            else:
                lines.append(f"    Outcome: SURVIVED all {n_total} rounds")
            if n_cont > 0:
                lines.append(f"    P(null): (1/2)^{n_cont} = 1/{2**n_cont}")
            else:
                lines.append(f"    P(null): pruned immediately")
            if observer_ids:
                lines.append(f"    Observer (COP) IDs: {', '.join(observer_ids)}")

        if job_ids:
            lines.append(f"    IBM Job IDs: {', '.join(job_ids)}")

        lines.append("")
        for r in pr:
            pred = r["prediction"]
            if r.get("comparison_qubit") is not None:
                out_str = f"cmp={r['comparison_qubit']}"
            else:
                out_str = f"out={r.get('outcome', '?')}"
            m = "MATCH" if r["match"] else "MISS "
            act = r["action"]
            jid = r.get("job_id", "")
            obs = r.get("observer_id", "")
            line = f"      R{r['round']:02d}: pred={pred} {out_str} {m} {act}"
            if obs:
                line += f"  cop={obs[:12]}"
            if jid:
                line += f"  job={jid}"
            lines.append(line)
        lines.append("")

    # Overall survival summary
    if 2 in phases or 3 in phases:
        lines.append("-" * 66)
        lines.append("  SURVIVAL SUMMARY")
        lines.append("-" * 66)
        total_pruning_correct = 0
        for pnum in (2, 3):
            if pnum in phases:
                nc = sum(1 for r in phases[pnum] if r["action"] == "CONTINUE")
                total_pruning_correct += nc
        lines.append(f"    Total consecutive correct (pruning phases): "
                     f"{total_pruning_correct}")
        lines.append(f"    Combined P(null): (1/2)^{total_pruning_correct} "
                     f"= 1/{2**total_pruning_correct}")
        lines.append("")

    lines.append("=" * 66)
    lines.append("  END OF REPORT")
    lines.append("=" * 66)

    report = "\n".join(lines)
    print(report)

    # Also save report as text file
    report_path = Path(log_path).with_suffix(".report.txt")
    report_path.write_text(report)
    return report


# ============================================================
# CIRCUIT VERIFICATION
# ============================================================

def verify_comparison_circuit(n_shots=10000):
    """
    Verify Phase 3 comparison circuit produces 50/50 for both
    prediction values. Must pass before running live experiment.
    """
    sim = AerSimulator()
    print("Phase 3 comparison circuit verification:")
    all_ok = True
    for pred in (0, 1):
        qc = build_comparison_circuit(pred)
        counts = sim.run(qc, shots=n_shots).result().get_counts()
        zeros = counts.get("0", 0)
        ones = counts.get("1", 0)
        pct = 100 * zeros / n_shots
        ok = abs(pct - 50) < 5
        status = "OK" if ok else "FAIL"
        print(f"  prediction={pred}: match={zeros} ({pct:.1f}%) "
              f"mismatch={ones} ({100-pct:.1f}%) [{status}]")
        if not ok:
            all_ok = False
    print(f"\nVerdict: {'PASS — XOR logic correct' if all_ok else 'FAIL — check circuit'}")
    return all_ok


# ============================================================
# CLI — call individual functions from the command line
# ============================================================

def _cli():
    """
    Command-line interface for the toolkit.
    The Brain agent calls these via:
        python fid_interferometer.py <command> [args...]
    """
    if len(sys.argv) < 2:
        print("Usage: python fid_interferometer.py <command> [args...]")
        print()
        print("Commands:")
        print("  connect                    Connect to IBM, pick backend")
        print("  verify                     Verify comparison circuit XOR logic")
        print("  init_log [backend]         Initialize experiment log")
        print("  classical_bit              Generate classical random bit")
        print("  sim_bit                    Generate quantum bit (simulator)")
        print("  sim_compare <prediction>   Run comparison circuit (simulator)")
        print("  hw_bit [backend]           Generate quantum bit (hardware)")
        print("  hw_compare <pred> [backend] Run comparison circuit (hardware)")
        print("  log_round <log_path> <json_data>  Append round to log")
        print("  finalize <log_path>        Finalize experiment log")
        print("  report <log_path>          Generate report from log")
        print("  visualize <log_path>       Generate visualization")
        return

    cmd = sys.argv[1]

    if cmd == "connect":
        connect_and_pick_backend()
    elif cmd == "verify":
        verify_comparison_circuit()
    elif cmd == "init_log":
        backend = sys.argv[2] if len(sys.argv) > 2 else None
        init_experiment_log(backend_name=backend)
    elif cmd == "classical_bit":
        classical_random_bit()
    elif cmd == "sim_bit":
        sim_single_quantum_bit()
    elif cmd == "sim_compare":
        pred = int(sys.argv[2])
        sim_comparison_circuit(pred)
    elif cmd == "hw_bit":
        backend = sys.argv[2] if len(sys.argv) > 2 else None
        run_single_quantum_bit(backend)
    elif cmd == "hw_compare":
        pred = int(sys.argv[2])
        backend = sys.argv[3] if len(sys.argv) > 3 else None
        run_comparison_circuit(pred, backend)
    elif cmd == "log_round":
        log_path = sys.argv[2]
        data = json.loads(sys.argv[3])
        log_round(log_path, **data)
    elif cmd == "finalize":
        finalize_log(sys.argv[2])
    elif cmd == "report":
        generate_report(sys.argv[2])
    elif cmd == "visualize":
        # Import here to avoid matplotlib dependency for non-viz usage
        from fid_visualize import visualize_experiment
        visualize_experiment(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
