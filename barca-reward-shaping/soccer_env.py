"""
soccer_env.py
-------------
STEP 2 of the project.

WHAT THIS SCRIPT DOES:
Builds a tiny, simplified 2-vs-1 soccer environment that follows the
Gymnasium API (the standard interface stable-baselines3 expects). It is
NOT a realistic physics sim -- it's deliberately simple so it trains in
minutes, not days. Two attackers (your team) try to get the ball into a
goal while one defender tries to stop them.

WHY IT'S SIMPLE ON PURPOSE:
The goal of this project isn't to build a full soccer engine -- it's to
show that changing the REWARD FUNCTION (based on real Barcelona data)
changes the LEARNED BEHAVIOR. A minimal env makes that comparison fast
and easy to visualize, which is exactly what a job reviewer wants to see
in a portfolio piece: a clear, legible cause -> effect result.

KEY IDEA -- REWARD SHAPING:
  - BASELINE reward: +1 only when your team scores a goal.
  - SHAPED reward:    +1 for a goal, PLUS a small bonus every step for
                       keeping teammate spacing close to the real
                       Barcelona average computed in extract_tactics.py.

This file defines the environment. It does not train anything itself.

HOW TO RUN (just a sanity check, doesn't train):
    python src/soccer_env.py
"""

import json
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import spaces

TACTICS_PATH = Path(__file__).parent.parent / "data" / "tactics_summary.json"

FIELD_W, FIELD_H = 100.0, 60.0   # arbitrary field units
GOAL_Y_RANGE = (25.0, 35.0)      # goal mouth on the right edge
MAX_STEPS = 200
PLAYER_SPEED = 3.0


def load_target_spacing() -> float:
    """Reads the real Barcelona spacing number produced by
    extract_tactics.py. If that file doesn't exist yet, falls back to a
    reasonable default so this file can still be tested standalone.
    """
    if TACTICS_PATH.exists():
        with open(TACTICS_PATH) as f:
            data = json.load(f)
        # Scale StatsBomb pitch units (120x80) down to our field size
        raw_spacing = data["avg_spacing_pitch_units"]
        return raw_spacing * (FIELD_W / 120.0)
    return 20.0


class SoccerEnv(gym.Env):
    """A 2-attacker vs 1-defender soccer environment.

    Observation: positions of both attackers, the defender, and the ball.
    Action: each attacker independently chooses a direction to move in
            (up/down/left/right/stay) -- discrete for simplicity.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, use_reward_shaping: bool = False, render_mode=None):
        super().__init__()
        self.use_reward_shaping = use_reward_shaping
        self.target_spacing = load_target_spacing()
        self.render_mode = render_mode

        # 5 discrete moves per attacker (stay, up, down, left, right),
        # 2 attackers controlled jointly -> 25 combined actions
        self.action_space = spaces.Discrete(25)

        # obs = [a1_x, a1_y, a2_x, a2_y, def_x, def_y, ball_x, ball_y]
        low = np.array([0, 0] * 4, dtype=np.float32)
        high = np.array([FIELD_W, FIELD_H] * 4, dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

        self.trajectory_log = []  # stores positions each step, for visualize.py

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.attacker1 = np.array([10.0, 20.0])
        self.attacker2 = np.array([10.0, 40.0])
        self.defender = np.array([70.0, 30.0])
        self.ball = self.attacker1.copy()
        self.trajectory_log = [self._current_positions()]
        return self._get_obs(), {}

    def _current_positions(self):
        return {
            "attacker1": self.attacker1.copy(),
            "attacker2": self.attacker2.copy(),
            "defender": self.defender.copy(),
            "ball": self.ball.copy(),
        }

    def _get_obs(self):
        return np.concatenate(
            [self.attacker1, self.attacker2, self.defender, self.ball]
        ).astype(np.float32)

    def _move(self, pos, direction):
        moves = {
            0: np.array([0, 0]),
            1: np.array([0, PLAYER_SPEED]),
            2: np.array([0, -PLAYER_SPEED]),
            3: np.array([-PLAYER_SPEED, 0]),
            4: np.array([PLAYER_SPEED, 0]),
        }
        new_pos = pos + moves[direction]
        new_pos[0] = np.clip(new_pos[0], 0, FIELD_W)
        new_pos[1] = np.clip(new_pos[1], 0, FIELD_H)
        return new_pos

    def step(self, action):
        self.step_count += 1

        a1_action = action // 5
        a2_action = action % 5
        self.attacker1 = self._move(self.attacker1, a1_action)
        self.attacker2 = self._move(self.attacker2, a2_action)

        # Ball follows whichever attacker is closer (simple "possession" rule)
        d1 = np.linalg.norm(self.attacker1 - self.ball)
        d2 = np.linalg.norm(self.attacker2 - self.ball)
        self.ball = self.attacker1.copy() if d1 < d2 else self.attacker2.copy()

        # Defender moves toward the ball
        direction_to_ball = self.ball - self.defender
        if np.linalg.norm(direction_to_ball) > 0:
            self.defender += (
                direction_to_ball / np.linalg.norm(direction_to_ball) * PLAYER_SPEED
            )

        self.trajectory_log.append(self._current_positions())

        # --- Reward ---
        reward = 0.0
        scored = self.ball[0] >= FIELD_W and GOAL_Y_RANGE[0] <= self.ball[1] <= GOAL_Y_RANGE[1]
        if scored:
            reward += 10.0

        if self.use_reward_shaping:
            actual_spacing = np.linalg.norm(self.attacker1 - self.attacker2)
            # Reward is highest when spacing matches the real Barcelona
            # average -- penalize being either too clustered or too spread.
            spacing_error = abs(actual_spacing - self.target_spacing)
            reward += max(0.0, 1.0 - spacing_error / FIELD_W)

        terminated = bool(scored)
        truncated = self.step_count >= MAX_STEPS

        return self._get_obs(), reward, terminated, truncated, {}


if __name__ == "__main__":
    # Quick sanity check: random actions for a few steps, no training.
    env = SoccerEnv(use_reward_shaping=True)
    obs, _ = env.reset()
    total_reward = 0.0
    for _ in range(20):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        if terminated or truncated:
            break
    print(f"Ran 20 random steps. Total reward: {total_reward:.2f}")
    print(f"Target spacing from real Barcelona data: {env.target_spacing:.2f} field units")
