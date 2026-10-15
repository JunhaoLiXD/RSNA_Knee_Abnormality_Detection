"""Rank-crossing test between two public-leaderboard snapshots (D-022): stable witnesses are teams present in both
snapshots with unchanged submission count, last submission time, displayed score and membership. Reports our rank,
witnesses crossing from above us to below and the other way, and order reversals among the stable teams.
Usage: python rank_cross.py <snapshot dir before> <snapshot dir after> [team id]"""
import glob
import sys
import zipfile

import pandas as pd

TEAM = int(sys.argv[3]) if len(sys.argv) > 3 else 16678028


def load(d):
    z = sorted(glob.glob(d + "/*.zip"))[-1]
    with zipfile.ZipFile(z) as f:
        name = f.namelist()[0]
        lb = pd.read_csv(f.open(name))
    return name, lb.set_index("TeamId")


na, a = load(sys.argv[1])
nb, b = load(sys.argv[2])
print("before:", na, len(a), "teams | after:", nb, len(b), "teams")
for tag, lb in (("before", a), ("after", b)):
    r = lb.loc[TEAM]
    print(f"{tag}: rank {r.Rank}, score {r.Score}, submissions {r.SubmissionCount}, last {r.LastSubmissionDate}")
keys = ["SubmissionCount", "LastSubmissionDate", "Score", "TeamMemberUserNames"]
common = a.index.intersection(b.index).drop(TEAM)
stable = [t for t in common if all(str(a.at[t, k]) == str(b.at[t, k]) for k in keys)]
ra, rb = a.loc[stable, "Rank"], b.loc[stable, "Rank"]
us_a, us_b = a.at[TEAM, "Rank"], b.at[TEAM, "Rank"]
down = [t for t in stable if ra[t] < us_a and rb[t] > us_b]   # above us before, below us after
up = [t for t in stable if ra[t] > us_a and rb[t] < us_b]
order_a = ra.sort_values().index.tolist()
order_b = rb.sort_values().index.tolist()
reversals = sum(1 for x, y in zip(order_a, [t for t in order_b if t in set(order_a)]) if x != y)
print(f"stable teams {len(stable)} of {len(common)} common | witnesses above->below {len(down)}, below->above {len(up)} | "
      f"positions differing in stable order {reversals}")
if down:
    print("witness scores (above->below):", a.loc[down, "Score"].value_counts().to_dict())
if up:
    print("reverse witnesses:", a.loc[up, ["TeamName", "Score"]].to_string())
n = len(b)
sc = b.sort_values("Rank")["Score"].reset_index(drop=True)
for k, nm in ((10 + int(0.002 * n), "gold"), (int(0.05 * n), "silver"), (int(0.10 * n), "bronze")):
    print(f"{nm} cut rank {k} score {sc.iloc[k - 1]}")
