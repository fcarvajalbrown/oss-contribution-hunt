import argparse
import csv
import json
import statistics
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTSIDE_ROLES = {"CONTRIBUTOR", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "NONE"}
COLUMNS = ["repo", "outside_prs", "responded", "median_hours", "p75_hours", "within_24h_pct",
           "merged_pct", "closed_silent", "open_unanswered", "oldest_unanswered_days", "window_start", "window_end"]

QUERY = """
query($owner: String!, $name: String!, $count: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: $count, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        createdAt closedAt mergedAt state authorAssociation
        author { __typename login }
        comments(first: 15) { nodes { createdAt author { __typename login } } }
        reviews(first: 15) { nodes { submittedAt author { __typename login } } }
      }
    }
  }
}
"""


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def is_bot(actor):
    if not actor:
        return True
    login = actor.get("login", "").lower()
    return actor.get("__typename") == "Bot" or login.endswith("[bot]") or login.endswith("bot")


def fetch_page(repo, count, cursor):
    owner, name = repo.split("/", 1)
    args = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={owner}", "-F", f"name={name}",
            "-F", f"count={count}"]
    if cursor:
        args += ["-F", f"cursor={cursor}"]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"{repo}: {result.stderr.strip()}")
    return json.loads(result.stdout)["data"]["repository"]["pullRequests"]


def first_response(pr):
    author = (pr.get("author") or {}).get("login")
    times = []
    for comment in pr["comments"]["nodes"]:
        if not is_bot(comment.get("author")) and comment["author"]["login"] != author:
            times.append(parse_time(comment["createdAt"]))
    for review in pr["reviews"]["nodes"]:
        if review.get("submittedAt") and not is_bot(review.get("author")) and review["author"]["login"] != author:
            times.append(parse_time(review["submittedAt"]))
    return min(times) if times else None


def outside_prs(repo, wanted, min_age_hours, max_pages):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=min_age_hours)
    found, cursor = [], None
    for _ in range(max_pages):
        page = fetch_page(repo, 50, cursor)
        for pr in page["nodes"]:
            created = parse_time(pr["createdAt"])
            if created > cutoff or is_bot(pr.get("author")) or pr["authorAssociation"] not in OUTSIDE_ROLES:
                continue
            found.append(pr)
            if len(found) >= wanted:
                return found
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return found


def summarize(repo, prs):
    now = datetime.now(timezone.utc)
    hours, unanswered_ages, merged, closed_silent = [], [], 0, 0
    for pr in prs:
        created = parse_time(pr["createdAt"])
        answer = first_response(pr)
        if pr.get("mergedAt"):
            merged += 1
        if answer:
            hours.append((answer - created).total_seconds() / 3600)
        elif pr["state"] == "OPEN":
            unanswered_ages.append((now - created).days)
        else:
            closed_silent += 1
    created_times = sorted(parse_time(pr["createdAt"]) for pr in prs)
    row = {"repo": repo, "outside_prs": len(prs), "responded": len(hours)}
    row["median_hours"] = round(statistics.median(hours), 1) if hours else ""
    row["p75_hours"] = round(statistics.quantiles(hours, n=4)[2], 1) if len(hours) >= 4 else ""
    row["within_24h_pct"] = round(100 * sum(h <= 24 for h in hours) / len(prs)) if prs else ""
    row["merged_pct"] = round(100 * merged / len(prs)) if prs else ""
    row["closed_silent"] = closed_silent
    row["open_unanswered"] = len(unanswered_ages)
    row["oldest_unanswered_days"] = max(unanswered_ages) if unanswered_ages else ""
    row["window_start"] = created_times[0].date().isoformat() if created_times else ""
    row["window_end"] = created_times[-1].date().isoformat() if created_times else ""
    return row


def done_repos(out):
    if not out.exists():
        return set()
    with out.open(newline="", encoding="utf-8") as handle:
        return {row["repo"] for row in csv.DictReader(handle)}


def main():
    parser = argparse.ArgumentParser(description="Time to first human response on pull requests from outside contributors.")
    parser.add_argument("repos", nargs="+", help="owner/name GitHub repositories")
    parser.add_argument("--out", required=True, type=Path, help="CSV to append to; repos already in it are skipped")
    parser.add_argument("--prs", type=int, default=40, help="outside-contributor PRs to sample per repo")
    parser.add_argument("--min-age-hours", type=int, default=72, help="ignore PRs younger than this")
    parser.add_argument("--max-pages", type=int, default=10, help="pages of 50 PRs to scan per repo")
    args = parser.parse_args()

    skip = done_repos(args.out)
    new_file = not args.out.exists()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        for repo in args.repos:
            if repo in skip:
                print(f"skip {repo} (already in {args.out})")
                continue
            try:
                row = summarize(repo, outside_prs(repo, args.prs, args.min_age_hours, args.max_pages))
            except RuntimeError as error:
                print(f"error {error}", file=sys.stderr)
                continue
            writer.writerow(row)
            handle.flush()
            print(json.dumps(row))


if __name__ == "__main__":
    main()
