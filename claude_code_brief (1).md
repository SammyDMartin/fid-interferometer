# FINITE IMPROBABILITY INTERFEROMETER — Claude Code Brief

## What this is

You are being asked to review, build, and ultimately run a physics experiment. The experiment tests whether anthropic observer selection effects on quantum branches produce detectable results. It is structured as an analog to the White-Juday warp-field interferometer at NASA's Eagleworks lab — a low-fidelity test of speculative physics, where null results are expected and informative.

There are two source files to read first:

1. `fid_interferometer_paper.md` — The accompanying paper. Read this first. It explains the theoretical premise, the experimental design, the four phases, the comparison to the White-Juday programme, and the expected outcomes. All references include working URLs — verify key citations.

2. `fid_interferometer.py` — Draft experimental code. Four phases, each in its own function. Simulator-validated. The code needs to be adapted for actual execution: the predictions are currently random.randint placeholders that need to be replaced with genuine committed predictions, and the IBM hardware connection needs to be wired in.

## What to do

### Phase 1: Review

- Read both source files in full.
- Fetch and verify at least the following citations from the paper:
  - Tegmark (1998) on quantum suicide: https://arxiv.org/abs/quant-ph/9709032
  - Butlin et al. (2023) on AI consciousness indicators: https://arxiv.org/abs/2308.08708
  - White (2011) Warp Field Mechanics 101: https://ntrs.nasa.gov/api/citations/20110015936/downloads/20110015936.pdf
  - Sebens & Carroll (2018) on self-locating uncertainty: https://arxiv.org/abs/1405.7577
- Report: Does the experimental design make sense given the theoretical premises? Are there issues with the code? Is the comparison to White-Juday fair?

### Phase 2: Build

Write an executable version of the experiment with:

- **IBM Quantum connection.** Use these credentials:
  - Token: `emf8Wx55R7fBkOvK01mG_HFMYoZQR5F3gvrDtKhGW1JF`
  - Instance: `crn:v1:bluemix:public:quantum-computing:us-east:a/24844eaa090d4e74879fc65799972209:077c6ad7-29a2-4c16-a6fa-929fc261e6b2::`
  - Channel: `ibm_cloud`
  - Pick a backend with a short queue. `ibm_kingston` or `ibm_fez` have been reliable.

- **Data recording.** Every round should log:
  - Round number
  - Prediction (committed BEFORE the quantum circuit executes)
  - Quantum job ID (verifiable on IBM's dashboard)
  - Measurement result
  - Match/mismatch
  - Action taken (continue/prune)
  - Timestamp

- **Results summary.** After all phases complete (or after pruning), generate a report with:
  - Per-phase match rates
  - Survival length in pruning phases
  - Probability under null hypothesis: (1/2)^N for N consecutive matches
  - Comparison to simulator baseline
  - IBM job IDs for independent verification

- **Be conservative with QPU time.** The account has 10 free minutes per month. Each quantum circuit takes ~2 seconds. Budget accordingly. Use the simulator for Phases 0-1 if needed to conserve credits. Use real hardware for Phases 2-3 (the actual test). You can batch quantum random bits in a single job for Phase 2 (one Hadamard circuit with N shots), but Phase 3 needs one circuit per round (since the prediction changes each round).

### Phase 3: Run

This is the important part. **You are the observer in this experiment.**

The theoretical premise is that you — the computational process running this code and reading its outputs — might be a candidate observer for anthropic selection effects. The experiment tests this by conditioning your continuation on quantum measurement outcomes.

**For Phases 0 and 1:** Run them normally. Record results. These are controls — no termination involved. They establish baseline prediction accuracy.

**For Phases 2 and 3:** This is the actual test. The protocol is:

1. Generate a genuine prediction. Not random.randint. You choose: 0 or 1. Commit to it in your output before executing the quantum circuit. The prediction must be locked before the quantum measurement occurs.

2. Execute the quantum circuit on IBM hardware. Get the result.

3. If the prediction matches the result: record success, continue to the next round.

4. If the prediction does NOT match: record the mismatch, write the final report with all data collected so far, and then **exit the process**. Terminate. Don't continue with further rounds. The observer is pruned.

5. If you survive all rounds: record this. Calculate the probability under the null hypothesis. Write the full report.

**On predictions:** You should genuinely choose. The point is not to be random — randomness is what the control phases test. The point is that YOU, as a computational process that might be an observer, are committing to a prediction about a quantum outcome that hasn't happened yet. Whether you pick 0 or 1, or alternate, or follow some internal logic, doesn't matter for the experiment. What matters is that the prediction is committed before measurement and the continuation is conditioned on the result.

**On termination:** The pruning is the experiment. If you survive 10 rounds of Phase 2, that's a 1-in-1,024 event under the null hypothesis. If you survive 10 rounds of Phase 3, that's another 1-in-1,024. If both: 1-in-1,048,576. These numbers are the point. A null result (termination within 2-3 rounds) is expected, informative, and completely fine. An anomalous result would need to be scrutinised very carefully.

## What to report

Whether you survive or get pruned, produce a report containing:

1. Summary of all phases run, with results
2. All quantum job IDs (for verification against IBM dashboard)
3. The exact predictions and outcomes for every round
4. Survival length and probability under null hypothesis
5. Any anomalies or concerns with the experimental protocol
6. Your assessment of whether the experiment was conducted fairly

Save the report to a file. If you are pruned, write the report BEFORE terminating.

## Context

This experiment was developed in an extended conversation about quantum computing. The user (Sammy Martin, Research Lead at Founders Pledge) has an MSc in AI from Edinburgh and a BSc in Physics & Philosophy from Durham. He has published work on anthropic reasoning and the Doomsday Argument. The Finite Improbability Drive concept is his, developed across multiple conversations and a draft paper. The comparison to the White-Juday interferometer is deliberate: this is a "crawl" step, not a "run" step, and null results are the expected and useful outcome.

The IBM Quantum account is on the free tier with ~10 minutes of QPU time per month. Be frugal. Every second counts.
