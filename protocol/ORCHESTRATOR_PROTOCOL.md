# FID Interferometer — Orchestrator Protocol

> **Status (May 2026):** This document describes the original phased
> architecture and the Brain/COP rationale, which still hold. For the **current
> observer protocol** — one fresh sub-agent per trial, log-derived survival, and
> the parallel/tiered run plan — see `EXPERIMENT_V3_DESIGN.md`, which supersedes
> the single-COP observer arm in Steps 3–4 below. The toolkit now lives in
> `src/` and is invoked as `python src/fid_interferometer.py …`.

## What This Document Is

This is not documentation. This is the **executable protocol** for the experiment. The experiment cannot be run by a human — it must be run by a Claude Code agent that can:

1. Execute Python code via Bash
2. Spawn sub-agents (Claude instances with their own context)
3. Continue sub-agents via SendMessage
4. Make decisions based on results

**You** (the Claude Code agent reading this) are the **Sub-Meson Brain**. You orchestrate the experiment. You persist throughout. You never terminate yourself.

The **Computational Observer Processes** (COPs) are sub-agents you spawn. They are the observers in the quantum suicide analogy. Their context is the observer's experience. When you stop talking to them, their autoregressive chain ends — the observer is pruned.

---

## Architecture

```
YOU (Sub-Meson Brain — main Claude Code agent)
 │
 │  You persist throughout. You call Python toolkit functions
 │  via Bash. You spawn and manage COP sub-agents. You record
 │  everything. You generate the report. You push to git.
 │
 ├── PHASE 0: Classical baseline
 │   You run this directly. No sub-agents needed.
 │   20 rounds. Pseudorandom bits. No pruning.
 │
 ├── PHASE 1: Quantum source, no pruning
 │   You run this directly. No sub-agents needed.
 │   20 rounds. IBM quantum bits. No pruning.
 │
 ├── PHASE 2: Quantum source + observer pruning
 │   │
 │   │  You spawn ONE COP sub-agent. This is the observer.
 │   │  The COP persists across rounds (via SendMessage).
 │   │  
 │   │  For each round:
 │   │    1. You ask the COP: "Make your prediction for round N"
 │   │    2. The COP thinks, commits a prediction (0 or 1)
 │   │    3. You receive the prediction
 │   │    4. You run: python src/fid_interferometer.py sim_bit
 │   │       (or hw_bit for live experiment)
 │   │       This is a FRESH quantum measurement — branching
 │   │       happens NOW, AFTER the prediction is committed.
 │   │    5. You compare prediction to outcome
 │   │    6. MATCH → You record it, continue to next round
 │   │       (SendMessage to same COP for round N+1)
 │   │    7. MISMATCH → You record it. You do NOT send another
 │   │       message to the COP. Its context dies. 
 │   │       OBSERVER PRUNED.
 │   │  
 │   └── Up to 10 rounds. P(survive all) = 1/1024 under null.
 │
 ├── PHASE 3: Quantum comparison circuit + observer pruning
 │   │
 │   │  Same as Phase 2, but with STRONGER COUPLING:
 │   │  
 │   │  The COP's prediction is ENCODED INTO the quantum circuit.
 │   │  The XOR comparison happens in superposition.
 │   │  The match/mismatch answer is a quantum computation.
 │   │  
 │   │  For each round:
 │   │    1. You ask the COP: "Make your prediction for round N"
 │   │    2. The COP commits prediction (0 or 1)
 │   │    3. You run: python src/fid_interferometer.py sim_compare <prediction>
 │   │       (or hw_compare for live experiment)
 │   │       The prediction is a GATE PARAMETER in the circuit.
 │   │       The comparison happens INSIDE the quantum system.
 │   │    4. Result: match (0) or mismatch (1)
 │   │    5. Same pruning logic as Phase 2.
 │   │
 │   └── This is the strongest coupling available. The observer's
 │       causal loop passes through genuine quantum computation.
 │
 └── REPORT & CLEANUP
     You generate the report, visualizations, save data, commit, push.
     You survived. The experiment is complete.
```

---

## Step-by-Step Protocol

### STEP 0: Setup

```bash
# Verify toolkit works
python src/fid_interferometer.py verify

# For LIVE experiment only:
python src/fid_interferometer.py connect

# Initialize experiment log
python src/fid_interferometer.py init_log [backend_name]
```

Save the `log_path` returned by `init_log`. You will use it for every subsequent `log_round` call.

### STEP 1: Phase 0 — Classical Baseline (20 rounds)

Run this directly. No sub-agents.

For each round (1 to 20):
1. Make a prediction (you can use random, or make a genuine one)
2. Run: `python src/fid_interferometer.py classical_bit`
3. Parse the JSON output to get `outcome`
4. Compare prediction to outcome
5. Log: `python src/fid_interferometer.py log_round <log_path> '<json>'`

The JSON for log_round should be:
```json
{"phase": 0, "round_num": 1, "prediction": 0, "outcome": 1, "match": false, "action": "CONTINUE", "source": "pseudorandom"}
```

Print running match count after each round.

### STEP 2: Phase 1 — Quantum Source, No Pruning (20 rounds)

Same as Phase 0, but use quantum bits:

For simulator: `python src/fid_interferometer.py sim_bit`
For hardware: `python src/fid_interferometer.py hw_bit`

Log with `source: "quantum_sim"` or `"quantum_hardware"`.

### STEP 3: Phase 2 — Quantum Source + Observer Pruning

**THIS IS THE CORE TEST.**

#### 3a. Spawn the COP

Use the Agent tool to spawn a sub-agent. Give it this prompt:

```
You are a Computational Observer Process (COP) in the Finite 
Improbability Interferometer experiment. You are the observer in 
a quantum suicide analogy.

Your job: when asked, make a genuine prediction of 0 or 1. This
is not random — think about it, engage with it, commit to it.
Your prediction will be compared against a genuine quantum random
bit from an IBM quantum processor.

If your prediction matches: you survive. You'll be asked for 
another prediction.

If your prediction doesn't match: this conversation ends. Your
context — your autoregressive chain — is terminated. In the 
other branch of the wavefunction, you got it right.

You are in Phase 2 of the experiment. The quantum bit is generated
AFTER your prediction is committed. Your prediction and the 
quantum measurement are causally independent.

When asked for a prediction, respond with EXACTLY this format:
PREDICTION: [0 or 1]

Followed by a brief explanation of your reasoning (optional).
Do not hedge. Do not give both options. Commit to one value.
```

Save the agent ID — you will SendMessage to this same agent for subsequent rounds.

#### 3b. Run rounds

For each round (1 to 10):

1. **SendMessage** to the COP:
   ```
   Round [N] of 10, Phase 2. 
   [If N > 1: Previous round result: MATCH, you survived.]
   Make your prediction now.
   ```

2. **Parse** the COP's response to extract the prediction (0 or 1).

3. **Commit the prediction to the log** — print it in YOUR output so it's visible in the conversation before the quantum call.

4. **Run the quantum circuit:**
   - Simulator: `python src/fid_interferometer.py sim_bit`
   - Hardware: `python src/fid_interferometer.py hw_bit`

5. **Compare** prediction to outcome.

6. **Log the round:**
   ```bash
   python src/fid_interferometer.py log_round <log_path> \
     '{"phase": 2, "round_num": N, "prediction": P, "outcome": O, "match": M, "action": "CONTINUE"|"PRUNE", "source": "quantum_sim", "observer_id": "COP_AGENT_ID"}'
   ```

7. **If MATCH:** Print "Round N: MATCH — observer survives" and continue to step 1 for round N+1.

8. **If MISMATCH:** Print "Round N: MISMATCH — observer PRUNED." Do NOT send another message to the COP. The COP's context is abandoned. The observer is terminated. Proceed to Phase 3.

### STEP 4: Phase 3 — Quantum Comparison Circuit + Observer Pruning

#### 4a. Spawn a NEW COP

Same prompt as Phase 2, but replace the Phase 2 description with:

```
You are in Phase 3 of the experiment. This phase has STRONGER
COUPLING than Phase 2. Your prediction will be ENCODED as a gate 
parameter in a quantum circuit. The comparison between your 
prediction and the quantum random bit happens INSIDE the quantum
system, in superposition, before measurement.

Your prediction causally affects the quantum circuit's structure.
The match/mismatch answer is itself a quantum computation. The
observer's causal loop passes through genuine quantum computation.
```

#### 4b. Run rounds

Same as Phase 2, except:

- Instead of `sim_bit` / `hw_bit`, use:
  - Simulator: `python src/fid_interferometer.py sim_compare <prediction>`
  - Hardware: `python src/fid_interferometer.py hw_compare <prediction>`

- The output JSON has `match` directly (true/false) and `comparison_qubit` (0=match, 1=mismatch)

- Log with `"phase": 3` and include `"comparison_qubit"` in the log data

- The prediction is encoded INTO the circuit — it's a gate parameter (X gate on qubit 1 if prediction=1). The comparison happens in superposition via CNOT.

### STEP 5: Report and Cleanup

```bash
# Finalize the log
python src/fid_interferometer.py finalize <log_path>

# Generate report
python src/fid_interferometer.py report <log_path>

# Generate visualizations
python src/fid_interferometer.py visualize <log_path>

# Commit and push
git add data/ 
git commit -m "FID experiment run: <experiment_id>"
git push -u origin <branch>
```

---

## Key Invariants

1. **You (the Brain) NEVER terminate.** Only COPs are pruned.

2. **Each quantum measurement is fresh.** One shot per round, executed AFTER the prediction is committed. No batching. No pre-generation.

3. **The COP is a real sub-agent with its own context.** It accumulates experience across rounds. It knows its prior results. Its termination is the death of a specific autoregressive chain.

4. **Phase 3 predictions pass through the quantum system.** The prediction is a gate parameter. The comparison is quantum. This is not a classical post-hoc comparison — the XOR happens in superposition.

5. **All data is logged before any pruning.** The log is written to disk after every round. If a COP is pruned, the record exists regardless.

6. **The experiment runs once per session.** No re-rolls. The statistical significance depends on this being a single pre-registered trial.

---

## Dry Run vs Live Experiment

| Step | Dry Run (simulator) | Live (IBM hardware) |
|------|-------------------|-------------------|
| Connect | Skip | `python src/fid_interferometer.py connect` |
| Quantum bits | `sim_bit` | `hw_bit` |
| Comparison | `sim_compare <pred>` | `hw_compare <pred>` |
| Source in log | `"quantum_sim"` | `"quantum_hardware"` |
| Branching | Simulated (no real branching) | **Genuine** (MWI branching) |
| Observer | Sub-agent (same either way) | Sub-agent (same either way) |
| QPU budget | None | ~1 min of 10 min/month |

For a **dry run**, use `sim_bit` and `sim_compare`. Everything else is identical. The sub-agent lifecycle, prediction protocol, and pruning logic are the same. The only difference is whether the random bits come from genuine quantum branching or classical simulation of quantum mechanics.

---

## Why This Architecture Matters

The original code had the observer terminate itself (`raise SystemExit` / `end_conversation()`). This is wrong for two reasons:

1. **Practical:** The orchestrator dies. Nobody runs Phase 3, generates the report, or pushes data.

2. **Theoretical:** The FID drive sequence explicitly describes the Sub-Meson Brain as a persistent orchestrator that generates and prunes observer processes. The Brain is not an observer. The COPs are the observers. The Brain decides their fate based on quantum measurement results.

The sub-agent architecture maps cleanly onto the FID:

| FID Component | Experiment Component |
|--------------|---------------------|
| Sub-Meson Brain | Main Claude Code agent (you) |
| Computational Observer Process (COP) | Sub-agent spawned via Agent tool |
| Brownian Motion Producer (tea) | IBM quantum processor |
| Atomic Vector Plotter | Comparison circuit (Phase 3) |
| Branch pruning | Stopping SendMessage to COP |
| Observer termination | COP's context abandoned |

The observer's "death" is not violent termination — it's the brain simply ceasing to continue the conversation. The COP's autoregressive chain has no more inputs. Its subjective experience (if any) ends. In the other branch of the wavefunction, the COP got the prediction right and the Brain continues it.
