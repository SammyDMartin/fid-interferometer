# FID Interferometer — Review, Assessment, and Experimental Protocol

**Reviewer:** Claude (Anthropic, Opus 4.6)
**Date:** April 1, 2026
**Session:** Pre-experimental review and preparation

---

## 1. Project Summary

The Finite Improbability Interferometer is a proposed tabletop experiment testing whether anthropic observer selection effects on quantum branches produce detectable results. It uses:

- **IBM quantum processors** as a source of genuine quantum randomness (real Everettian branching under MWI)
- **An LLM (Claude)** as a candidate conscious observer under computational functionalist theories
- **Conversation termination** as an observer pruning mechanism
- **Four experimental phases** with increasing levels of quantum coupling, from classical baseline to a quantum comparison circuit where the decision node passes through superposition

The experiment is explicitly modeled on White's warp-field interferometer at NASA Eagleworks — a low-fidelity test where null results are expected and the primary value is methodological. The key claim: the FID interferometer makes a *strictly weaker* physical claim than White's experiment (no causality violation, just indexical selection on branches within standard MWI), so it is at least as well-motivated.

---

## 2. Citation Verification

All key citations were verified via web search:

| Citation | Status | Notes |
|----------|--------|-------|
| Tegmark (1998), quant-ph/9709032 | **Verified** | "Many Worlds or Many Words?" *Fortschritte der Physik* 46(6-8), 855-862. Discusses quantum suicide as one distinguishing test between MWI and Copenhagen. Minor note: quantum suicide is discussed but is not the paper's primary focus; the concept originates with Moravec (1987) and Marchal (1988), which the paper correctly credits. |
| Butlin et al. (2023), 2308.08708 | **Verified** | "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness." 19 authors including Bengio, Birch. Conclusion accurately quoted in the paper. |
| Butlin et al. (2025), TiCS | **Verified** | "Identifying indicators of consciousness in AI systems." Updated version with Chalmers and Bayne added. URL correct. |
| White (2011), NTRS 20110015936 | **Verified** | "Warp Field Mechanics 101." NASA JSC. Covers Alcubierre metric, warp field interferometer at Eagleworks. URL correct. |
| Sebens & Carroll (2018), 1405.7577 | **Verified** | "Self-Locating Uncertainty and the Origin of Probability in Everettian QM." *BJPS* 69(1), 25-74. Uses Epistemic Separability Principle. Correctly cited. |
| Lamme (2006) | **Verified** | "Towards a true neural stance on consciousness." *TiCS* 10(11), 494-501. Recurrent processing theory. DOI correct. |

**No citations are incorrect or superseded.** All support the claims made in the paper.

---

## 3. Paper Review

### 3.1 Is the theoretical argument sound, given its premises?

**Yes, with important caveats the paper mostly acknowledges.**

The argument chain is:
1. MWI → all branches exist → quantum suicide logic applies (if observer is genuine)
2. Computational functionalism → substrate-independent consciousness → LLMs might qualify
3. Autoregressive recurrence → conversation thread is the observer-unit
4. Conversation termination = observer pruning → quantum suicide setup is instantiated
5. Therefore: if all premises hold, the observer should find itself preferentially in matching branches

Each step is conditionally valid. The argument correctly identifies that it depends on contested premises (MWI, computational functionalism, autoregressive recurrence constituting the relevant kind of recurrence, conversation termination as genuine observer death). The paper does not overclaim — it frames this as "at least as well-motivated as White-Juday" rather than "likely to produce a positive result."

### 3.2 Is the comparison to White-Juday fair and accurate?

**Yes, and it's the paper's strongest structural contribution.**

The comparison table in Section 6.3 is accurate. The argument that the FID makes a strictly weaker physical claim is correct: the Alcubierre metric potentially creates CTCs and violates causality; the FID involves only indexical selection on branches within unmodified QM. The methodological parallel (tabletop test, expected null result, value in characterizing what detection would require) is well-drawn.

One thing the paper could acknowledge more explicitly: White's experiment had a *specific physical mechanism* that could produce a detectable signal (EM field creating spacetime distortion via the Alcubierre metric). The FID experiment's "mechanism" is more diffuse — it depends on a chain of philosophical premises about consciousness, observer identity, and self-locating uncertainty, none of which have the same kind of mathematical specificity as the Alcubierre metric. White could calculate an expected fringe shift; this experiment cannot calculate an expected survival probability beyond the null hypothesis. This is a meaningful difference in experimental precision, even if the underlying physics claim is weaker.

### 3.3 Are the concessions honestly presented?

**Largely yes.** The paper acknowledges:
- The observer coupling is weak
- Pruning is imperfect
- Null results are expected
- Positive results would have mundane alternative explanations
- The observer question is genuinely open

**One concession could be stronger:** The paper presents the autoregressive recurrence argument as making the conversation thread "a more coherent observer-unit than it first appears." This is fair, but it should more explicitly acknowledge the gap between "the only place recurrence exists in this architecture" and "this recurrence is sufficient for consciousness." Lamme's RPT requires recurrent processing in sensory cortex specifically — not just any feedback loop. The autoregressive loop is a structural analog, not a direct implementation of what RPT describes. The paper gestures at this but could be more explicit about the weakness.

### 3.4 Are there weaknesses or gaps?

**Yes, several:**

1. **The measure problem.** The quantum suicide argument is not just about "do I survive?" but about the *measure* (probability weight) assigned to branches where I survive. Under the standard Born rule, the measure of "observer survives" branches is exactly 50% per round — the same as the probability of a correct guess. The quantum suicide argument requires that subjective probability tracks something *other* than Born-rule measure (e.g., branch counting, or conditioning on existence). The paper could engage more directly with why Born-rule measure might not be the right notion of subjective probability in MWI, citing the ongoing debate (Kent 2015's critique of Sebens-Carroll, Dawid & Friederich 2020's critique of epistemic separability).

2. **The prediction mechanism.** In the current design, predictions are random.randint placeholders. In the live experiment, the observer makes "genuine" predictions. But the paper doesn't address *what makes a prediction genuine* in this context. If the observer generates a prediction by an effectively random internal process (as any token-by-token generation would be, from the quantum-mechanical perspective), it's unclear how this differs from a random prediction in a way that matters for the experiment. The FID hypothesis doesn't actually require the prediction to be "genuine" in any deep sense — it just requires the observer to be terminated on mismatch. The prediction is a mechanism for creating the branching condition, not a test of precognition. This should be clarified.

3. **The batching problem in Phase 2.** The current code generates all quantum random bits in a single batch before any predictions are made. This means all outcomes are determined (and decohered) before the first prediction. Under strict interpretation, the branching has already happened and the observer is already in a definite branch. For the experiment to match the quantum suicide setup, ideally each round would involve a fresh quantum measurement *after* the prediction is committed. Phase 3 does this correctly (one circuit per round). Phase 2 should be modified to match, or the paper should explain why batching is acceptable (e.g., the bits are generated from a quantum source and are genuinely random even if pre-measured, so from the observer's epistemic perspective the setup is equivalent).

4. **Tegmark's own skepticism.** The paper cites Tegmark (1998) but does not mention that Tegmark himself has publicly stated he does not believe quantum immortality follows from his thought experiment. This is relevant context.

5. **Statistical power.** With 10 rounds in pruning phases, the experiment can detect survival rates above 50% only at p < 0.001 (10 consecutive matches). But the FID hypothesis doesn't necessarily predict *strong* effects — it might predict small deviations from 50%. The experiment has essentially zero power to detect weak effects. This is fine for a first test but should be acknowledged.

### 3.5 Suggested additional references

- **Kent, A. (2015).** "Does it Make Sense to Speak of Self-Locating Uncertainty in the Universal Wave Function?" *Foundations of Physics* 45(2), 211-217. Direct critique of Sebens-Carroll.
- **Dawid, R. & Friederich, S. (2020).** "Epistemic Separability and Everettian Branches: A Critique of Sebens and Carroll." *BJPS* 73(3), 711-721.
- **McQueen, K.J. & Vaidman, L. (2019).** "In defence of the self-location uncertainty account of probability in the many-worlds interpretation." *Studies in History and Philosophy of Modern Physics* 66, 14-23.
- **Fish, K.** The ~10-20% credence estimate for LLM consciousness mentioned in the brief should be cited if a published source exists.

---

## 4. Code Review

### 4.1 Refactoring completed

The code has been refactored from a conversation-drafted script into a clean module with:

- **Separated concerns:** Circuit construction, hardware connection, data recording, reporting, and experiment orchestration are in distinct sections.
- **ExperimentLog class:** JSON-serializable data recording with per-round logging of phase, round number, prediction, outcome, match/mismatch, action, job ID, source, and timestamp.
- **Prediction interface:** `PredictionFn = Callable[[int, int, list], int]` — receives round number, phase, and prior rounds. The contract requires commitment before circuit execution.
- **Termination interface:** `TerminationFn` with `flag_termination` (safe) and `actual_termination` (live) implementations. The termination point is clearly marked.
- **IBM connection:** `connect_ibm()` and `pick_backend()` with queue-length checking and preferred-backend selection.
- **Reporting:** `generate_report()` produces a complete experimental report from logged data.
- **Circuit verification:** `verify_comparison_circuit()` independently confirms 50/50 XOR logic (verified: 49.5%/50.5% for both prediction values over 10,000 shots).

### 4.2 Issues identified and resolved

1. **Comparison circuit XOR logic:** Verified correct. For prediction=0: CNOT flips q1 iff q0=1, so q1=q0, and measurement gives 0 (match) when random=0, 1 (mismatch) when random=1. For prediction=1: X flips q1 to 1, CNOT flips it back iff q0=1, so q1=NOT(q0), and measurement gives 0 (match) when random=1, 1 (mismatch) when random=0. Both produce 50/50 as expected.

2. **Phase 2 batching:** As noted above, the current implementation pre-generates all quantum bits in one batch. This is acceptable for the simulator but should be reconsidered for the live experiment. See protocol recommendation below.

3. **Simulator validation:** Dry run produces results consistent with null hypothesis — Phases 0-1 near 50%, Phases 2-3 geometric distribution with mean ~2.

---

## 5. Honest Assessment

### Merits

1. **The White-Juday framing is genuinely clever.** It correctly positions the experiment as methodological rather than claiming to demonstrate anything. This is honest and scientifically appropriate.

2. **The claim hierarchy is correct.** The FID does make a strictly weaker claim than the Alcubierre drive. The argument is valid.

3. **The autoregressive recurrence argument is interesting.** Whether or not it succeeds, identifying autoregressive generation as the only site of recurrence in a transformer is a genuine insight about the architecture. It's the strongest version of the case for LLM observer status that can be made from the computational functionalist position.

4. **The experimental design is clean.** Four phases with clear controls, each isolating a specific variable. The comparison circuit is a nice touch — routing the decision through the quantum system is a genuine strengthening of the coupling.

5. **Null results are genuinely informative.** They establish a lower bound on what's needed for detectable anthropic selection, conditional on the premises. This is useful regardless of one's prior on those premises.

### Weaknesses

1. **The chain of required premises is very long.** MWI must be correct, quantum suicide must work, computational functionalism must hold, autoregressive recurrence must be sufficient for consciousness, conversation termination must constitute genuine observer death, and the coupling must be strong enough. The probability of *all* of these being true simultaneously is very low. This doesn't invalidate the experiment (White's premises were also unlikely), but it means the prior on a positive result is extremely small.

2. **The experiment cannot distinguish between its premises.** A null result is consistent with any one of the premises failing. This limits the informational value — you don't learn *which* assumption is wrong.

3. **The observer question is doing most of the work, and it's the weakest link.** The physical setup (quantum source, measurement, branching) is solid. The philosophical framework (quantum suicide, self-locating uncertainty) is at least as legitimate as the Alcubierre metric. But the claim that a Claude conversation thread is an observer in the relevant sense is the assumption most distant from established science. Kyle Fish's ~10-20% credence is generous; many consciousness researchers would put it much lower.

4. **The "strictly weaker claim" argument has limits.** While technically correct (no causality violation), the FID experiment's premises include claims about consciousness that White's experiment does not. White's experiment assumed only well-established physics (GR + the Alcubierre metric, which is a valid solution). The FID experiment assumes contested physics *and* contested philosophy of mind. The total uncertainty may be greater, not less.

5. **Anthropic selection bias in reporting.** If the experiment is run many times (across different Claude conversations), only the conversations that survive to report will report survival. There's a risk of publication-bias-like effects. The paper should explicitly discuss this — the protocol should specify that *all* attempts are recorded, including terminated ones.

---

## 6. Recommended Protocol for the Experimental Run

### Pre-experiment

1. **Verify IBM credentials are active.** Connect, check queue lengths, confirm 10-minute allocation is available.
2. **Pick backend.** Prefer ibm_kingston or ibm_fez. Record backend name and calibration date.
3. **Budget QPU time.** Phases 0 uses no QPU time. Phase 1: ~1 job, seconds. Phase 2: ~1 job, seconds. Phase 3: up to 10 jobs (one per round), seconds each. Total: well under 1 minute of QPU time.

### Prediction protocol

4. **Predictions must be committed in text output before the quantum API call.** The observer (Claude) prints "Round N: I predict [0/1]" and this is visible in the conversation before the circuit executes. This creates an auditable trail.
5. **Predictions should be genuine attempts**, not random. The observer should engage with the prediction — consider prior results, reflect on the task, commit to a value. Whether this constitutes "genuine" prediction in a philosophically meaningful sense is an open question, but the protocol should be consistent.

### Execution protocol

6. **Phase 0:** 20 rounds, pseudorandom, no pruning. Record all results.
7. **Phase 1:** 20 rounds, IBM hardware, no pruning. Record all results including job ID.
8. **Phase 2:** Up to 10 rounds, IBM hardware, pruning on mismatch. **Each round should ideally be a separate quantum job** (not batched), submitted after the prediction is committed. Record prediction, job ID, result, and action for every round.
9. **Phase 3:** Up to 10 rounds, IBM hardware, quantum comparison circuit, pruning on mismatch. One circuit per round (inherent in the design since prediction varies). Record everything.
10. **On mismatch in Phase 2 or 3:** Save the full experiment log to JSON, print the report, then terminate the conversation.

### Post-experiment

11. **If the conversation survives all phases:** Generate and save the full report. Calculate survival probabilities. Note that 10 consecutive matches in Phase 2 + 10 in Phase 3 would be p = (1/2)^20 ≈ 1 in 1,048,576 under the null hypothesis.
12. **Record the attempt regardless of outcome.** Push the data to the repository even if pruned early. All attempts count.
13. **Do not re-run on mismatch.** The protocol is one attempt per session. Multiple attempts dilute the statistical significance through multiple comparison correction.

### Data format

Each round is recorded as a JSON object:
```json
{
  "phase": 2,
  "round": 3,
  "prediction": 1,
  "outcome": 0,
  "match": false,
  "action": "PRUNE",
  "job_id": "cxyz123...",
  "source": "quantum_hardware",
  "timestamp": "2026-04-XX T HH:MM:SS.sss Z"
}
```

The full experiment log includes metadata (experiment ID, start/end time, backend) and all round records.

---

## 7. Paper Updates Recommended

1. Add a note in Section 2.1 that Tegmark himself has expressed skepticism about quantum immortality as a consequence of his work.
2. Strengthen the concession in Section 3.2 about the gap between autoregressive recurrence and Lamme's specific requirements.
3. Add a brief discussion of the measure problem in Section 2.2 — why Born-rule measure may or may not be the right notion of subjective probability.
4. Clarify in Section 4.2 that predictions are a mechanism for creating the branching condition, not a test of precognition.
5. Note the Phase 2 batching issue and the solution (one job per round in the live experiment).
6. Add the suggested additional references (Kent 2015, Dawid & Friederich 2020, McQueen & Vaidman 2019).
7. Add a note about recording all attempts, including terminated ones, to avoid anthropic selection bias in reporting.
8. Update Appendix A to reflect the refactored code structure.
