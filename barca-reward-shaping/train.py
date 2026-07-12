"""
train.py
--------
STEP 3 of the project.

WHAT THIS SCRIPT DOES:
Trains TWO separate RL agents using PPO (Proximal Policy Optimization,
a standard reinforcement learning algorithm) on the SoccerEnv:

  1. "baseline" agent  -> rewarded ONLY for scoring goals
  2. "shaped" agent     -> rewarded for scoring goals AND for keeping
                           the real Barcelona spacing pattern

Both agents are saved to models/, and their trajectories from a final
test episode are saved to results/ so visualize.py can turn them into
comparison plots and a GIF.

WHY TWO AGENTS:
A single trained agent proves nothing on its own. The COMPARISON is the
result: "here is what changes when I add tactical-data-driven reward
shaping." That comparison is the actual deliverable for your portfolio.

HOW TO RUN:
    python src/train.py
(Takes ~5-10 minutes on a laptop CPU for the short training run used here.)
"""

import json
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from soccer_env import SoccerEnv

MODELS_DIR = Path(__file__).parent.parent / "models"
RESULTS_DIR = Path(__file__).parent.parent / "results"
TRAIN_STEPS = 20_000  # kept small so this finishes in minutes, not hours


def train_agent(use_reward_shaping: bool, name: str) -> PPO:
    print(f"\n=== Training '{name}' agent (reward_shaping={use_reward_shaping}) ===")
    env = Monitor(SoccerEnv(use_reward_shaping=use_reward_shaping))
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=TRAIN_STEPS)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODELS_DIR / f"{name}_agent")
    print(f"Saved model to {MODELS_DIR / name}_agent.zip")
    return model


def run_test_episode(model: PPO, use_reward_shaping: bool, name: str):
    """Runs one full episode with the trained agent and saves the
    trajectory so visualize.py can plot/animate it.
    """
    env = SoccerEnv(use_reward_shaping=use_reward_shaping)
    obs, _ = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, _ = env.step(int(action))
        done = terminated or truncated

    # Convert trajectory log (numpy arrays) to plain lists for JSON
    log = [
        {k: v.tolist() for k, v in step.items()}
        for step in env.trajectory_log
    ]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"{name}_trajectory.json"
    with open(out_path, "w") as f:
        json.dump(log, f)
    print(f"Saved test trajectory to {out_path}")


def main():
    baseline_model = train_agent(use_reward_shaping=False, name="baseline")
    shaped_model = train_agent(use_reward_shaping=True, name="shaped")

    run_test_episode(baseline_model, use_reward_shaping=False, name="baseline")
    run_test_episode(shaped_model, use_reward_shaping=True, name="shaped")

    print("\nDone. Run src/visualize.py next to generate comparison plots.")


if __name__ == "__main__":
    main()
