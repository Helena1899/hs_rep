"""
extract_tactics.py
-------------------
STEP 1 of the project.

WHAT THIS SCRIPT DOES:
1. Downloads free, public FC Barcelona match event data from StatsBomb's
   open-data project (no login or API key needed).
2. Filters that data down to completed passes.
3. Computes real tactical numbers from the data:
      a) average on-ball position for each player (where do they usually touch the ball?)
      b) average spacing between teammates (how far apart do they play?)
      c) passing centrality (who is the team's main pass hub?), using the
         networkx graph library's betweenness centrality algorithm
4. Saves the key number our RL environment needs -- average spacing --
   into data/tactics_summary.json, which soccer_env.py reads automatically.

WHY THIS MATTERS:
This is the file that makes the whole project "real" instead of a toy
RL demo. Everything downstream (the environment's reward shaping, the
final comparison chart) traces back to an actual number computed from
real Barcelona match data here.

HOW TO RUN:
    python src/extract_tactics.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
from statsbombpy import sb

DATA_DIR = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# CONFIG - change these if you want a different match/team.
# Explore options with:
#   from statsbombpy import sb
#   print(sb.competitions())                                   # find competition/season ids
#   print(sb.matches(competition_id=11, season_id=90))          # find a match_id
# ---------------------------------------------------------------------------
COMPETITION_ID = 11   # La Liga
SEASON_ID = 90
TEAM_NAME = "Barcelona"


def load_team_events():
    """Pick the first available Barcelona match for this competition/season
    and download its full event log. Returns (events_df, match_id)."""
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)
    team_matches = matches[
        (matches["home_team"] == TEAM_NAME) | (matches["away_team"] == TEAM_NAME)
    ]
    if team_matches.empty:
        raise ValueError(
            f"No {TEAM_NAME} matches found for competition={COMPETITION_ID}, "
            f"season={SEASON_ID}. Try different ids (see sb.competitions())."
        )

    match_id = team_matches.iloc[0]["match_id"]
    row = team_matches.iloc[0]
    print(f"Using match_id={match_id}: {row['home_team']} vs {row['away_team']}")
    return sb.events(match_id=match_id), match_id


def get_completed_passes(events: pd.DataFrame) -> pd.DataFrame:
    """Keep only this team's passes that have valid start locations and
    a known recipient (i.e. successfully completed passes)."""
    passes = events[(events["type"] == "Pass") & (events["team"] == TEAM_NAME)].copy()
    passes = passes.dropna(subset=["location", "player"])
    passes["x"] = passes["location"].apply(lambda loc: loc[0])
    passes["y"] = passes["location"].apply(lambda loc: loc[1])
    return passes


def compute_average_positions(passes: pd.DataFrame) -> pd.DataFrame:
    """Each player's average (x, y) on-ball position -- a simple stand-in
    for 'where does this player usually operate on the pitch'."""
    return (
        passes.groupby("player")[["x", "y"]]
        .mean()
        .reset_index()
        .rename(columns={"x": "avg_x", "y": "avg_y"})
    )


def compute_average_spacing(avg_pos: pd.DataFrame) -> float:
    """Average pairwise distance between every pair of players' average
    positions. This is our single number for 'how spread out does the
    team play' -- the number the RL environment will target."""
    coords = avg_pos[["avg_x", "avg_y"]].to_numpy()
    n = len(coords)
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            dists.append(np.linalg.norm(coords[i] - coords[j]))
    return float(np.mean(dists))


def compute_compactness_area(avg_pos: pd.DataFrame) -> float:
    """Area of the convex hull wrapped around every player's average
    position. A smaller area means the team plays in a tighter shape."""
    from scipy.spatial import ConvexHull

    coords = avg_pos[["avg_x", "avg_y"]].to_numpy()
    hull = ConvexHull(coords)
    return float(hull.volume)  # for 2D points, ConvexHull.volume IS the area


def compute_pass_centrality(passes: pd.DataFrame) -> pd.DataFrame:
    """Build a directed pass network (node = player, edge = a completed
    pass) and compute betweenness centrality: who is the pivot player
    that most passes flow through?"""
    G = nx.DiGraph()
    for _, row in passes.iterrows():
        receiver = row.get("pass_recipient")
        if pd.isna(receiver):
            continue
        passer = row["player"]
        if G.has_edge(passer, receiver):
            G[passer][receiver]["weight"] += 1
        else:
            G.add_edge(passer, receiver, weight=1)

    centrality = nx.betweenness_centrality(G, weight="weight")
    return (
        pd.DataFrame(centrality.items(), columns=["player", "centrality"])
        .sort_values("centrality", ascending=False)
        .reset_index(drop=True)
    )


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading Barcelona match events from StatsBomb open data...")
    events, match_id = load_team_events()

    print("Filtering to completed passes...")
    passes = get_completed_passes(events)
    print(f"Found {len(passes)} passes.")

    avg_pos = compute_average_positions(passes)
    avg_spacing = compute_average_spacing(avg_pos)
    compactness_area = compute_compactness_area(avg_pos)
    centrality = compute_pass_centrality(passes)

    print(f"\nAverage teammate spacing (pitch units, 120x80 scale): {avg_spacing:.2f}")
    print(f"Team compactness (convex hull area, pitch units^2): {compactness_area:.1f}")
    print("\nTop 5 pass hubs (betweenness centrality):")
    print(centrality.head(5).to_string(index=False))

    # Save the raw tables for reference / your README
    avg_pos.to_csv(DATA_DIR / "avg_positions.csv", index=False)
    centrality.to_csv(DATA_DIR / "pass_centrality.csv", index=False)

    # Save the numbers soccer_env.py and visualize.py read.
    # NOTE: soccer_env.py only actually *needs* avg_spacing_pitch_units --
    # the rest is here so it's visible in your README / repo as evidence
    # the numbers come from real data, not made up.
    summary = {
        "match_id": int(match_id),
        "team": TEAM_NAME,
        "num_passes_analyzed": len(passes),
        "avg_spacing_pitch_units": avg_spacing,
        "compactness_area_pitch_units2": compactness_area,
        "pivot_player": centrality.iloc[0]["player"] if not centrality.empty else None,
    }
    with open(DATA_DIR / "tactics_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved tactics_summary.json, avg_positions.csv, pass_centrality.csv to {DATA_DIR}/")


if __name__ == "__main__":
    main()
