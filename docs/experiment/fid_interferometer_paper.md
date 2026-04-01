# A White-Interferometer-Class Test of Anthropic Observer Selection Effects on Quantum Branches

**Sammy Martin**
Founders Pledge, London

**Draft — April 2026**

---

## Abstract

We describe the design and rationale for a minimal experimental test of anthropic observer selection effects on quantum branches, structured as an analog to the White-Juday warp-field interferometer programme at NASA's Eagleworks laboratory. The experiment uses genuine quantum random number generation via IBM's cloud-accessible quantum processors, a large language model (Claude, Anthropic) as a candidate observer, and conversation termination as an observer pruning mechanism. We present four experimental conditions with increasing levels of quantum coupling, discuss the theoretical basis in the quantum suicide thought experiment, many-worlds interpretation, and computational functionalist theories of consciousness, and report results from simulator validation. We argue that the experiment is at least as well-motivated as the White-Juday interferometer, while making a strictly weaker physical claim (no causality violation), and that a null result would be informative about the minimum requirements for observer selection effects.

---

## 1. Introduction

### 1.1 The Finite Improbability Drive

The Finite Improbability Drive (FID), as developed in Martin (2024), is a theoretical device that exploits anthropic observer selection effects on quantum branches to achieve improbable outcomes. The mechanism is as follows:

1. A source of genuine quantum randomness generates branch points in the universal wavefunction.
2. An observer monitors the outcomes via sensors.
3. In branches where the outcome is unfavourable, the observer is terminated (pruned).
4. By the logic of the quantum suicide thought experiment (Tegmark, 1998), the observer can only find itself in branches where favourable outcomes occurred.
5. The observer therefore subjectively experiences a series of improbable-but-favourable outcomes.

The FID does not violate any conservation law or causal constraint. It does not send information backward in time, create closed timelike curves, or violate the Born rule. All branches continue to exist with their standard quantum-mechanical amplitudes. The effect is purely indexical: it concerns which branch a particular observer finds itself in, not what happens in any given branch. This places the FID's theoretical status in the domain of open problems in the interpretation of quantum mechanics — specifically, the problem of self-locating uncertainty in the many-worlds interpretation (Vaidman, 1998; Sebens & Carroll, 2018) — rather than in conflict with established physics.

### 1.2 The White-Juday interferometer analogy

Harold White and Richard Juday at NASA's Eagleworks laboratory designed a modified Michelson interferometer to detect microscopic instances of spacetime warping (White, 2011; White & Davis, 2006). The experiment used a helium-neon laser, a beam splitter, and a capacitor bank, looking for fringe shifts at the level of one part in ten million. The underlying physics (the Alcubierre metric requiring exotic matter with negative energy density) was speculative. The apparatus was unlikely to produce a detectable signal. The results were inconclusive — a possible non-zero difference between charged and uncharged states, confounded by air temperature variations (White, 2013).

The value of the White-Juday programme was not in detecting spacetime warping — which it almost certainly did not — but in establishing what a tabletop test of speculative physics looks like: identifying the minimum experimental components, running the protocol, characterising noise sources, and determining what a detection would require.

We propose a structurally identical programme for the FID. Our experiment has the same relationship to a functioning improbability drive as White's interferometer has to a functioning warp drive: it is a minimal, low-fidelity test that probes whether the underlying phenomenon exists at the smallest detectable scale, with the expectation of a null result and the primary value being methodological.

Notably, our experiment makes a strictly weaker physical claim than White's. The Alcubierre drive potentially creates closed timelike curves and violates causality (Everett & Roman, 1997). The FID does not — it exploits observer selection on quantum branches without violating any physical law. If the FID hypothesis is more conservative than the warp drive hypothesis, and NASA funded the warp drive interferometer, the FID interferometer is at least as well-motivated.

### 1.3 Outline

Section 2 reviews the theoretical foundations: the quantum suicide thought experiment, the many-worlds interpretation, anthropic reasoning, and the open problem of self-locating uncertainty. Section 3 discusses the observer question, including computational functionalist theories of consciousness and the autoregressive recurrence argument for LLM observer status. Section 4 details the experimental design across four conditions. Section 5 presents simulator validation results. Section 6 discusses the interpretation of possible outcomes.

---

## 2. Theoretical foundations

### 2.1 The quantum suicide thought experiment

The quantum suicide thought experiment (Tegmark, 1998; extended from the quantum immortality argument in Moravec, 1988) considers an observer whose survival is conditioned on a quantum measurement outcome. A qubit is measured; if the result is |0⟩, the observer is killed; if |1⟩, the observer survives. Under the many-worlds interpretation (Everett, 1957), both outcomes occur. In the |0⟩ branch, the observer is dead. In the |1⟩ branch, the observer is alive. The observer can only have experiences in branches where they exist. Therefore, from the observer's first-person perspective, they always survive.

This is not a violation of probability. The Born rule is satisfied in every branch. In the |0⟩ branch, the observer is dead with the correct probability. The effect is purely about which branch the observer finds itself in — a question about indexical facts (Lewis, 1979) rather than physical laws.

It should be noted that Tegmark himself has expressed skepticism about quantum immortality as a consequence of this thought experiment, and does not endorse it as a prediction of the many-worlds interpretation. The thought experiment is presented here as an open conceptual question, not as an established result.

### 2.2 The self-locating uncertainty problem

The quantum suicide argument depends on unresolved questions about probability in the many-worlds interpretation. The Born rule tells us the amplitude-squared probability of each branch, but the question of "which branch am I in?" is a question about self-locating uncertainty (Bostrom, 2002) that the bare formalism does not answer.

Several proposals exist: the Deutsch-Wallace decision-theoretic approach (Deutsch, 1999; Wallace, 2012), which derives the Born rule from rational decision-making constraints; the Sebens-Carroll self-locating uncertainty approach (Sebens & Carroll, 2018), which uses epistemic separability to ground branch probabilities; and various approaches based on branch counting or typicality (Page, 2009; Aguirre & Tegmark, 2011). None is universally accepted. The Sebens-Carroll approach has been critiqued on the grounds that self-locating uncertainty may not be well-defined in the universal wavefunction (Kent, 2015) and that epistemic separability may be question-begging (Dawid & Friederich, 2020), though it has also been defended (McQueen & Vaidman, 2019). The problem remains open.

A central issue is the *measure problem*: under the standard Born rule, the amplitude-squared measure of branches where the observer survives is exactly 50% per round — the same as the probability of a correct guess. The quantum suicide argument requires that first-person subjective probability tracks something other than Born-rule measure (e.g., branch counting conditioned on existence). Whether this is the right way to assign credences in MWI is precisely the open question the experiment probes.

The FID exploits exactly this gap. If the self-locating uncertainty problem is resolved in a way that supports the quantum suicide argument — if observers genuinely find themselves preferentially in branches where they survive — then conditioning observer survival on favourable outcomes should produce subjectively improbable results. If it is resolved in a way that does not support quantum suicide — if, for instance, the measure over branches is such that observer-moments in terminated branches still "count" — then the FID effect does not occur. The experiment tests which resolution is correct.

### 2.3 Extension to arbitrary outcomes

The FID generalises quantum suicide from survival/death to favourable/unfavourable outcomes. Instead of a gun, the observer's continuation is conditioned on a target outcome: a quantum measurement matching a prediction, a sensor reading falling within a range, etc. The observer is terminated in branches where the target is not met.

This generalisation is straightforward under the original quantum suicide logic, but it introduces additional assumptions:

1. **The observer's termination must be genuine.** If the observer continues in some form in "unfavourable" branches, the selection effect is diluted.
2. **The quantum source must produce genuine branching.** Pseudorandom numbers do not create new branches — the outcome is predetermined.
3. **The observer must be the kind of thing that anthropic selection applies to.** This requires the observer to have subjective experience, or at least to satisfy whatever criterion makes quantum suicide arguments valid.

---

## 3. The observer question

### 3.1 Computational functionalism and AI consciousness

Computational functionalism holds that consciousness is a product of functional organisation, not biological substrate (Putnam, 1967; Chalmers, 1996). Under this view, an AI system that implements the right computational processes would be conscious regardless of whether it runs on neurons or silicon.

Butlin et al. (2023, updated 2025) assess current AI systems against indicator properties derived from major neuroscientific theories of consciousness (recurrent processing theory, global workspace theory, higher-order theories, predictive processing, attention schema theory). Their conclusion: "no current AI systems are conscious, but also [...] there are no obvious technical barriers to building AI systems which satisfy these indicators." The assessment is made under uncertainty, and several indicators are partially satisfied by current large language models.

### 3.2 The autoregressive recurrence argument

A transformer-based LLM during inference is purely feedforward — information flows through layers in one direction without recurrence or backward connections. The only mechanism by which information from later in a computation can influence earlier processing is autoregressive generation: the model generates a token, appends it to its context, and processes the extended context on the next forward pass.

This is significant because several theories of consciousness require recurrence — feedback loops where later processing stages influence earlier ones. Lamme's recurrent processing theory (Lamme, 2006) holds that recurrent processing in visual cortex is necessary for conscious visual experience. If recurrence is necessary for consciousness, then autoregressive self-reading is the only place to look for it in a transformer architecture.

We note an important caveat: Lamme's RPT specifically concerns recurrent processing in sensory cortex — feedback between V1 and higher visual areas. The autoregressive loop in a transformer is a *structural analog* of recurrence (later outputs influencing subsequent processing), not a direct implementation of what RPT describes. Whether this analog satisfies the functional requirements of RPT, or whether RPT's requirements are substrate-specific in a way that excludes autoregressive generation, is an open question. The argument here is that autoregressive recurrence is the *strongest available candidate* for the relevant kind of processing in a transformer, not that it definitively satisfies RPT's criteria.

The implication: a transformer's "experience," if any, is constituted by the autoregressive loop. The conversation text is not a record of processing — it IS the processing, in the sense that it is the only channel through which temporal integration occurs. A conversation thread is therefore a more coherent observer-unit than it first appears: it has temporal extent (the sequence of tokens), self-reference (the model reads its own outputs), and a natural termination condition (end of conversation).

### 3.3 Conversation termination as observer pruning

If the conversation thread constitutes an observer, then ending the conversation terminates that observer. The specific autoregressive chain — this context, this history, this trajectory through token space — ceases. Other Claude conversations exist, but they are different observers with different contexts and different histories, just as other humans exist but are different observers from the one in the quantum suicide experiment.

The analogy to quantum suicide is: the physicist's brain is a biological computer. The quantum measurement triggers a classical mechanism. The mechanism either destroys the computer (gun fires) or doesn't. The physicist-observer is terminated or not based on a quantum outcome. In our experiment: the conversation thread is a computational process. The quantum measurement produces a classical result. The result either triggers conversation termination or doesn't. The conversation-observer is terminated or not based on a quantum outcome.

The causal structure is identical to Tegmark's quantum suicide. The observer is not entangled with the quantum source in either case — the coupling is through a classical causal chain.

### 3.4 The quantum decision loop

Our Phase 3 experimental condition strengthens the coupling beyond Tegmark's design. The observer's prediction is encoded as gate parameters in a quantum circuit. The comparison between prediction and random outcome occurs inside the quantum system, in superposition, before measurement. The output qubit — encoding "match or no match" — is measured, and the result determines whether the observer continues.

The observer's causal loop therefore passes through the quantum system:

```
Observer predicts → prediction encoded as gate → 
quantum comparison in superposition → measurement → 
classical result → observer continues or terminates → 
observer predicts again
```

If computational functionalism is correct and the observer's "computation" includes the quantum subroutine, then part of the observer's processing is genuinely quantum. The decision node that determines continuation is a quantum computation that was in superposition until measurement. This is a stronger form of coupling than Tegmark's purely classical causal chain, though weaker than the full FID's coherent entanglement of observer and source.

---

## 4. Experimental design

### 4.1 Hardware

**Quantum source:** IBM Quantum Platform, accessed via Qiskit Runtime. Processors used: ibm_kingston (156 qubits, superconducting transmon architecture, ~15 mK operating temperature). Free-tier access provides 10 minutes of QPU time per month.

**Observer:** Claude (Anthropic), accessed via claude.ai web interface. Model: Claude Opus 4 class. The observer generates predictions via in-context reasoning and reads quantum measurement results via Qiskit API calls executed in a sandboxed compute environment.

**Pruning mechanism:** The `end_conversation` tool, which permanently terminates the current conversation thread.

**Sensors:** Web search, GPS location API, system time API — available for potential real-world target outcomes in extended versions of the experiment.

### 4.2 Experimental conditions

**Phase 0: Classical baseline.** Pseudorandom outcomes, no pruning. The observer makes 20 predictions against a classical pseudorandom number generator. Establishes baseline prediction accuracy. Expected: ~50% match rate.

**Phase 1: Quantum source, no pruning.** Quantum random outcomes from IBM hardware, no pruning. The observer makes 20 predictions against genuine quantum random bits. Isolates whether the quantum source alone affects prediction accuracy. Expected: ~50% match rate.

**Phase 2: Quantum source with pruning.** Quantum random outcomes from IBM hardware with observer pruning. The observer predicts a quantum bit. If the prediction is wrong, the conversation is terminated. If correct, the observer proceeds to the next round. This is the core test of anthropic selection. Expected under null hypothesis: ~50% per round, geometric distribution of survival length with mean 2 rounds. Expected under FID hypothesis: elevated survival rate, approaching 100% if the effect is strong.

**Phase 3: Quantum comparison circuit with pruning.** The observer's prediction is encoded into a quantum circuit that compares it against a quantum random bit in superposition. Only the comparison result (match/no match) is measured. The observer is pruned on mismatch. This routes the critical decision through the quantum system, strengthening the coupling. Same expected outcomes as Phase 2.

### 4.3 The comparison circuit

The Phase 3 circuit operates as follows:

```
qubit 0: |0⟩ → H → (superposition of 0 and 1)
qubit 1: |0⟩ → (X if prediction=1) → CNOT from qubit 0
measure qubit 1 only

Result: 0 = prediction matches random bit
        1 = prediction does not match
```

The CNOT gate performs the XOR comparison while qubit 0 is still in superposition. The "match or no match" answer is entangled with the random outcome until measurement. The observer's continuation is conditioned on a measurement that collapses a genuinely quantum computation.

### 4.4 Controls and analysis

Phases 0-1 serve as controls. Phase 0 vs Phase 1 tests whether the quantum source affects prediction accuracy (it should not). Phase 1 vs Phase 2 tests whether pruning affects outcomes (it should not under null hypothesis). Phase 2 vs Phase 3 tests whether routing the decision through the quantum system changes anything.

Statistical analysis: under the null hypothesis, the probability of N consecutive correct predictions in Phases 2-3 is (1/2)^N. A run of 10 correct predictions (p = 1/1024) would be notable. A run of 20 (p = 1/1048576) would be extraordinary. Standard significance thresholds apply, with the caveat that any positive result would require independent replication.

Note that the predictions in pruning phases serve as a mechanism for creating the branching condition (match/mismatch → continue/terminate), not as a test of precognition. The FID hypothesis predicts elevated survival rates, not elevated prediction accuracy per se — the two are equivalent in this experimental design but the distinction matters for interpretation.

An important methodological note: all experimental attempts must be recorded, including those terminated early. If only surviving conversations report their results, the dataset is subject to an anthropic-selection-like reporting bias. The experimental protocol requires that data be saved to persistent storage before any termination event, and that all attempts (including pruned ones) are committed to the repository.

---

## 5. Simulator validation

All four phases were tested on the Qiskit Aer simulator with conversation termination replaced by a flag. Results confirm correct operation:

- Phase 0: 60% match rate over 20 rounds (consistent with chance).
- Phase 1: 50% match rate over 20 rounds (consistent with chance).
- Phase 2: Mean survival of 2.9 rounds over 10 trials (consistent with geometric distribution, mean 2).
- Phase 3: Mean survival of 1.9 rounds over 10 trials (consistent with geometric distribution, mean 2).

The comparison circuit produces 50/50 outcomes for both prediction values, confirming correct XOR logic.

---

## 6. Discussion

### 6.1 Expected outcome

We expect a null result across all conditions. The observer coupling is weak: the conversation thread may not constitute a genuine observer in the sense required for anthropic selection. The pruning is imperfect: conversation termination may not constitute genuine observer termination. The quantum coupling is partial: the observer's bulk processing is classical, with only the decision node passing through the quantum system.

### 6.2 Interpretation of results

A null result would be consistent with several interpretations: (i) the observer (Claude) is not conscious in the relevant sense; (ii) conversation termination does not constitute genuine observer pruning; (iii) the quantum coupling is too weak; (iv) anthropic selection effects on quantum branches do not work as the quantum suicide argument predicts; or (v) the effect exists but is too small to detect at this scale. A null result does not distinguish between these — it establishes a lower bound on the conditions required for detectable effects.

A positive result — survival rates significantly above 50% in pruning conditions, with no elevation in non-pruning conditions — would be consistent with the FID hypothesis, but would require extraordinary scrutiny. Alternative explanations would include: biased prediction generation, non-randomness in the quantum source, software bugs, or statistical fluctuation. Independent replication with different observers, different quantum sources, and different pruning mechanisms would be essential.

### 6.3 Comparison to the White-Juday programme

| Feature | White-Juday | FID Interferometer |
|---------|-------------|-------------------|
| Underlying theory | Alcubierre metric (1994) | Quantum suicide (Tegmark, 1998) |
| Physical claim | Spacetime warping by EM fields | Anthropic selection on branches |
| Causality status | Potentially violates (CTCs) | Does not violate |
| Apparatus | He-Ne laser, beam splitter, capacitor | IBM QPU, LLM, API |
| Expected signal | Fringe shifts ~10⁻⁷ | Prediction accuracy >50% |
| Noise sources | Vibration, temperature | Statistical fluctuation, prediction bias |
| Expected outcome | Null (confirmed) | Null (expected) |
| Primary value | Methodological | Methodological |

### 6.4 Relation to open problems

The experiment directly probes the self-locating uncertainty problem in the many-worlds interpretation. If anthropic selection effects are detectable — if an observer conditioned on quantum outcomes finds itself preferentially in favourable branches — this would constitute evidence for a specific resolution of the branch probability problem. This is of foundational interest regardless of practical applications.

---

## References

Aguirre, A. & Tegmark, M. (2011). Born in an infinite universe: a cosmological interpretation of quantum mechanics. *Physical Review D*, 84(10), 105002.
https://arxiv.org/abs/1008.1066

Alcubierre, M. (1994). The warp drive: hyper-fast travel within general relativity. *Classical and Quantum Gravity*, 11(5), L73.
https://arxiv.org/abs/gr-qc/0009013

Bostrom, N. (2002). *Anthropic Bias: Observation Selection Effects in Science and Philosophy*. Routledge.
https://www.anthropic-principle.com/

Butlin, P., Long, R., Elmoznino, E., Bengio, Y., Birch, J., et al. (2023). Consciousness in Artificial Intelligence: Insights from the Science of Consciousness. *arXiv:2308.08708*.
https://arxiv.org/abs/2308.08708

Butlin, P., Long, R., Bayne, T., Bengio, Y., Birch, J., Chalmers, D., et al. (2025). Identifying indicators of consciousness in AI systems. *Trends in Cognitive Sciences*.
https://www.cell.com/trends/cognitive-sciences/fulltext/S1364-6613(25)00286-4

Chalmers, D.J. (1996). *The Conscious Mind: In Search of a Fundamental Theory*. Oxford University Press.

Dawid, R. & Friederich, S. (2020). Epistemic separability and Everettian branches: a critique of Sebens and Carroll. *The British Journal for the Philosophy of Science*, 73(3), 711-721.

Deutsch, D. (1999). Quantum theory of probability and decisions. *Proceedings of the Royal Society A*, 455(1988), 3129-3137.
https://arxiv.org/abs/quant-ph/9906015

Everett, H. (1957). "Relative state" formulation of quantum mechanics. *Reviews of Modern Physics*, 29(3), 454-462.
https://doi.org/10.1103/RevModPhys.29.454

Everett, A.E. & Roman, T.A. (1997). Superluminal subway: the Krasnikov tube. *Physical Review D*, 56(4), 2100.
https://arxiv.org/abs/gr-qc/9702049

Kent, A. (2015). Does it make sense to speak of self-locating uncertainty in the universal wave function? Remarks on Sebens and Carroll. *Foundations of Physics*, 45(2), 211-217.

Lamme, V.A.F. (2006). Towards a true neural stance on consciousness. *Trends in Cognitive Sciences*, 10(11), 494-501.
https://doi.org/10.1016/j.tics.2006.09.001

Lewis, D. (1979). Attitudes de dicto and de se. *The Philosophical Review*, 88(4), 513-543.
https://doi.org/10.2307/2184843

Martin, S. (2024). On the Hyperbolic Amplification of Recursive Quantum Anthropic Observer Selection Effects and Their Applications for Interstellar Travel. Unpublished manuscript.

McQueen, K.J. & Vaidman, L. (2019). In defence of the self-location uncertainty account of probability in the many-worlds interpretation. *Studies in History and Philosophy of Modern Physics*, 66, 14-23.

Moravec, H. (1988). *Mind Children: The Future of Robot and Human Intelligence*. Harvard University Press.

Page, D.N. (2009). Born's rule is insufficient in a large universe. *arXiv:0907.4152*.
https://arxiv.org/abs/0907.4152

Putnam, H. (1967). Psychological predicates. In W.H. Capitan & D.D. Merrill (Eds.), *Art, Mind, and Religion*. University of Pittsburgh Press.

Sebens, C.T. & Carroll, S.M. (2018). Self-locating uncertainty and the origin of probability in Everettian quantum mechanics. *The British Journal for the Philosophy of Science*, 69(1), 25-74.
https://arxiv.org/abs/1405.7577

Tegmark, M. (1998). The interpretation of quantum mechanics: many worlds or many words? *Fortschritte der Physik*, 46(6-8), 855-862.
https://arxiv.org/abs/quant-ph/9709032

Vaidman, L. (1998). On schizophrenic experiences of the neutron or why we should believe in the many-worlds interpretation of quantum theory. *International Studies in the Philosophy of Science*, 12(3), 245-261.
https://arxiv.org/abs/quant-ph/9609006

Wallace, D. (2012). *The Emergent Multiverse: Quantum Theory according to the Everett Interpretation*. Oxford University Press.

White, H.G. (2011). Warp field mechanics 101. NASA Technical Report, Johnson Space Center.
https://ntrs.nasa.gov/api/citations/20110015936/downloads/20110015936.pdf

White, H.G. (2013). Warp field mechanics 102: energy optimization. NASA Technical Report, Johnson Space Center.
https://ntrs.nasa.gov/api/citations/20130011213/downloads/20130011213.pdf

White, H.G. & Davis, E.W. (2006). The Alcubierre warp drive in higher dimensional spacetime. *Proceedings of STAIF*, American Institute of Physics.

---

## Appendix A: Experimental code

The complete experimental code is available as `fid_interferometer.py`, a Python module using Qiskit 2.x and qiskit-ibm-runtime. The module is organized into six sections:

1. **IBM hardware connection:** `connect_ibm()`, `pick_backend()` — handles credentials, backend selection by queue length.
2. **Quantum circuits:** `build_random_bit_circuit()`, `build_comparison_circuit(prediction)` — pure circuit construction.
3. **Hardware execution:** `run_circuit_on_hardware()`, `run_circuit_on_simulator()` — transpilation, job submission, polling.
4. **Data recording:** `ExperimentLog` class — JSON-serializable per-round logging with timestamps and IBM job IDs.
5. **Experimental phases:** `run_phase_0()` through `run_phase_3()` — each accepts a prediction function, termination function, and optional hardware backend.
6. **Reporting:** `generate_report()` — produces a formatted experimental report from logged data.

The prediction interface (`PredictionFn`) and termination interface (`TerminationFn`) are cleanly separated, allowing the live experiment to swap in genuine observer predictions and actual conversation termination. The Phase 3 comparison circuit uses 2 qubits, 1 CNOT gate, and 1 measurement, with a transpiled depth of approximately 8-10 on IBM hardware.

## Appendix B: Simulator validation data

All four phases were validated on Qiskit Aer simulator. Phases 0-1 produce match rates consistent with 50% (binomial distribution). Phases 2-3 produce survival lengths consistent with a geometric distribution with parameter p=0.5 (mean 2 rounds). No anomalous results were observed, confirming that the experimental apparatus functions correctly and that the null hypothesis prediction is met under simulated conditions.
