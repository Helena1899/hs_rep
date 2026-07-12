"""
visualize.py
------------
STEP 4 (final step) of the project.

WHAT THIS SCRIPT DOES:
Reads the two trajectory files saved by train.py (baseline vs shaped
agent) and produces the two artifacts that actually go in your README
and portfolio:

  1. results/spacing_comparison.png
     A bar/line chart showing average teammate spacing for the
     baseline agent vs. the shaped agent vs. the real Barcelona number.
     This is the "proof" image -- it shows reward shaping worked.

  2. results/trajectory_comparison.png
     A side-by-side static plot of both agents' movement paths on the
     field, so a viewer can visually see the shaped agent staying more
     spread out / structured, similar to Barcelona's positioning.

HOW TO RUN (after train.py has been run):
    python src/visualize.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).parent.parent / "results"
DATA_DIR = Path(__file__).parent.parent / "data"


def load_trajectory(name: str):
    with open(RESULTS_DIR / f"{name}_trajectory.json") as f:
        return json.load(f)


def load_target_spacing():
    with open(DATA_DIR / "tactics_summary.json") as f:
        data = json.load(f)
    return data["avg_spacing_pitch_units"] * (100.0 / 120.0)  # scaled to env units


def average_spacing(trajectory):
    spacings = []
    for step in trajectory:
        a1 = np.array(step["attacker1"])
        a2 = np.array(step["attacker2"])
        spacings.append(np.linalg.norm(a1 - a2))
    return np.mean(spacings)


def plot_spacing_comparison(baseline_traj, shaped_traj, target_spacing):
    baseline_avg = average_spacing(baseline_traj)
    shaped_avg = average_spacing(shaped_traj)

    labels = ["Baseline agent\n(goal-only reward)", "Shaped agent\n(+ Barcelona spacing reward)", "Real Barcelona\n(from match data)"]
    values = [baseline_avg, shaped_avg, target_spacing]
    colors = ["#9CA3AF", "#A50044", "#004D98"]  # grey, Barca red, Barca blue

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Average teammate spacing (field units)")
    ax.set_title("Reward Shaping Effect: Agent Spacing vs. Real Barcelona Data")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{val:.1f}",
                 ha="center", fontweight="bold")
    plt.tight_layout()
    out_path = RESULTS_DIR / "spacing_comparison.png"
    plt.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")
    plt.close()


def plot_trajectory_comparison(baseline_traj, shaped_traj):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

    for ax, traj, title in zip(
        axes, [baseline_traj, shaped_traj], ["Baseline agent", "Shaped agent (Barcelona-informed)"]
    ):
        a1_path = np.array([s["attacker1"] for s in traj])
        a2_path = np.array([s["attacker2"] for s in traj])
        ball_path = np.array([s["ball"] for s in traj])

        ax.plot(a1_path[:, 0], a1_path[:, 1], color="#A50044", label="Attacker 1")
        ax.plot(a2_path[:, 0], a2_path[:, 1], color="#004D98", label="Attacker 2")
        ax.plot(ball_path[:, 0], ball_path[:, 1], "--", color="black", alpha=0.4, label="Ball")
        ax.set_title(title)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 60)
        ax.legend(fontsize=8)

    plt.tight_layout()
    out_path = RESULTS_DIR / "trajectory_comparison.png"
    plt.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")
    plt.close()


def main():
    baseline_traj = load_trajectory("baseline")
    shaped_traj = load_trajectory("shaped")
    target_spacing = load_target_spacing()

    plot_spacing_comparison(baseline_traj, shaped_traj, target_spacing)
    plot_trajectory_comparison(baseline_traj, shaped_traj)

    print("\nAll visuals generated. Add these PNGs to your README.")


if __name__ == "__main__":
    main()
