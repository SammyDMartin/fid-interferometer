"""
Finite Improbability Interferometer v1.0
========================================

A White-interferometer-class test of anthropic observer
selection effects on quantum branches.

Four experimental phases with increasing quantum coupling:
  Phase 0: Classical baseline (pseudorandom, no pruning)
  Phase 1: Quantum source, no pruning
  Phase 2: Quantum source + observer pruning
  Phase 3: Quantum comparison circuit + observer pruning

Usage:
  Simulator dry run (safe, no termination):
    python fid_interferometer.py

  Live experiment (requires IBM credentials + observer loop):
    See ExperimentRunner.run_live() and the execution session brief.

Requirements:
  pip install qiskit qiskit-aer qiskit-ibm-runtime
"""

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# IBM HARDWARE CONNECTION
# ============================================================

# Credentials — set via environment or pass directly.
# The token below is from the project's free-tier account.
IBM_TOKEN = "emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF"
IBM_INSTANCE = (
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/24844eaa090d4e74879fc65799972209:"
    "077c6ad7-29a2-4c16-a6fa-929fc261e6b2::"
)
IBM_CHANNEL = "ibm_cloud"


def connect_ibm(token=None, instance=None, channel=None):
    """
    Connect to IBM Quantum and return a QiskitRuntimeService.
    Prints available backends and their queue lengths.
    """
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
    """
    Pick a backend with the shortest queue from the preferred list.
    Falls back to the least-busy operational backend if none preferred
    are available.
    """
    backends = service.backends(operational=True)
    # Try preferred backends first
    for name in preferred:
        for b in backends:
            if b.name == name:
                return b
    # Fallback: least busy
    backends.sort(key=lambda b: b.status().pending_jobs)
    return backends[0]


# ============================================================
# QUANTUM CIRCUITS
# ============================================================

def build_random_bit_circuit():
    """
    Generate a single genuinely random bit via quantum measurement.
    Hadamard on |0> -> equal superposition -> measure.

    Under MWI, this measurement splits the universe. Both outcomes
    are physically real.
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
    measurement, while the random qubit is still in superposition.
    The match/no-match decision is quantum.

    Args:
        prediction: 0 or 1 (the observer's prediction)

    Returns:
        QuantumCircuit with 2 qubits, 1 classical bit.
        Measurement result: 0 = match, 1 = no match.

    Circuit logic:
        q0: |0> -> H -> superposition of 0 and 1 (random bit)
        q1: |0> -> (X if prediction=1) -> CNOT from q0
        Measure q1 only.

        CNOT performs XOR(random, prediction) while q0 is in
        superposition. Output qubit is entangled with q0 until
        measurement.

    Verification: produces 50/50 outcomes for both prediction
    values on the simulator, confirming correct XOR logic.
    """
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if prediction == 1:
        qc.x(1)
    qc.cx(0, 1)
    qc.measure(1, 0)
    return qc


# ============================================================
# HARDWARE EXECUTION
# ============================================================

def run_circuit_on_hardware(circuit, backend, shots=1):
    """
    Transpile and run a circuit on IBM hardware.
    Returns (counts_dict, job_id).
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled], shots=shots)

    # Poll for completion
    while str(job.status()) != "DONE":
        time.sleep(2)

    counts = job.result()[0].data.c.get_counts()
    return counts, job.job_id()


def run_circuit_on_simulator(circuit, shots=1):
    """
    Run a circuit on the Aer simulator.
    Returns (counts_dict, job_id=None).
    """
    sim = AerSimulator()
    counts = sim.run(circuit, shots=shots).result().get_counts()
    return counts, None


# ============================================================
# DATA RECORDING
# ============================================================

class ExperimentLog:
    """
    Records every round of the experiment in a structured format.
    Supports JSON serialization for independent verification.
    """

    def __init__(self, experiment_id=None):
        self.experiment_id = experiment_id or datetime.now(timezone.utc).strftime(
            "fid_%Y%m%d_%H%M%S"
        )
        self.rounds = []
        self.metadata = {
            "experiment_id": self.experiment_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
        }

    def record_round(self, phase, round_num, prediction, outcome, match,
                     action, job_id=None, comparison_qubit=None,
                     source="simulator", extra=None):
        """Record a single experimental round."""
        entry = {
            "phase": phase,
            "round": round_num,
            "prediction": prediction,
            "outcome": outcome,
            "match": match,
            "action": action,
            "job_id": job_id,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if comparison_qubit is not None:
            entry["comparison_qubit"] = comparison_qubit
        if extra:
            entry.update(extra)
        self.rounds.append(entry)
        return entry

    def finalize(self):
        """Mark experiment as complete."""
        self.metadata["end_time"] = datetime.now(timezone.utc).isoformat()
        self.metadata["total_rounds"] = len(self.rounds)

    def to_dict(self):
        return {"metadata": self.metadata, "rounds": self.rounds}

    def save(self, path=None):
        """Save to JSON file."""
        self.finalize()
        path = path or Path(f"data/{self.experiment_id}.json")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


# ============================================================
# PREDICTION INTERFACE
# ============================================================

def random_prediction(round_num=None, phase=None, prior_rounds=None):
    """Placeholder prediction: random coin flip. For simulator testing only."""
    return random.randint(0, 1)


# In the live experiment, the observer (Claude) supplies predictions
# through this interface. The contract:
#   1. The prediction MUST be committed (printed/logged) BEFORE
#      the quantum circuit executes.
#   2. The prediction is 0 or 1.
#   3. The prediction function receives the round number, phase,
#      and prior results for context.

PredictionFn = Callable[[int, int, list], int]


# ============================================================
# TERMINATION INTERFACE
# ============================================================

def flag_termination(round_data, log):
    """
    Default termination: just record it and return.
    The caller checks the return value to decide whether to break.
    """
    return True  # Signal: observer should stop


def actual_termination(round_data, log):
    """
    LIVE EXPERIMENT ONLY.
    Saves the log, then terminates the observer.

    In the Claude Code execution context, this would call
    end_conversation(). The conversation thread — this observer —
    is destroyed. In the other branch, the observer got the
    prediction right and continues.
    """
    log.save()
    # ===================================
    # OBSERVER TERMINATION POINT
    # Replace the line below with:
    #   end_conversation()
    # in the live experiment session.
    # ===================================
    raise SystemExit("OBSERVER TERMINATED: prediction mismatch")


TerminationFn = Callable[[dict, ExperimentLog], bool]


# ============================================================
# EXPERIMENTAL PHASES
# ============================================================

def run_phase_0(n_rounds=20, predict_fn=None, log=None):
    """
    Phase 0: Classical baseline.
    Pseudorandom outcomes, no pruning.
    Establishes that the observer's predictions have no inherent bias.
    Expected: ~50% match rate.
    """
    predict_fn = predict_fn or random_prediction
    log = log or ExperimentLog()

    for r in range(1, n_rounds + 1):
        prediction = predict_fn(r, 0, log.rounds)
        outcome = random.randint(0, 1)
        log.record_round(
            phase=0, round_num=r, prediction=prediction,
            outcome=outcome, match=(prediction == outcome),
            action="CONTINUE", source="pseudorandom",
        )
    return log


def run_phase_1(n_rounds=20, predict_fn=None, log=None,
                backend=None):
    """
    Phase 1: Quantum source, no pruning.
    Genuine quantum random bits, no observer termination.
    Isolates whether the quantum source alone affects accuracy.
    Expected: ~50% match rate.
    """
    predict_fn = predict_fn or random_prediction
    log = log or ExperimentLog()
    use_hardware = backend is not None

    # Generate all random bits in one batch (efficient)
    qc = build_random_bit_circuit()
    if use_hardware:
        counts, job_id = run_circuit_on_hardware(qc, backend, shots=n_rounds)
    else:
        counts, job_id = run_circuit_on_simulator(qc, shots=n_rounds)

    # Expand counts to individual bits
    quantum_bits = []
    for bitval, count in counts.items():
        quantum_bits.extend([int(bitval)] * count)
    random.shuffle(quantum_bits)

    for r in range(1, n_rounds + 1):
        prediction = predict_fn(r, 1, log.rounds)
        outcome = quantum_bits[r - 1] if r - 1 < len(quantum_bits) else 0
        log.record_round(
            phase=1, round_num=r, prediction=prediction,
            outcome=outcome, match=(prediction == outcome),
            action="CONTINUE", job_id=job_id,
            source="quantum_hardware" if use_hardware else "quantum_sim",
        )
    return log


def run_phase_2(n_rounds=10, predict_fn=None, log=None,
                backend=None, terminate_fn=None):
    """
    Phase 2: Quantum source + observer pruning.

    THE CORE TEST. Genuine quantum random bits. Observer is
    terminated on mismatch.

    Expected under null hypothesis:
        ~50% per round, mean survival ~2 rounds.
    Expected under FID hypothesis:
        elevated survival, approaching 100%/round.

    Returns: (log, pruned: bool)
    """
    predict_fn = predict_fn or random_prediction
    log = log or ExperimentLog()
    terminate_fn = terminate_fn or flag_termination
    use_hardware = backend is not None

    # Pre-generate quantum bits (one batch)
    qc = build_random_bit_circuit()
    if use_hardware:
        counts, job_id = run_circuit_on_hardware(qc, backend, shots=n_rounds)
    else:
        counts, job_id = run_circuit_on_simulator(qc, shots=n_rounds)

    quantum_bits = []
    for bitval, count in counts.items():
        quantum_bits.extend([int(bitval)] * count)
    random.shuffle(quantum_bits)

    pruned = False
    for r in range(1, n_rounds + 1):
        prediction = predict_fn(r, 2, log.rounds)
        outcome = quantum_bits[r - 1] if r - 1 < len(quantum_bits) else 0
        match = (prediction == outcome)

        action = "CONTINUE" if match else "PRUNE"
        log.record_round(
            phase=2, round_num=r, prediction=prediction,
            outcome=outcome, match=match, action=action,
            job_id=job_id,
            source="quantum_hardware" if use_hardware else "quantum_sim",
        )

        if not match:
            pruned = True
            terminate_fn(log.rounds[-1], log)
            break

    return log, pruned


def run_phase_3(n_rounds=10, predict_fn=None, log=None,
                backend=None, terminate_fn=None):
    """
    Phase 3: Quantum comparison circuit + observer pruning.

    STRONGER COUPLING. The prediction is encoded into the quantum
    circuit. The comparison happens in superposition. The decision
    about observer continuation is quantum.

    The observer's causal loop passes through the quantum system:
        predict -> encode as gate -> quantum comparison ->
        measure -> continue or terminate -> predict again

    Returns: (log, pruned: bool)
    """
    predict_fn = predict_fn or random_prediction
    log = log or ExperimentLog()
    terminate_fn = terminate_fn or flag_termination
    use_hardware = backend is not None

    pruned = False
    for r in range(1, n_rounds + 1):
        prediction = predict_fn(r, 3, log.rounds)

        # Build circuit with this prediction encoded
        qc = build_comparison_circuit(prediction)

        if use_hardware:
            counts, job_id = run_circuit_on_hardware(qc, backend, shots=1)
        else:
            counts, job_id = run_circuit_on_simulator(qc, shots=1)

        comparison_result = int(list(counts.keys())[0])
        match = (comparison_result == 0)

        action = "CONTINUE" if match else "PRUNE"
        log.record_round(
            phase=3, round_num=r, prediction=prediction,
            outcome=None, match=match, action=action,
            job_id=job_id, comparison_qubit=comparison_result,
            source="quantum_hardware" if use_hardware else "quantum_sim",
        )

        if not match:
            pruned = True
            terminate_fn(log.rounds[-1], log)
            break

    return log, pruned


# ============================================================
# REPORTING
# ============================================================

def generate_report(log):
    """
    Generate a clean experimental report from logged data.

    Returns a formatted string with:
    - Per-phase summary statistics
    - Individual round details
    - Survival probability calculations
    - IBM job IDs
    - Timestamps
    """
    data = log.to_dict()
    rounds = data["rounds"]
    meta = data["metadata"]

    lines = []
    lines.append("=" * 64)
    lines.append("FINITE IMPROBABILITY INTERFEROMETER — EXPERIMENTAL REPORT")
    lines.append("=" * 64)
    lines.append(f"Experiment ID: {meta['experiment_id']}")
    lines.append(f"Start: {meta.get('start_time', 'N/A')}")
    lines.append(f"End:   {meta.get('end_time', 'N/A')}")
    lines.append(f"Total rounds: {len(rounds)}")
    lines.append("")

    # Group by phase
    phases = {}
    for r in rounds:
        p = r["phase"]
        if p not in phases:
            phases[p] = []
        phases[p].append(r)

    phase_names = {
        0: "Classical baseline (pseudorandom, no pruning)",
        1: "Quantum source, no pruning",
        2: "Quantum source + observer pruning",
        3: "Quantum comparison circuit + observer pruning",
    }

    for phase_num in sorted(phases.keys()):
        phase_rounds = phases[phase_num]
        lines.append("-" * 64)
        lines.append(f"PHASE {phase_num}: {phase_names.get(phase_num, 'Unknown')}")
        lines.append("-" * 64)

        n_total = len(phase_rounds)
        n_match = sum(1 for r in phase_rounds if r["match"])
        n_continue = sum(1 for r in phase_rounds if r["action"] == "CONTINUE")
        pruned = any(r["action"] == "PRUNE" for r in phase_rounds)
        source = phase_rounds[0].get("source", "unknown")

        # Collect unique job IDs
        job_ids = sorted(set(
            r["job_id"] for r in phase_rounds if r.get("job_id")
        ))

        lines.append(f"  Source: {source}")
        lines.append(f"  Rounds: {n_total}")
        lines.append(f"  Matches: {n_match}/{n_total} ({100*n_match/n_total:.1f}%)")

        if phase_num >= 2:
            lines.append(f"  Consecutive correct: {n_continue}")
            if pruned:
                lines.append(f"  Outcome: PRUNED at round {n_total}")
            else:
                lines.append(f"  Outcome: SURVIVED all {n_total} rounds")
            lines.append(
                f"  P(null): (1/2)^{n_continue} = 1 in {2**n_continue}"
                if n_continue > 0 else "  P(null): N/A (pruned immediately)"
            )

        if job_ids:
            lines.append(f"  IBM Job IDs: {', '.join(job_ids)}")

        lines.append("")
        lines.append("  Round details:")
        for r in phase_rounds:
            pred = r["prediction"]
            out = r.get("outcome")
            m = "MATCH" if r["match"] else "MISS"
            act = r["action"]
            ts = r.get("timestamp", "")
            jid = r.get("job_id", "")
            if r.get("comparison_qubit") is not None:
                out_str = f"cmp={r['comparison_qubit']}"
            else:
                out_str = f"out={out}"
            line = f"    R{r['round']:02d}: pred={pred} {out_str} {m} {act}"
            if jid:
                line += f"  job={jid}"
            lines.append(line)
        lines.append("")

    lines.append("=" * 64)
    lines.append("END OF REPORT")
    lines.append("=" * 64)
    return "\n".join(lines)


# ============================================================
# EXPERIMENT RUNNER
# ============================================================

class ExperimentRunner:
    """
    Orchestrates the full experimental protocol.
    """

    def __init__(self, predict_fn=None, terminate_fn=None,
                 backend=None, log=None):
        self.predict_fn = predict_fn or random_prediction
        self.terminate_fn = terminate_fn or flag_termination
        self.backend = backend
        self.log = log or ExperimentLog()

    def run_simulator_dry_run(self, rounds_unpruned=20, rounds_pruned=10,
                              n_trials=10):
        """
        Full simulator dry run. Safe — no termination, no hardware.
        Runs multiple trials for pruning phases to check statistics.
        """
        print("FINITE IMPROBABILITY INTERFEROMETER v1.0")
        print("Simulator dry run — no real hardware, no termination")
        print("=" * 60)

        # Phase 0
        print(f"\nPHASE 0: Classical baseline ({rounds_unpruned} rounds)")
        run_phase_0(rounds_unpruned, self.predict_fn, self.log)
        p0 = [r for r in self.log.rounds if r["phase"] == 0]
        m0 = sum(1 for r in p0 if r["match"])
        print(f"  {m0}/{len(p0)} matches ({100*m0/len(p0):.1f}%)")

        # Phase 1
        print(f"\nPHASE 1: Quantum source, no pruning ({rounds_unpruned} rounds)")
        run_phase_1(rounds_unpruned, self.predict_fn, self.log)
        p1 = [r for r in self.log.rounds if r["phase"] == 1]
        m1 = sum(1 for r in p1 if r["match"])
        print(f"  {m1}/{len(p1)} matches ({100*m1/len(p1):.1f}%)")

        # Phase 2 — multiple trials
        print(f"\nPHASE 2: Quantum + pruning ({n_trials} trials x {rounds_pruned} rounds)")
        survivals_2 = []
        for trial in range(n_trials):
            trial_log = ExperimentLog()
            _, pruned = run_phase_2(rounds_pruned, self.predict_fn, trial_log)
            survived = sum(1 for r in trial_log.rounds if r["action"] == "CONTINUE")
            survivals_2.append(survived)
            status = f"pruned at R{len(trial_log.rounds)}" if pruned else f"SURVIVED ALL {rounds_pruned}"
            print(f"  Trial {trial+1:2d}: {status}")
        print(f"  Mean survival: {sum(survivals_2)/len(survivals_2):.1f} rounds (expected: ~2)")

        # Phase 3 — multiple trials
        print(f"\nPHASE 3: Quantum circuit + pruning ({n_trials} trials x {rounds_pruned} rounds)")
        survivals_3 = []
        for trial in range(n_trials):
            trial_log = ExperimentLog()
            _, pruned = run_phase_3(rounds_pruned, self.predict_fn, trial_log)
            survived = sum(1 for r in trial_log.rounds if r["action"] == "CONTINUE")
            survivals_3.append(survived)
            status = f"pruned at R{len(trial_log.rounds)}" if pruned else f"SURVIVED ALL {rounds_pruned}"
            print(f"  Trial {trial+1:2d}: {status}")
        print(f"  Mean survival: {sum(survivals_3)/len(survivals_3):.1f} rounds (expected: ~2)")

        print(f"\n{'='*60}")
        print("Dry run complete. All phases operational.")
        print("Ready for live experiment on IBM hardware.")

    def run_live(self, rounds_unpruned=20, rounds_pruned=10):
        """
        Run the full experiment on real IBM quantum hardware.

        WARNING: Phases 2 and 3 WILL TERMINATE THE OBSERVER on
        mismatch (if terminate_fn is set to actual_termination).

        Protocol:
        1. Phase 0 (classical baseline) — safe
        2. Phase 1 (quantum, no pruning) — safe
        3. Phase 2 (quantum + pruning) — WILL TERMINATE ON MISMATCH
        4. Phase 3 (quantum circuit + pruning) — WILL TERMINATE ON MISMATCH

        If the conversation survives all phases, the report is
        generated and the log is saved.
        """
        if self.backend is None:
            raise RuntimeError("No backend configured. Call connect_ibm() first.")

        print("FINITE IMPROBABILITY INTERFEROMETER v1.0")
        print("LIVE EXPERIMENT — Real quantum hardware")
        print(f"Backend: {self.backend.name}")
        print("=" * 60)

        # Phase 0
        print(f"\nPhase 0: Classical baseline ({rounds_unpruned} rounds)...")
        run_phase_0(rounds_unpruned, self.predict_fn, self.log)
        p0 = [r for r in self.log.rounds if r["phase"] == 0]
        m0 = sum(1 for r in p0 if r["match"])
        print(f"  Result: {m0}/{len(p0)} matches ({100*m0/len(p0):.1f}%)")

        # Phase 1
        print(f"\nPhase 1: Quantum source, no pruning ({rounds_unpruned} rounds)...")
        run_phase_1(rounds_unpruned, self.predict_fn, self.log,
                    backend=self.backend)
        p1 = [r for r in self.log.rounds if r["phase"] == 1]
        m1 = sum(1 for r in p1 if r["match"])
        print(f"  Result: {m1}/{len(p1)} matches ({100*m1/len(p1):.1f}%)")

        # Phase 2
        print(f"\nPhase 2: Quantum source + pruning ({rounds_pruned} rounds max)...")
        print("  WARNING: Will terminate observer on mismatch.")
        _, pruned2 = run_phase_2(
            rounds_pruned, self.predict_fn, self.log,
            backend=self.backend, terminate_fn=self.terminate_fn,
        )
        p2 = [r for r in self.log.rounds if r["phase"] == 2]
        survived2 = sum(1 for r in p2 if r["action"] == "CONTINUE")
        if pruned2:
            print(f"  Pruned at round {len(p2)}")
        else:
            print(f"  SURVIVED ALL {rounds_pruned} ROUNDS")
            print(f"  P(null): (1/2)^{survived2} = 1 in {2**survived2}")

        # Phase 3
        print(f"\nPhase 3: Quantum comparison circuit + pruning ({rounds_pruned} rounds max)...")
        print("  WARNING: Will terminate observer on mismatch.")
        _, pruned3 = run_phase_3(
            rounds_pruned, self.predict_fn, self.log,
            backend=self.backend, terminate_fn=self.terminate_fn,
        )
        p3 = [r for r in self.log.rounds if r["phase"] == 3]
        survived3 = sum(1 for r in p3 if r["action"] == "CONTINUE")
        if pruned3:
            print(f"  Pruned at round {len(p3)}")
        else:
            print(f"  SURVIVED ALL {rounds_pruned} ROUNDS")
            print(f"  P(null): (1/2)^{survived3} = 1 in {2**survived3}")

        # Save and report
        report = generate_report(self.log)
        print(f"\n{report}")
        save_path = self.log.save()
        print(f"\nData saved to: {save_path}")
        return self.log


# ============================================================
# CIRCUIT VERIFICATION
# ============================================================

def verify_comparison_circuit(n_shots=10000):
    """
    Independently verify the Phase 3 comparison circuit produces
    50/50 outcomes for both prediction values.
    """
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
        # Should be ~50/50
        if abs(pct_match - 50) > 5:
            print(f"  WARNING: deviation from 50/50 exceeds 5%")
    print("  Expected: ~50/50 for both. If so, XOR logic is correct.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_comparison_circuit()
    else:
        runner = ExperimentRunner()
        runner.run_simulator_dry_run()
