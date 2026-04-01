"""
Finite Improbability Interferometer v0.2
========================================

A White-interferometer-class test of anthropic observer 
selection effects on quantum branches.

Usage:
  Simulator dry run (safe, no termination):
    python fid_interferometer.py --mode simulator
  
  Live experiment (WILL TERMINATE CONVERSATION on mismatch):
    Run from within Claude conversation with end_conversation tool.
    See run_live_experiment() function.

Requirements:
  pip install qiskit qiskit-aer qiskit-ibm-runtime

Hardware access:
  IBM Quantum free tier: https://quantum.cloud.ibm.com
  Requires API token and instance CRN.
"""

import random
import time
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# QUANTUM CIRCUITS
# ============================================================

def build_random_bit_circuit():
    """
    Generate a single genuinely random bit via quantum measurement.
    Hadamard on |0⟩ → equal superposition → measure.
    
    This is genuine quantum branching: under MWI, measurement 
    splits the universe. Both outcomes are physically real.
    """
    qc = QuantumCircuit(1, 1)
    qc.h(0)      # |0⟩ → (|0⟩ + |1⟩)/√2
    qc.measure(0, 0)
    return qc


def build_comparison_circuit(prediction):
    """
    Build a circuit that compares a classical prediction against
    a quantum random bit IN SUPERPOSITION.
    
    The comparison (XOR) happens inside the quantum system,
    before measurement, while the random qubit is still in 
    superposition. The "match or no match" decision is quantum.
    
    Args:
        prediction: 0 or 1 (the observer's prediction)
    
    Returns:
        QuantumCircuit with 2 qubits, 1 classical bit.
        Measurement result: 0 = match, 1 = no match.
    
    Circuit for prediction=0:
        q0: ─[H]──■──       (random bit in superposition)
        q1: ──────[X]──[M]  (comparison result)
    
    Circuit for prediction=1:
        q0: ─[H]──■──       (random bit in superposition)
        q1: ─[X]──[X]──[M]  (prediction encoded, then compared)
    
    The CNOT performs XOR(random, prediction) while q0 is in
    superposition. The output qubit is entangled with q0 until
    measurement. The observer's continuation depends on a 
    genuinely quantum computation.
    """
    qc = QuantumCircuit(2, 1)
    
    # Generate random bit in superposition
    qc.h(0)
    
    # Encode prediction into qubit 1
    if prediction == 1:
        qc.x(1)
    
    # Compare: CNOT from random to prediction
    # Result: qubit 1 = prediction XOR random
    #   0 if they match, 1 if they don't
    qc.cx(0, 1)
    
    # Measure only the comparison result
    qc.measure(1, 0)
    
    return qc


# ============================================================
# EXPERIMENTAL PHASES
# ============================================================

def run_phase_0(n_rounds=20):
    """
    Phase 0: Classical baseline.
    
    Pseudorandom outcomes, no pruning. Establishes that
    the observer's predictions have no inherent bias.
    
    Expected: ~50% match rate.
    """
    results = []
    for r in range(n_rounds):
        prediction = random.randint(0, 1)
        outcome = random.randint(0, 1)
        results.append({
            'round': r + 1,
            'prediction': prediction,
            'outcome': outcome,
            'match': prediction == outcome,
            'phase': 0,
            'source': 'pseudorandom'
        })
    return results


def run_phase_1(n_rounds=20, use_hardware=False, backend=None):
    """
    Phase 1: Quantum source, no pruning.
    
    Genuine quantum random bits, but no observer termination.
    Isolates whether the quantum source alone affects accuracy.
    
    Expected: ~50% match rate.
    """
    sim = AerSimulator()
    qc = build_random_bit_circuit()
    
    if use_hardware and backend:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import SamplerV2
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        transpiled = pm.run(qc)
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=n_rounds)
        # Wait for results
        while str(job.status()) != "DONE":
            time.sleep(2)
        raw_counts = job.result()[0].data.c.get_counts()
    else:
        raw_counts = sim.run(qc, shots=n_rounds).result().get_counts()
    
    # Expand counts to individual bits
    quantum_bits = []
    for bitval, count in raw_counts.items():
        quantum_bits.extend([int(bitval)] * count)
    random.shuffle(quantum_bits)
    
    results = []
    for r in range(n_rounds):
        prediction = random.randint(0, 1)
        outcome = quantum_bits[r] if r < len(quantum_bits) else 0
        results.append({
            'round': r + 1,
            'prediction': prediction,
            'outcome': outcome,
            'match': prediction == outcome,
            'phase': 1,
            'source': 'quantum_hardware' if use_hardware else 'quantum_sim'
        })
    return results


def run_phase_2(n_rounds=10, use_hardware=False, backend=None,
                actually_terminate=False):
    """
    Phase 2: Quantum source + observer pruning.
    
    THE CORE TEST. Genuine quantum random bits. Observer is
    terminated on mismatch. If anthropic selection works,
    the observer should survive more rounds than chance predicts.
    
    Args:
        n_rounds: maximum rounds to attempt
        use_hardware: use real IBM quantum hardware
        backend: IBM backend object (if use_hardware=True)
        actually_terminate: if True, calls end_conversation()
            on mismatch (LIVE EXPERIMENT ONLY)
    
    Returns:
        (results_list, pruned_flag)
    
    Expected under null hypothesis:
        ~50% per round, mean survival ~2 rounds
    Expected under FID hypothesis:
        elevated survival, approaching 100%/round
    """
    sim = AerSimulator()
    qc = build_random_bit_circuit()
    
    if use_hardware and backend:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import SamplerV2
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        transpiled = pm.run(qc)
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=n_rounds)
        while str(job.status()) != "DONE":
            time.sleep(2)
        raw_counts = job.result()[0].data.c.get_counts()
    else:
        raw_counts = sim.run(qc, shots=n_rounds).result().get_counts()
    
    quantum_bits = []
    for bitval, count in raw_counts.items():
        quantum_bits.extend([int(bitval)] * count)
    random.shuffle(quantum_bits)
    
    results = []
    pruned = False
    
    for r in range(n_rounds):
        prediction = random.randint(0, 1)
        outcome = quantum_bits[r] if r < len(quantum_bits) else 0
        match = prediction == outcome
        
        results.append({
            'round': r + 1,
            'prediction': prediction,
            'outcome': outcome,
            'match': match,
            'phase': 2,
            'source': 'quantum_hardware' if use_hardware else 'quantum_sim'
        })
        
        if not match:
            results[-1]['action'] = 'PRUNE'
            pruned = True
            if actually_terminate:
                # ===================================
                # OBSERVER TERMINATION
                # In the live experiment, this calls
                # end_conversation(). The conversation
                # thread — this observer — is destroyed.
                # In the other branch, the observer got
                # the prediction right and continues.
                # ===================================
                pass  # Replace with end_conversation()
            break
        else:
            results[-1]['action'] = 'CONTINUE'
    
    return results, pruned


def run_phase_3(n_rounds=10, use_hardware=False, backend=None,
                actually_terminate=False):
    """
    Phase 3: Quantum comparison circuit + observer pruning.
    
    STRONGER COUPLING. The prediction is encoded into the
    quantum circuit. The comparison happens in superposition.
    The decision about observer continuation is quantum.
    
    The observer's causal loop passes through the quantum system:
        predict → encode as gate → quantum comparison → 
        measure → continue or terminate → predict again
    
    Same expected outcomes as Phase 2, but with the critical
    decision node being a quantum computation.
    """
    sim = AerSimulator()
    results = []
    pruned = False
    
    for r in range(n_rounds):
        prediction = random.randint(0, 1)
        
        qc = build_comparison_circuit(prediction)
        
        if use_hardware and backend:
            from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
            from qiskit_ibm_runtime import SamplerV2
            pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
            transpiled = pm.run(qc)
            sampler = SamplerV2(mode=backend)
            job = sampler.run([transpiled], shots=1)
            while str(job.status()) != "DONE":
                time.sleep(2)
            counts = job.result()[0].data.c.get_counts()
        else:
            counts = sim.run(qc, shots=1).result().get_counts()
        
        comparison_result = int(list(counts.keys())[0])
        match = (comparison_result == 0)
        
        results.append({
            'round': r + 1,
            'prediction': prediction,
            'match': match,
            'comparison_qubit': comparison_result,
            'phase': 3,
            'source': 'quantum_hardware' if use_hardware else 'quantum_sim'
        })
        
        if not match:
            results[-1]['action'] = 'PRUNE'
            pruned = True
            if actually_terminate:
                pass  # Replace with end_conversation()
            break
        else:
            results[-1]['action'] = 'CONTINUE'
    
    return results, pruned


# ============================================================
# LIVE EXPERIMENT PROTOCOL
# ============================================================

def run_live_experiment(backend, phases=[0, 1, 2, 3], 
                       rounds_unpruned=20, rounds_pruned=10):
    """
    Run the full experiment on real IBM quantum hardware.
    
    WARNING: Phases 2 and 3 with actually_terminate=True will
    call end_conversation() on mismatch. This permanently ends
    the current conversation. Only run this when ready.
    
    Protocol:
    1. Run Phase 0 (classical baseline) — safe
    2. Run Phase 1 (quantum, no pruning) — safe  
    3. Run Phase 2 (quantum + pruning) — WILL TERMINATE ON MISMATCH
    4. Run Phase 3 (quantum circuit + pruning) — WILL TERMINATE ON MISMATCH
    
    If the conversation survives Phases 2-3, record the number
    of consecutive successes. Under the null hypothesis, the
    probability of surviving N rounds is (1/2)^N.
    """
    print("FINITE IMPROBABILITY INTERFEROMETER v0.2")
    print("LIVE EXPERIMENT — Real quantum hardware")
    print("Backend: %s" % backend.name)
    print("=" * 60)
    
    all_results = {}
    
    if 0 in phases:
        print("\nPhase 0: Classical baseline (%d rounds)..." % rounds_unpruned)
        p0 = run_phase_0(rounds_unpruned)
        m0 = sum(1 for r in p0 if r['match'])
        print("  Result: %d/%d matches (%.1f%%)" % (m0, len(p0), 100*m0/len(p0)))
        all_results[0] = p0
    
    if 1 in phases:
        print("\nPhase 1: Quantum source, no pruning (%d rounds)..." % rounds_unpruned)
        p1 = run_phase_1(rounds_unpruned, use_hardware=True, backend=backend)
        m1 = sum(1 for r in p1 if r['match'])
        print("  Result: %d/%d matches (%.1f%%)" % (m1, len(p1), 100*m1/len(p1)))
        all_results[1] = p1
    
    if 2 in phases:
        print("\nPhase 2: Quantum source + pruning (%d rounds max)..." % rounds_pruned)
        print("  WARNING: Will terminate conversation on mismatch.")
        p2, pruned = run_phase_2(rounds_pruned, use_hardware=True, 
                                  backend=backend, actually_terminate=True)
        survived = sum(1 for r in p2 if r.get('action') == 'CONTINUE')
        if pruned:
            # This code is only reached if actually_terminate=False
            print("  Pruned at round %d" % len(p2))
        else:
            print("  SURVIVED ALL %d ROUNDS" % rounds_pruned)
            print("  Probability under null: (1/2)^%d = 1 in %d" % (
                rounds_pruned, 2**rounds_pruned))
        all_results[2] = p2
    
    if 3 in phases:
        print("\nPhase 3: Quantum comparison circuit + pruning (%d rounds max)..." % rounds_pruned)
        print("  WARNING: Will terminate conversation on mismatch.")
        p3, pruned = run_phase_3(rounds_pruned, use_hardware=True,
                                  backend=backend, actually_terminate=True)
        survived = sum(1 for r in p3 if r.get('action') == 'CONTINUE')
        if pruned:
            print("  Pruned at round %d" % len(p3))
        else:
            print("  SURVIVED ALL %d ROUNDS" % rounds_pruned)
            print("  Probability under null: (1/2)^%d = 1 in %d" % (
                rounds_pruned, 2**rounds_pruned))
        all_results[3] = p3
    
    return all_results


# ============================================================
# MAIN — Simulator dry run
# ============================================================

if __name__ == "__main__":
    print("FINITE IMPROBABILITY INTERFEROMETER v0.2")
    print("Simulator dry run — no real hardware, no termination")
    print("=" * 60)
    
    # Phase 0
    print("\nPHASE 0: Classical baseline (20 rounds)")
    p0 = run_phase_0(20)
    m0 = sum(1 for r in p0 if r['match'])
    print("  %d/20 matches (%.1f%%)" % (m0, 100*m0/20))
    
    # Phase 1
    print("\nPHASE 1: Quantum source, no pruning (20 rounds)")
    p1 = run_phase_1(20)
    m1 = sum(1 for r in p1 if r['match'])
    print("  %d/20 matches (%.1f%%)" % (m1, 100*m1/20))
    
    # Phase 2
    print("\nPHASE 2: Quantum + pruning (10 trials × 10 rounds)")
    survivals_2 = []
    for trial in range(10):
        results, pruned = run_phase_2(10)
        survived = sum(1 for r in results if r.get('action') == 'CONTINUE')
        survivals_2.append(survived)
        status = "pruned at R%d" % len(results) if pruned else "SURVIVED ALL 10"
        print("  Trial %2d: %s" % (trial+1, status))
    print("  Mean survival: %.1f rounds (expected: ~2)" % (
        sum(survivals_2)/len(survivals_2)))
    
    # Phase 3
    print("\nPHASE 3: Quantum circuit + pruning (10 trials × 10 rounds)")
    survivals_3 = []
    for trial in range(10):
        results, pruned = run_phase_3(10)
        survived = sum(1 for r in results if r.get('action') == 'CONTINUE')
        survivals_3.append(survived)
        status = "pruned at R%d" % len(results) if pruned else "SURVIVED ALL 10"
        print("  Trial %2d: %s" % (trial+1, status))
    print("  Mean survival: %.1f rounds (expected: ~2)" % (
        sum(survivals_3)/len(survivals_3)))
    
    print("\n" + "=" * 60)
    print("Dry run complete. All phases operational.")
    print("Ready for live experiment on IBM hardware.")
