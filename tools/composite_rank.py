import argparse
import csv
import math
import random
import statistics
from pathlib import Path

FLOOR = 0.01


def load(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["median_hours"]]
    for row in rows:
        row["x1"] = float(row["within_24h_pct"])
        row["x2"] = -math.log(max(float(row["median_hours"]), 0.1))
        row["x3"] = float(row["merged_pct"])
    return rows


def normalise(rows, key):
    values = [row[key] for row in rows]
    low, high = min(values), max(values)
    for row in rows:
        row["z" + key[1]] = max((row[key] - low) / (high - low), FLOOR) if high > low else 1.0


def score(z, weights, geometric):
    if geometric:
        return math.exp(sum(w * math.log(v) for w, v in zip(weights, z)))
    return sum(w * v for w, v in zip(weights, z))


def ranks(rows, weights, geometric):
    scored = sorted(rows, key=lambda row: score((row["z1"], row["z2"], row["z3"]), weights, geometric), reverse=True)
    return {row["repo"]: position for position, row in enumerate(scored, 1)}


def dirichlet(rng, size):
    draws = [rng.gammavariate(1.0, 1.0) for _ in range(size)]
    total = sum(draws)
    return [draw / total for draw in draws]


def main():
    parser = argparse.ArgumentParser(description="OECD/JRC-style composite ranking of pr_response_time.py output.")
    parser.add_argument("csv", type=Path, help="output of pr_response_time.py")
    parser.add_argument("--runs", type=int, default=10000, help="Monte Carlo runs")
    parser.add_argument("--seed", type=int, default=20261124)
    parser.add_argument("--out", type=Path, help="optional CSV of the ranking")
    args = parser.parse_args()

    rows = load(args.csv)
    for key in ("x1", "x2", "x3"):
        normalise(rows, key)
    base = ranks(rows, (1 / 3, 1 / 3, 1 / 3), geometric=True)
    rng = random.Random(args.seed)
    samples = {row["repo"]: [] for row in rows}
    for run in range(args.runs):
        weights = dirichlet(rng, 3)
        for repo, position in ranks(rows, weights, geometric=run % 2 == 0).items():
            samples[repo].append(position)

    table = []
    for row in rows:
        positions = sorted(samples[row["repo"]])
        table.append({
            "repo": row["repo"],
            "base_rank": base[row["repo"]],
            "base_score": round(score((row["z1"], row["z2"], row["z3"]), (1 / 3, 1 / 3, 1 / 3), True), 3),
            "median_rank": statistics.median(positions),
            "p5_rank": positions[int(0.05 * (len(positions) - 1))],
            "p95_rank": positions[int(0.95 * (len(positions) - 1))],
            "within_24h_pct": row["within_24h_pct"],
            "median_hours": row["median_hours"],
            "merged_pct": row["merged_pct"],
        })
    table.sort(key=lambda item: item["base_rank"])
    for item in table:
        print(f'{item["base_rank"]:>2}  {item["repo"]:<40} score {item["base_score"]:<6} '
              f'MC median {item["median_rank"]:<5} range {item["p5_rank"]}-{item["p95_rank"]}  '
              f'24h {item["within_24h_pct"]}%  median {item["median_hours"]} h  merged {item["merged_pct"]}%')
    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)


if __name__ == "__main__":
    main()
