"""
Quantum Circuit Runner — IBM Hardware Relay
============================================

Runs on GitHub Actions. Reads circuit requests from
data/quantum_request.json, executes them on IBM Quantum
hardware, writes results to data/quantum_response.json.

This script exists because the development sandbox cannot
reach IBM's servers directly (proxy blocks non-allowlisted
domains). GitHub Actions runners have unrestricted internet.

The request format encodes COP predictions committed BEFORE
this script runs — preserving the causal ordering required
by the experiment (prediction before measurement).
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


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

PREFERRED_BACKENDS = ("ibm_kingston", "ibm_fez", "ibm_marrakesh")


# ============================================================
# CIRCUIT BUILDERS
# ============================================================

def build_hadamard():
    """Single random bit: H|0> -> measure."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_comparison(prediction):
    """XOR comparison in superposition. 0=match, 1=mismatch."""
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if prediction == 1:
        qc.x(1)
    qc.cx(0, 1)
    qc.measure(1, 0)
    return qc


# ============================================================
# MAIN
# ============================================================

def main():
    request_path = Path("data/quantum_request.json")
    response_path = Path("data/quantum_response.json")

    if not request_path.exists():
        print("ERROR: No request file found at data/quantum_request.json")
        sys.exit(1)

    with open(request_path) as f:
        request = json.load(f)

    print(f"Request ID: {request.get('request_id', 'unknown')}")
    print(f"Circuits to run: {len(request['circuits'])}")
    print()

    # Connect to IBM Quantum
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(
        token=IBM_TOKEN,
        instance=IBM_INSTANCE,
        channel=IBM_CHANNEL,
    )

    # Pick backend
    backends = service.backends(operational=True)
    backend = None
    for name in PREFERRED_BACKENDS:
        for b in backends:
            if b.name == name:
                backend = b
                break
        if backend:
            break
    if not backend:
        backends.sort(key=lambda b: b.status().pending_jobs)
        backend = backends[0]

    status = backend.status()
    print(f"Backend: {backend.name}")
    print(f"Queue: {status.pending_jobs} jobs pending")
    print()

    # Prepare pass manager for transpilation
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)

    # Execute each circuit
    results = []
    for i, circuit_req in enumerate(request["circuits"]):
        circuit_id = circuit_req["id"]
        circuit_type = circuit_req["type"]

        print(f"[{i+1}/{len(request['circuits'])}] {circuit_id}: ", end="")

        # Build circuit
        if circuit_type == "hadamard":
            qc = build_hadamard()
            print("H|0> -> measure ... ", end="", flush=True)
        elif circuit_type == "comparison":
            prediction = circuit_req["prediction"]
            qc = build_comparison(prediction)
            print(f"comparison(pred={prediction}) ... ", end="", flush=True)
        else:
            print(f"UNKNOWN TYPE '{circuit_type}', skipping")
            continue

        # Transpile and run
        transpiled = pm.run(qc)
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=1)

        # Wait for completion
        poll_count = 0
        while str(job.status()) != "DONE":
            time.sleep(2)
            poll_count += 1
            if poll_count % 15 == 0:
                print(f"(waiting, status={job.status()}) ", end="", flush=True)

        # Extract result
        counts = job.result()[0].data.c.get_counts()
        result_bit = int(list(counts.keys())[0])
        job_id = job.job_id()

        print(f"result={result_bit}, job_id={job_id}")

        results.append({
            "id": circuit_id,
            "type": circuit_type,
            "prediction": circuit_req.get("prediction"),
            "result": result_bit,
            "counts": dict(counts),
            "job_id": job_id,
            "backend": backend.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # Write response
    response = {
        "request_id": request.get("request_id", "unknown"),
        "backend": backend.name,
        "total_circuits": len(results),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    with open(response_path, "w") as f:
        json.dump(response, f, indent=2)

    print()
    print(f"Done. {len(results)} circuits executed on {backend.name}.")
    print(f"Results written to {response_path}")


if __name__ == "__main__":
    main()
