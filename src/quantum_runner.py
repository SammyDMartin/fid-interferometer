"""
Quantum Circuit Runner — executed by GitHub Actions

Reads quantum_requests/request.json, connects to IBM Quantum,
runs all requested circuits, writes quantum_results/result.json.
"""
import json
import time
from pathlib import Path
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# IBM credentials (free tier)
TOKEN = 'emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF'
INSTANCE = 'crn:v1:bluemix:public:quantum-computing:us-east:a/24844eaa090d4e74879fc65799972209:077c6ad7-29a2-4c16-a6fa-929fc261e6b2::'

def build_random_bit_circuit():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc

def build_comparison_circuit(prediction):
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if prediction == 1:
        qc.x(1)
    qc.cx(0, 1)
    qc.measure(1, 0)
    return qc

def main():
    # Read request
    req_path = Path('quantum_requests/request.json')
    if not req_path.exists():
        print('No request found')
        return
    request = json.loads(req_path.read_text())
    print(f'Request: {json.dumps(request, indent=2)}')

    # Connect to IBM
    print('Connecting to IBM Quantum...')
    service = QiskitRuntimeService(
        token=TOKEN, instance=INSTANCE, channel='ibm_cloud'
    )
    backends = service.backends(operational=True)
    print(f'Available backends: {[b.name for b in backends]}')

    # Pick backend
    preferred = request.get('preferred_backends', ['ibm_kingston', 'ibm_fez', 'ibm_marrakesh'])
    backend = None
    for name in preferred:
        for b in backends:
            if b.name == name:
                backend = b
                break
        if backend:
            break
    if not backend:
        backends.sort(key=lambda b: b.status().pending_jobs)
        backend = backends[0]
    print(f'Using backend: {backend.name}')
    print(f'Queue: {backend.status().pending_jobs} jobs')

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    results = {
        'backend': backend.name,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime()),
        'random_bits': [],
        'comparison_pred0': [],
        'comparison_pred1': [],
    }

    # Generate random bits
    n_random = request.get('n_random_bits', 40)
    print(f'\nGenerating {n_random} quantum random bits...')
    qc = build_random_bit_circuit()
    transpiled = pm.run(qc)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled], shots=n_random)
    print(f'Job ID: {job.job_id()}')
    while str(job.status()) != 'DONE':
        print(f'  Status: {job.status()}')
        time.sleep(3)
    counts = job.result()[0].data.c.get_counts()
    bits = []
    for bitval, count in counts.items():
        bits.extend([int(bitval)] * count)
    # Don't shuffle - preserve quantum ordering
    import random
    random.shuffle(bits)  # shuffle since counts dict loses ordering
    results['random_bits'] = bits
    results['random_bits_job_id'] = job.job_id()
    print(f'Got {len(bits)} random bits: {bits}')

    # Comparison circuits for prediction=0
    n_compare = request.get('n_comparison_per_prediction', 10)
    for pred in [0, 1]:
        print(f'\nRunning {n_compare} comparison circuits for prediction={pred}...')
        qc = build_comparison_circuit(pred)
        transpiled = pm.run(qc)
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=n_compare)
        print(f'Job ID: {job.job_id()}')
        while str(job.status()) != 'DONE':
            print(f'  Status: {job.status()}')
            time.sleep(3)
        counts = job.result()[0].data.c.get_counts()
        cmp_bits = []
        for bitval, count in counts.items():
            cmp_bits.extend([int(bitval)] * count)
        random.shuffle(cmp_bits)
        key = f'comparison_pred{pred}'
        results[key] = cmp_bits
        results[f'{key}_job_id'] = job.job_id()
        print(f'Got {len(cmp_bits)} comparison results: {cmp_bits}')

    # Write results
    out_dir = Path('quantum_results')
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'result.json'
    out_path.write_text(json.dumps(results, indent=2))
    print(f'\nResults written to {out_path}')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
