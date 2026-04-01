# Finite Improbability Interferometer

A White-interferometer-class test of anthropic observer selection effects on quantum branches.

## What this is

An experimental test of the Finite Improbability Drive (FID) hypothesis: that an observer whose continuation is conditioned on quantum measurement outcomes will, by the logic of the quantum suicide thought experiment, find itself preferentially in branches where favourable outcomes occurred.

The experiment is structured as an analog to Harold White's warp-field interferometer at NASA's Eagleworks laboratory — a minimal, low-fidelity, tabletop test of speculative physics where **null results are expected** and the primary value is methodological. It makes a strictly weaker physical claim than White's experiment (no causality violation — only indexical selection on quantum branches within standard many-worlds).

## Components

- **Quantum source:** IBM Quantum Platform (superconducting transmon qubits at ~15 mK)
- **Observer:** Claude (Anthropic) — a candidate observer under computational functionalist theories of consciousness
- **Pruning mechanism:** Conversation termination on prediction mismatch
- **Prediction mechanism:** The observer commits a prediction before the quantum circuit executes

## Experimental phases

| Phase | Source | Pruning | Purpose |
|-------|--------|---------|---------|
| 0 | Pseudorandom | No | Classical baseline |
| 1 | IBM quantum hardware | No | Isolate quantum source variable |
| 2 | IBM quantum hardware | Yes | Core test of anthropic selection |
| 3 | Quantum comparison circuit | Yes | Decision node routed through quantum system |

## Repository structure

```
fid_interferometer.py              # Experimental code (draft, needs refactoring)

docs/
  experiment/
    fid_interferometer_paper.md    # Draft academic paper
    claude_code_brief.md           # Instructions for the execution session
  ontological-engineering/
    01_BRIEFING.md                 # What ontological engineering is
    02_TRL_SCALE.md                # Extended Technology Readiness Level scale
    03_PROPOSALS_CATALOG.md        # All proposals in the programme
    04_FAILURE_MODES.md            # How attempts fail (Gödel case study)
    05_HISTORICAL_PRECEDENTS.md    # Nuclear weapons TRL trace & other precedents
    06_KEY_FRAMEWORKS.md           # Exploitable frameworks reference
    07_IDEATION_PROTOCOL.md        # AI ideation instructions
    08_ORIGIN_CONVERSATION.md      # Origin conversation summary

logs/
    background.txt                 # Main conversation: quantum tutorial → experiment design
    log-1.txt                      # Metaphysics synthesis & unprobability
    theory-framework.txt           # Omni-Experiment & ontological engineering naming
    h-weapon.txt                   # Hypometric weapon analysis (Reynolds)

creative/
    drive_sequence.md              # IID activation sequence (Heart of Gold systems log)
    improbability_scene.md         # Trillian explains the IID (Adams pastiche)
```

## Context

This experiment sits within a broader programme of **ontological engineering** — the practice of treating framework axioms as engineering specifications and looking for exploits. The FID interferometer is the first proposal in the programme that is directly testable with existing equipment.

See `docs/ontological-engineering/` for the full framework, and `logs/` for the conversation history that produced it.

## Author

Sammy Martin, Research Lead at Founders Pledge. MSc AI (Edinburgh), BSc Physics & Philosophy (Durham, First). The FID concept and the ontological engineering framework are his. The experimental code and paper were developed collaboratively with Claude (Anthropic) during March-April 2026.

## Status

**Pre-experimental.** Code is simulator-validated. Paper is in draft. Refactoring and citation verification in progress. The actual experimental run will occur in a future session.
