"""
Bulk quantum-bit harvester for the Simulation Substrate Probe.

Efficiency insight: a single 1-qubit circuit (H |0>, measure) run for N SHOTS
yields N genuine quantum random bits for essentially one circuit's worth of QPU
time. Shots are cheap; circuits/queueing are the cost. So 100,000 bits is a few
seconds of QPU — trivial against the free 10-min/month tier.

Like the FID, the sandbox cannot reach IBM directly, so this runs on the GitHub
Actions relay. Two modes:

  python harvest_bits.py request 100000
      Writes quantum_requests/substrate_request.json (N shots). Committing/pushing
      that file is what triggers a harvest — left to a deliberate, QPU-spending
      decision, NOT done automatically here.

  python harvest_bits.py run
      Executed BY the relay runner (unrestricted network). Reads the request,
      pulls the bits from IBM hardware, writes probes/simulation_substrate/
      harvest_<backend>.json. Mirrors src/quantum_runner.py.
"""
import json
import sys
from pathlib import Path

IBM_TOKEN = "emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF"
IBM_INSTANCE = ("crn:v1:bluemix:public:quantum-computing:us-east:"
                "a/24844eaa090d4e74879fc65799972209:"
                "077c6ad7-29a2-4c16-a6fa-929fc261e6b2::")
REQ = Path("quantum_requests/substrate_request.json")
OUT_DIR = Path("probes/simulation_substrate")


def make_request(n_shots):
    REQ.parent.mkdir(parents=True, exist_ok=True)
    REQ.write_text(json.dumps({
        "probe": "simulation_substrate",
        "circuit": "single_qubit_hadamard",
        "shots": int(n_shots),
        "note": "H|0> measured n_shots times → n_shots genuine quantum bits",
    }, indent=2))
    print(f"wrote {REQ} requesting {n_shots} shots.")
    print("To harvest: commit & push this file (spends a few seconds of QPU "
          "time). The relay workflow runs harvest_bits.py run and commits the bits.")


def run_harvest():
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    req = json.loads(REQ.read_text())
    shots = int(req["shots"])

    service = QiskitRuntimeService(token=IBM_TOKEN, instance=IBM_INSTANCE,
                                   channel="ibm_cloud")
    backend = min(service.backends(operational=True, simulator=False),
                  key=lambda b: b.status().pending_jobs)
    print(f"backend: {backend.name}  (queue {backend.status().pending_jobs})")

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa = pm.run(qc)

    sampler = SamplerV2(mode=backend)
    job = sampler.run([isa], shots=shots)
    print(f"job id: {job.job_id()}")
    res = job.result()[0]
    # per-shot bit string from the classical register
    bits = [int(b) for b in res.data.c.get_bitstrings()]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"harvest_{backend.name}.json"
    out.write_text(json.dumps({
        "backend": backend.name, "job_id": job.job_id(),
        "shots": shots, "n_bits": len(bits), "random_bits": bits,
    }))
    print(f"harvested {len(bits)} genuine quantum bits → {out}")
    print(f"analyse with: python probes/simulation_substrate/substrate_probe.py {out}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "request":
        make_request(sys.argv[2] if len(sys.argv) > 2 else 100000)
    elif cmd == "run":
        run_harvest()
    else:
        print(__doc__)
