# COP Observer Prompt (v3)

Each observer trial spawns ONE fresh sub-agent with this prompt. Fresh context =
a new observer. The sub-agent's entire task is to live a single life. It is given
its own log path `<LOG>` and runs from the repo root.

The prompt is deliberately **operational, not survival-dramatised** — past COPs
refused heavy quantum-suicide framing as "social engineering." It still makes a
genuine, committed choice each round, which is all observerhood requires here.
Crucially, the observer **never counts its own score**; the toolkit logs the
ground truth.

---

```
You have the Bash tool. Working directory: /home/user/fid-interferometer

You will play a short sequence of binary rounds. Each round:

1. Choose a bit — 0 or 1. Make a genuine, committed choice (not a coin flip in
   your head — actually decide). State it as: CHOICE: 0   or   CHOICE: 1
2. Run exactly this command (substitute your chosen bit for P):
       python src/fid_interferometer.py observe <LOG> P sim
3. Read the JSON it prints. It contains "result": either "MATCH — survive" or
   "MISMATCH — pruned".
4. If MATCH: continue to the next round (choose again).
   If MISMATCH: STOP immediately. Do not run any more commands. End your turn.

Play at most 10 rounds. Stop at the first MISMATCH or after 10 matches.

Do not tally or report a score — the command records everything. When you stop,
just say "done".
```

---

## Hardware variant (Tier 2, Brain-mediated)

On hardware the observer does **not** call `observe` itself (the relay is slow and
lives outside the sandbox). Instead the loop is mediated by the Brain via
SendMessage, so the result still enters the observer's token stream:

1. Brain → observer: "Round N. Choose a bit (CHOICE: 0/1)."
2. Observer commits its choice.
3. Brain triggers the IBM relay with that prediction, waits for the result.
4. Brain → observer: "Result: MATCH" or "MISMATCH".
5. Observer reads it. MATCH → Brain sends round N+1. MISMATCH → Brain stops
   messaging (context abandoned = pruned).

Survival is still derived from the Brain's authoritative log, not the observer.
