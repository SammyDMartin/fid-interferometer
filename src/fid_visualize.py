"""
FID Interferometer — Visualization
===================================

Generates publication-quality plots from experiment log data.
Called via: python fid_interferometer.py visualize <log_path>
       or: python fid_visualize.py <log_path>

Produces:
  1. Round-by-round timeline with match/mismatch markers
  2. Survival probability curve vs null hypothesis
  3. Phase comparison bar chart
  4. Control flow diagram (architecture visualization)

All saved as PNG files alongside the log.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np


# Color scheme
C_MATCH = "#2ecc71"      # Green — survived
C_MISMATCH = "#e74c3c"   # Red — pruned
C_NULL = "#95a5a6"        # Grey — null hypothesis
C_BG = "#1a1a2e"          # Dark background
C_FG = "#e0e0e0"          # Light foreground
C_ACCENT = "#3498db"      # Blue accent
C_PHASE0 = "#f39c12"      # Orange
C_PHASE1 = "#9b59b6"      # Purple
C_PHASE2 = "#2ecc71"      # Green
C_PHASE3 = "#3498db"      # Blue


def _load(log_path):
    return json.loads(Path(log_path).read_text())


def plot_timeline(log, save_path):
    """
    Round-by-round timeline showing predictions, outcomes, and actions.
    Each phase is a separate row. Matches are green circles, mismatches
    are red X marks. Pruning events are marked with a skull.
    """
    rounds = log["rounds"]
    phases = {}
    for r in rounds:
        phases.setdefault(r["phase"], []).append(r)

    fig, axes = plt.subplots(
        len(phases), 1,
        figsize=(14, 2.5 * len(phases)),
        facecolor=C_BG,
    )
    if len(phases) == 1:
        axes = [axes]

    phase_names = {
        0: "Phase 0: Classical Baseline",
        1: "Phase 1: Quantum Source",
        2: "Phase 2: Quantum + Pruning",
        3: "Phase 3: Quantum Circuit + Pruning",
    }
    phase_colors = {0: C_PHASE0, 1: C_PHASE1, 2: C_PHASE2, 3: C_PHASE3}

    for idx, (pnum, pdata) in enumerate(sorted(phases.items())):
        ax = axes[idx]
        ax.set_facecolor(C_BG)
        ax.set_title(phase_names.get(pnum, f"Phase {pnum}"),
                     color=phase_colors.get(pnum, C_FG),
                     fontsize=13, fontweight="bold", pad=10)

        for i, r in enumerate(pdata):
            x = i + 1
            if r["match"]:
                ax.scatter(x, 0.5, s=200, c=C_MATCH, marker="o",
                          zorder=3, edgecolors="white", linewidths=0.5)
                ax.text(x, -0.3, str(r["prediction"]),
                       ha="center", va="top", color=C_FG, fontsize=9)
            else:
                ax.scatter(x, 0.5, s=200, c=C_MISMATCH, marker="X",
                          zorder=3, edgecolors="white", linewidths=0.5)
                ax.text(x, -0.3, str(r["prediction"]),
                       ha="center", va="top", color=C_MISMATCH, fontsize=9)

            if r.get("action") == "PRUNE":
                ax.annotate("PRUNED", (x, 0.5),
                           xytext=(x + 0.5, 1.2),
                           fontsize=10, color=C_MISMATCH, fontweight="bold",
                           arrowprops=dict(arrowstyle="->", color=C_MISMATCH),
                           ha="center")

        n = len(pdata)
        ax.set_xlim(0.3, max(n + 1, 3))
        ax.set_ylim(-0.8, 1.8)
        ax.set_xlabel("Round", color=C_FG, fontsize=10)
        ax.set_xticks(range(1, n + 1))
        ax.set_yticks([])
        ax.tick_params(colors=C_FG)
        for spine in ax.spines.values():
            spine.set_color(C_FG)
            spine.set_alpha(0.3)

    fig.tight_layout(pad=2.0)
    fig.savefig(save_path, dpi=150, facecolor=C_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Timeline saved: {save_path}")


def plot_survival_curve(log, save_path):
    """
    Survival probability curve for pruning phases.
    Shows observed survival vs null hypothesis (0.5^n).
    """
    rounds = log["rounds"]
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    # Null hypothesis curve
    n_max = 12
    x_null = np.arange(0, n_max + 1)
    y_null = 0.5 ** x_null
    ax.plot(x_null, y_null, "--", color=C_NULL, linewidth=2,
            label="Null hypothesis: P = (1/2)^N", zorder=1)
    ax.fill_between(x_null, y_null, alpha=0.1, color=C_NULL)

    # Significance thresholds
    ax.axhline(y=0.05, color="#e74c3c", alpha=0.4, linestyle=":",
               label="p = 0.05 (N ≈ 4.3)")
    ax.axhline(y=0.001, color="#e74c3c", alpha=0.2, linestyle=":",
               label="p = 0.001 (N = 10)")

    # Observed data for pruning phases
    for pnum, color, label in [
        (2, C_PHASE2, "Phase 2: Quantum + Pruning"),
        (3, C_PHASE3, "Phase 3: Quantum Circuit + Pruning"),
    ]:
        pdata = [r for r in rounds if r["phase"] == pnum]
        if not pdata:
            continue
        n_survived = sum(1 for r in pdata if r["action"] == "CONTINUE")
        pruned = any(r["action"] == "PRUNE" for r in pdata)

        # Plot the observed point
        y_obs = 0.5 ** (n_survived + (1 if pruned else 0))
        ax.scatter(n_survived + (1 if pruned else 0), y_obs,
                  s=300, c=color, marker="*" if not pruned else "X",
                  zorder=5, edgecolors="white", linewidths=1,
                  label=f"{label}: {'pruned R' + str(len(pdata)) if pruned else 'SURVIVED ' + str(n_survived)}")

        # Draw the path
        x_path = list(range(0, n_survived + 1 + (1 if pruned else 0)))
        y_path = [0.5 ** n for n in x_path]
        ax.plot(x_path, y_path, "-", color=color, linewidth=2, alpha=0.7, zorder=2)

    ax.set_xlabel("Consecutive correct predictions (N)", color=C_FG, fontsize=12)
    ax.set_ylabel("Probability under null hypothesis", color=C_FG, fontsize=12)
    ax.set_title("Survival Probability vs Null Hypothesis",
                color=C_FG, fontsize=14, fontweight="bold")
    ax.set_yscale("log")
    ax.set_xlim(-0.5, n_max + 0.5)
    ax.set_ylim(1e-4, 1.5)
    ax.legend(loc="upper right", fontsize=9, facecolor=C_BG,
             edgecolor=C_FG, labelcolor=C_FG)
    ax.tick_params(colors=C_FG)
    ax.grid(True, alpha=0.15, color=C_FG)
    for spine in ax.spines.values():
        spine.set_color(C_FG)
        spine.set_alpha(0.3)

    fig.tight_layout()
    fig.savefig(save_path, dpi=150, facecolor=C_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Survival curve saved: {save_path}")


def plot_phase_comparison(log, save_path):
    """
    Bar chart comparing match rates across all phases.
    """
    rounds = log["rounds"]
    phases = {}
    for r in rounds:
        phases.setdefault(r["phase"], []).append(r)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    phase_colors = {0: C_PHASE0, 1: C_PHASE1, 2: C_PHASE2, 3: C_PHASE3}
    phase_labels = {
        0: "P0: Classical",
        1: "P1: Quantum",
        2: "P2: Q+Prune",
        3: "P3: Circuit+Prune",
    }

    x_pos = []
    heights = []
    colors = []
    labels = []
    annotations = []

    for i, pnum in enumerate(sorted(phases.keys())):
        pdata = phases[pnum]
        n_match = sum(1 for r in pdata if r["match"])
        n_total = len(pdata)
        pct = 100 * n_match / n_total

        x_pos.append(i)
        heights.append(pct)
        colors.append(phase_colors.get(pnum, C_FG))
        labels.append(phase_labels.get(pnum, f"Phase {pnum}"))
        annotations.append(f"{n_match}/{n_total}")

    bars = ax.bar(x_pos, heights, color=colors, edgecolor="white",
                  linewidth=0.5, width=0.6)

    # 50% reference line
    ax.axhline(y=50, color=C_NULL, linestyle="--", linewidth=1.5,
               label="Expected: 50%")

    for i, (bar, ann) in enumerate(zip(bars, annotations)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
               ann, ha="center", va="bottom", color=C_FG, fontsize=11,
               fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, color=C_FG, fontsize=11)
    ax.set_ylabel("Match Rate (%)", color=C_FG, fontsize=12)
    ax.set_title("Match Rates by Phase", color=C_FG, fontsize=14,
                fontweight="bold")
    ax.set_ylim(0, 110)
    ax.legend(facecolor=C_BG, edgecolor=C_FG, labelcolor=C_FG)
    ax.tick_params(colors=C_FG)
    for spine in ax.spines.values():
        spine.set_color(C_FG)
        spine.set_alpha(0.3)

    fig.tight_layout()
    fig.savefig(save_path, dpi=150, facecolor=C_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Phase comparison saved: {save_path}")


def plot_architecture(save_path):
    """
    Visual diagram of the Sub-Meson Brain / COP architecture.
    Shows the control flow of the experiment.
    """
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    def box(x, y, w, h, text, color, fontsize=9, alpha=0.85):
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.15",
                              facecolor=color, alpha=alpha,
                              edgecolor="white", linewidth=1)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
               color="white", fontsize=fontsize, fontweight="bold",
               wrap=True)

    def arrow(x1, y1, x2, y2, text="", color=C_FG):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle="-|>", color=color,
                                   linewidth=1.5))
        if text:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx + 0.15, my, text, fontsize=7.5, color=color,
                   ha="left", va="center")

    # Title
    ax.text(7, 9.5, "FID INTERFEROMETER — CONTROL FLOW",
           ha="center", fontsize=16, fontweight="bold", color=C_FG)
    ax.text(7, 9.1, "Sub-Meson Brain (orchestrator) + Computational Observer Processes (sub-agents)",
           ha="center", fontsize=9, color=C_NULL)

    # Sub-Meson Brain (main box)
    brain_rect = FancyBboxPatch((0.5, 3.5), 3.5, 5,
                                boxstyle="round,pad=0.2",
                                facecolor="#2c3e50", alpha=0.9,
                                edgecolor=C_ACCENT, linewidth=2)
    ax.add_patch(brain_rect)
    ax.text(2.25, 8.1, "SUB-MESON BRAIN", ha="center", fontsize=11,
           fontweight="bold", color=C_ACCENT)
    ax.text(2.25, 7.7, "(Main Claude Agent)", ha="center", fontsize=8,
           color=C_NULL)
    ax.text(2.25, 7.2, "Persists throughout\nManages all phases\nNever terminates",
           ha="center", fontsize=7.5, color=C_FG)

    # Phase boxes inside brain
    box(0.8, 6.0, 2.9, 0.7, "Phase 0-1\nRun directly (no pruning)", "#34495e", 8)

    box(0.8, 4.8, 2.9, 0.9, "Phase 2-3\nSpawn COP → get prediction\n"
        "Run circuit → check result", "#34495e", 8)

    box(0.8, 3.8, 2.9, 0.7, "Report\nVisualize → Save → Push", "#34495e", 8)

    # Phase 2 COP lifecycle
    box(5.5, 6.5, 2.8, 1.5, "COP Sub-Agent\n(Phase 2)\n\nMakes prediction\n"
        "Returns to Brain", C_PHASE2, 8, 0.7)

    # Arrow from brain to COP
    arrow(3.7, 7.0, 5.5, 7.2, "spawn", C_PHASE2)
    arrow(5.5, 6.8, 4.0, 5.5, "prediction", C_FG)

    # Quantum circuit box
    box(5.5, 4.5, 2.8, 1.2, "IBM Quantum\nProcessor\n\nH|0⟩ → measure\n(one shot)", "#8e44ad", 8)
    arrow(4.0, 5.0, 5.5, 5.1, "execute", "#8e44ad")

    # Phase 3 COP + circuit
    box(9.5, 6.5, 3.8, 1.5, "COP Sub-Agent\n(Phase 3)\n\nPrediction ENCODED\n"
        "into quantum circuit", C_PHASE3, 8, 0.7)
    arrow(8.3, 7.2, 9.5, 7.2, "", C_FG)

    # Phase 3 quantum
    box(9.5, 4.5, 3.8, 1.2, "Comparison Circuit\n\nH → CNOT(pred, rand)\n"
        "XOR in superposition", "#8e44ad", 8)
    arrow(10.5, 6.5, 10.5, 5.7, "pred encodes\nas gate", C_PHASE3)

    # Decision diamond
    ax.plot([7, 8, 7, 6, 7], [3.5, 2.8, 2.1, 2.8, 3.5],
           color=C_FG, linewidth=1.5)
    ax.text(7, 2.8, "Match?", ha="center", va="center",
           color=C_FG, fontsize=9, fontweight="bold")

    arrow(7, 4.5, 7, 3.5, "", "#8e44ad")

    # Match path
    ax.annotate("YES", xy=(5.5, 2.8), xytext=(6, 2.8),
               fontsize=9, color=C_MATCH, fontweight="bold",
               ha="right")
    ax.annotate("", xy=(4.5, 5.0), xytext=(6, 2.8),
               arrowprops=dict(arrowstyle="-|>", color=C_MATCH, linewidth=1.5))
    ax.text(4.5, 3.7, "Continue →\nnext round", fontsize=7.5, color=C_MATCH,
           ha="center")

    # Mismatch path
    ax.annotate("NO", xy=(8.5, 2.8), xytext=(8.0, 2.8),
               fontsize=9, color=C_MISMATCH, fontweight="bold",
               ha="left")

    box(9, 1.8, 2.5, 1.0, "COP PRUNED\n\nContext destroyed\nObserver terminated",
        C_MISMATCH, 8, 0.8)
    ax.annotate("", xy=(9, 2.3), xytext=(8, 2.8),
               arrowprops=dict(arrowstyle="-|>", color=C_MISMATCH, linewidth=1.5))

    # Key insight note
    box(0.5, 0.5, 13, 1.0,
        "KEY: The Brain (main agent) NEVER terminates. Only the COP sub-agents are pruned.\n"
        "In Phase 3, the COP's prediction passes THROUGH the quantum circuit in superposition — "
        "the observer's causal loop includes genuine quantum computation.",
        "#1a1a2e", 8.5, 0.95)

    fig.savefig(save_path, dpi=150, facecolor=C_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Architecture diagram saved: {save_path}")


def visualize_experiment(log_path):
    """Generate all visualizations from an experiment log."""
    log = _load(log_path)
    base = Path(log_path).stem

    out_dir = Path("data/plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_timeline(log, out_dir / f"{base}_timeline.png")
    plot_survival_curve(log, out_dir / f"{base}_survival.png")
    plot_phase_comparison(log, out_dir / f"{base}_phases.png")
    plot_architecture(out_dir / f"{base}_architecture.png")

    print(f"\nAll visualizations saved to {out_dir}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fid_visualize.py <log_path>")
        print("  or:  python fid_visualize.py --architecture")
        sys.exit(1)

    if sys.argv[1] == "--architecture":
        Path("data/plots").mkdir(parents=True, exist_ok=True)
        plot_architecture("data/plots/fid_architecture.png")
    else:
        visualize_experiment(sys.argv[1])
