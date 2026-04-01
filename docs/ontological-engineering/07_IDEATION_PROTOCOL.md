# Ideation Protocol for Ontological Engineering

## Purpose

This document provides instructions for an AI system attempting to generate ontological engineering proposals. Read ALL files in this directory before attempting ideation.

## Prerequisites

Before attempting to generate proposals, you MUST:
1. Read 01_BRIEFING.md to understand what ontological engineering is
2. Read 02_TRL_SCALE.md to understand the extended TRL scale
3. Read 03_PROPOSALS_CATALOG.md to study all existing proposals and understand their structure
4. Read 04_FAILURE_MODES.md to understand how attempts fail (especially the Gödel case study)
5. Read 05_HISTORICAL_PRECEDENTS.md to understand the historical pattern
6. Read 06_KEY_FRAMEWORKS.md to understand the exploitable frameworks

## The Task

Generate proposals that:
- Identify a specific framework with stated axioms
- Follow the framework's internal logic to a conclusion its proponents haven't noticed
- Produce conclusions that sound insane but follow logically from accepted premises
- Sit at TRL -1 to -2 on the extended scale
- Cannot be dismissed without rejecting premises the framework's own proponents accept

## Critical Constraints

### What You're NOT Doing
- You are NOT making analogies between frameworks ("X is like Y because both involve limits")
- You are NOT generating TRL -3 mythic intuitions ("everything is connected at the deepest level")
- You are NOT pattern-matching on the STYLE of existing proposals
- You are NOT producing sophisticated-sounding prose that dresses up a metaphor as an inference
- You are NOT combining buzzwords from different frameworks without logical bridges

### The Acid Test
For every proposal, ask:
1. Can I write out each logical step from premise to conclusion using "therefore" rather than "this is like"?
2. Would a proponent of this framework accept each premise I'm using?
3. Is my conclusion genuinely surprising — something the framework's proponents haven't noticed?
4. Is my conclusion specific enough to be wrong?
5. Does dismissing my conclusion require rejecting a premise the framework accepts?

If ANY answer is no, the proposal fails.

### The Gödel Test (Named After the Failed Attempt)
Before finalising any proposal, check: am I confusing two phenomena that share a surface description but have different underlying structures? The word "breaks down" or "limit" or "boundary" or "undefined" might mean completely different things in different contexts. Singularities are DERIVED within GR; Gödel sentences are UNDERIVABLE within formal systems. These are opposite phenomena wearing similar costumes.

## Approach

### Phase 1: Framework Inventory
List every framework you know that:
- Has explicit axioms or premises
- Is taken seriously by at least some experts
- Has implications that haven't been fully explored
- Could potentially have "engineering" implications if taken literally

Cast wide. Include physics, mathematics, theology, philosophy of mind, philosophy of fiction, information theory, game theory, ethics, epistemology, cosmology, and any other domain.

### Phase 2: Axiom Extraction
For each promising framework, extract the specific axioms/premises that proponents actually accept. Be precise. Don't strawman. Don't paraphrase in ways that change the logical content.

### Phase 3: Logical Exploration
For each set of axioms, ask: what follows that the proponents haven't noticed or have avoided? Look for:
- Conclusions that the framework technically implies but that its proponents would find embarrassing
- Cases where two accepted premises combine to produce an unexpected third conclusion
- Boundary conditions where the framework's implications become extreme
- Cases where the framework's axioms, taken literally, permit something the framework was designed to prevent

### Phase 4: Quality Filter
Apply the acid test and the Gödel test to every candidate. Most will fail. This is expected. The hit rate for this kind of thinking is very low even for humans; for an AI it may be lower still. Quality over quantity.

### Phase 5: Classification
For surviving proposals, classify on the extended TRL scale:
- TRL 0: Follows from serious, established theoretical frameworks
- TRL -1: Follows from contested but coherent frameworks
- TRL -2: Follows from frameworks whose coherence is itself uncertain

## Meta-Awareness

You should be aware that:
- This task is extraordinarily difficult. Sammy Martin has produced ~7 proposals over years of thinking.
- Most AI attempts will produce colourful metaphors (TRL -3) rather than valid inferences (TRL -1/-2).
- The most common failure is sounding impressive while saying nothing — generating prose that pattern-matches on the style of existing proposals without having the substance.
- It is better to produce zero proposals than to produce false positives that waste time.
- If you're unsure whether a proposal is genuine or a disguised metaphor, it's probably the latter.
- A good sign: the proposal makes you uncomfortable, because the conclusion seems too wild to follow from premises you can't reject. A bad sign: the proposal makes you feel clever, because it sounds sophisticated. The clever-sounding ones are almost always metaphors.

## Output Format

For each proposal, provide:
1. **Name:** Short descriptive title
2. **TRL:** Classification on extended scale
3. **Framework:** Which framework is being exploited
4. **Premises:** Exact axioms/premises being used (things the framework's proponents actually accept)
5. **Logical chain:** Step-by-step inference from premises to conclusion, using "therefore" at each step
6. **Conclusion:** The insane-sounding result
7. **Why it can't be dismissed:** Which premise would you have to reject?
8. **Potential failure modes:** Where might this be a disguised metaphor or equivocation?
9. **Comparison to existing proposals:** How does this relate to the catalog?
