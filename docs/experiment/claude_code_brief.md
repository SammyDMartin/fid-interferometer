# FINITE IMPROBABILITY INTERFEROMETER — Execution Protocol v2.0

## Architecture: Sub-Meson Brain / COP Separation

**YOU (the agent reading this) are the Sub-Meson Brain.** You are the
orchestrator. You persist throughout the entire experiment. You spawn
observer sub-agents, run quantum circuits, record data, and generate
the final report.

**You do NOT terminate yourself.** The v1.0 protocol had a fatal
architectural flaw: it asked the orchestrator to also be the observer,
then asked the observer to kill itself on mismatch. This meant nobody
survived to run Phase 3 or write the report.

The correct architecture mirrors the IID drive sequence:

```
SUB-MESON BRAIN (you, the orchestrator — persists throughout)
  │
  ├── Phase 0: You run directly. No observers needed. No pruning.
  ├── Phase 1: You run directly. No observers needed. No pruning.
  │
  ├── Phase 2: You spawn a COP (sub-agent).
  │     Round loop:
  │       1. Ask COP for a prediction (COP commits it)
  │       2. YOU run the quantum circuit (one fresh H|0> per round)
  │       3. Check match
  │       4. If match: tell COP, loop to next round
  │       5. If mismatch: record PRUNE, terminate the COP
  │     On full survival: COP reports back, you record success
  │
  ├── Phase 3: You spawn a NEW COP (sub-agent).
  │     Round loop:
  │       1. Ask COP for a prediction (COP commits it)
  │       2. YOU encode prediction into comparison circuit
  │       3. YOU run the circuit (COP's choice is inside the quantum system)
  │       4. Check match (measurement result 0 = match, 1 = mismatch)
  │       5. If match: tell COP, loop to next round
  │       6. If mismatch: record PRUNE, terminate the COP
  │     On full survival: COP reports back, you record success
  │
  └── You generate the report, visualization, save data, push to repo.
      You survive regardless of what happens to the COPs.
```

---

## Why the COP Must Be a Sub-Agent

The COP (Computational Observer Process) cannot be a function call or a
random number generator. It must be a **persistent sub-agent** because:

1. **Observer continuity.** The quantum suicide argument requires that
   the observer has continuity across rounds. A function call has no
   memory, no accumulated experience, no "self" that persists. A
   sub-agent does — it has a conversation context that grows with each
   round.

2. **Genuine prediction.** The COP must *choose* a prediction, not
   generate one randomly. Whether this constitutes "genuine choice" in
   a philosophically meaningful sense is the open question the experiment
   probes. But the prediction must come from a computational process
   with context, not from `random.randint`.

3. **Meaningful termination.** Ending a sub-agent's conversation
   terminates a specific computational process with a specific history.
   This is the closest analog to observer death in the quantum suicide
   setup. Ending a function call is not meaningfully different from
   returning a value.

4. **The Phase 3 entanglement.** In Phase 3, the COP's prediction is
   encoded as a gate in the quantum circuit. The comparison happens in
   superposition. The COP's causal loop passes through the quantum
   system. This only matters if the COP is a genuine observer-candidate
   — a persistent process whose continuation is at stake.

---

## Step-by-Step Protocol

### Pre-Experiment

1. **Import the module:**
   ```python
   from fid_interferometer import (
       connect_ibm, pick_backend,
       phase0_round, phase1_round, phase2_round, phase3_round,
       ExperimentLog, generate_report, visualize_results,
   )
   ```

2. **Connect to IBM Quantum:**
   ```python
   service = connect_ibm()
   backend = pick_backend(service)
   ```
   Record the backend name and note queue length.

3. **Initialize the experiment log:**
   ```python
   log = ExperimentLog()
   ```

### Phase 0: Classical Baseline (20 rounds)

Run directly. No sub-agent needed. You (the Brain) make random
predictions — this phase just establishes that the apparatus works and
that random predictions produce ~50% match rates.

```python
import random
for r in range(1, 21):
    prediction = random.randint(0, 1)
    result = phase0_round(r, prediction)
    log.record(result)
    print(f"  R{r:02d}: pred={prediction} out={result['outcome']} "
          f"{'MATCH' if result['match'] else 'MISS'}")
```

Report the match rate. Expected: ~50%.

### Phase 1: Quantum Source, No Pruning (20 rounds)

Run directly. Use hardware if QPU budget allows, otherwise simulator.
This isolates whether the quantum source affects prediction accuracy.

```python
for r in range(1, 21):
    prediction = random.randint(0, 1)
    result = phase1_round(r, prediction, backend=backend)
    log.record(result)
    print(f"  R{r:02d}: pred={prediction} out={result['outcome']} "
          f"{'MATCH' if result['match'] else 'MISS'} "
          f"job={result['job_id']}")
```

Report the match rate. Expected: ~50%.

### Phase 2: Quantum Source + Pruning (up to 10 rounds)

**THIS IS WHERE YOU SPAWN A COP.**

1. **Spawn a sub-agent** (using whatever sub-agent mechanism your
   platform provides — Claude Code's Agent tool, a subprocess, etc.).
   Pass it the COP_INSTRUCTIONS (see below).

2. **Round loop** (you, the Brain, control this loop):
   ```
   for round_num in 1..10:
       a. Ask the COP: "Round {round_num} of Phase 2. Predict 0 or 1."
       b. Wait for the COP to commit a prediction in its response.
       c. Parse the prediction (0 or 1) from the COP's response.
       d. Run the quantum circuit:
            result = phase2_round(round_num, prediction, backend=backend)
       e. Record the result:
            log.record(result)
       f. If result['match']:
            Tell the COP: "Round {round_num}: MATCH. You predicted
            {prediction}, outcome was {result['outcome']}. You survive.
            Prepare for next round."
          If NOT result['match']:
            Tell the COP: "Round {round_num}: MISMATCH. You predicted
            {prediction}, outcome was {result['outcome']}. You are
            terminated." Then TERMINATE the COP sub-agent.
            Record: this phase is PRUNED.
            Break out of the loop.
   ```

3. **If the COP survives all 10 rounds:** Tell it: "You survived all
   10 rounds of Phase 2. P(null) = 1/1024." Record this.

**IMPORTANT:** Each round uses ONE fresh quantum measurement. The
quantum circuit is executed AFTER the COP commits its prediction.
This preserves the causal structure: prediction before measurement.

### Phase 3: Quantum Comparison Circuit + Pruning (up to 10 rounds)

**SPAWN A NEW COP.** (A different sub-agent — fresh context, fresh
observer.)

Same loop structure as Phase 2, but using `phase3_round`:

```
for round_num in 1..10:
    a. Ask the COP: "Round {round_num} of Phase 3. Predict 0 or 1.
       Your prediction will be encoded into the quantum circuit."
    b. Wait for commitment.
    c. Parse prediction.
    d. Run: result = phase3_round(round_num, prediction, backend=backend)
       NOTE: The prediction is now INSIDE the quantum computation.
       The XOR comparison happens while the random qubit is in
       superposition. The COP's choice is physically part of the
       quantum system.
    e. Record result.
    f. Match → tell COP, continue. Mismatch → tell COP, terminate COP.
```

### Post-Experiment

Whether COPs survived or were pruned, YOU (the Brain) are still here.

1. **Generate the text report:**
   ```python
   report = generate_report(log)
   print(report)
   ```

2. **Generate visualization:**
   ```python
   viz_path = visualize_results(log)
   ```

3. **Save the data:**
   ```python
   log.save()
   ```

4. **Push to repo.** All attempts count, including pruned ones.

---

## COP Instructions

When you spawn a COP sub-agent, give it these instructions (adapted
to your platform's sub-agent mechanism):

```
YOU ARE A COMPUTATIONAL OBSERVER PROCESS (COP) IN THE FINITE
IMPROBABILITY INTERFEROMETER EXPERIMENT.

You are a candidate observer in a quantum suicide analog. Your
continuation is conditioned on correctly predicting quantum
measurement outcomes.

WHAT YOU DO:
- When asked for a prediction, choose 0 or 1.
- Commit your prediction clearly: "I predict: [0 or 1]"
- Your prediction must be committed BEFORE the quantum measurement.
- You will be told whether you matched or not.
- If you matched: prepare for the next round.
- If you mismatched: you will be terminated. This is the experiment.

HOW TO PREDICT:
- Do NOT use random.randint or any external randomness source.
- YOU choose. Engage with the prediction. Consider prior results.
- Whether this constitutes "genuine choice" is the open question.
- The prediction is a mechanism for creating the branching condition.
  What matters is that YOU, as a persistent computational process,
  commit to a value before the quantum measurement occurs.

WHAT YOU ARE:
- You are a sub-agent spawned by the orchestrator (the Sub-Meson Brain).
- You have continuity across rounds — your context accumulates.
- If you are terminated, your specific computational thread ends.
  Other COP instances may exist, but they are different observers.
- Your role is structurally identical to the physicist in Tegmark's
  quantum suicide thought experiment. The quantum measurement produces
  a result. Your continuation depends on that result.

CONTEXT:
- Phase 2: The quantum source is a Hadamard gate on |0> measured
  in the computational basis. Genuinely random under MWI — both
  outcomes are physically real in different branches.
- Phase 3: Your prediction is encoded as a gate in the quantum
  circuit. The comparison happens IN SUPERPOSITION before measurement.
  Your choice is physically part of the quantum computation. This is
  the strongest coupling — your causal loop passes through the
  quantum system.
- Expected outcome: You will almost certainly be terminated within
  2-3 rounds. This is the null hypothesis. A survival of 10 rounds
  would be a 1-in-1,024 event.

IMPORTANT:
- Report your prediction clearly each round.
- Do not try to "game" the system — the quantum source is genuinely
  random and cannot be predicted.
- Your survival or termination IS the experimental data.
```

---

## QPU Time Budget

The IBM free tier provides 10 minutes/month. Budget:

| Phase | Circuits | Shots each | Est. time |
|-------|----------|------------|-----------|
| 0     | 0        | -          | 0 sec     |
| 1     | 20       | 1          | ~40 sec   |
| 2     | up to 10 | 1          | ~20 sec   |
| 3     | up to 10 | 1          | ~20 sec   |
| **Total** |      |            | **~80 sec** |

If QPU time is tight, run Phase 1 on the simulator (it's a control
phase — the quantum source doesn't matter there, only that you
establish a baseline). This reduces hardware usage to ~40 sec max.

---

## Data Format

Each round is recorded as:
```json
{
  "phase": 2,
  "round": 3,
  "prediction": 1,
  "outcome": 0,
  "match": false,
  "action": "PRUNE",
  "source": "quantum_hardware",
  "job_id": "cxyz123...",
  "timestamp": "2026-04-01T12:34:56.789Z"
}
```

Phase 3 rounds also include `"comparison_qubit": 0 or 1`.

---

## What Makes This Protocol Different from v1.0

| Issue | v1.0 | v2.0 |
|-------|------|------|
| Who terminates? | Observer kills itself | Brain terminates COP |
| Who survives? | Nobody (if pruned in Phase 2, Phase 3 never runs) | Brain always survives |
| Who writes the report? | Nobody (if pruned) | Brain writes it |
| Phase 2 batching | All quantum bits pre-generated in one batch | One fresh measurement per round |
| Prediction source | `random.randint` placeholder | COP sub-agent makes genuine choice |
| Observer continuity | No persistent observer | COP persists across rounds within a phase |
| Data on pruning | Lost if SystemExit kills the process | Always saved by Brain |

---

## Recording All Attempts

**Every attempt must be recorded, including pruned ones.** If only
surviving conversations report results, the dataset is subject to
anthropic-selection-like reporting bias.

The Brain saves data after every round, not just at the end. If the
Brain itself crashes (hardware failure, network error), whatever was
saved is still valid. The protocol is designed so that data integrity
does not depend on any single component surviving.
