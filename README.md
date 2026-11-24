<p align="center">
  <img src="assets/logo.svg" alt="oss-contribution-hunt logo: a stopwatch whose hand is a merge arrow" width="120" height="120">
</p>

<h1 align="center">oss-contribution-hunt</h1>

<p align="center">
  <a href="https://github.com/fcarvajalbrown/oss-contribution-hunt/commits/main"><img src="https://img.shields.io/github/last-commit/fcarvajalbrown/oss-contribution-hunt" alt="Last commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-MIT-blue" alt="Code licence: MIT"></a>
  <a href="LICENSE-DATA"><img src="https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey" alt="Data licence: CC BY 4.0"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
</p>

Find open-source projects that accept AI-assisted contributions under a written policy and answer outside contributors quickly.

If you use AI tools to write code and want your pull requests read, two things matter: whether the project allows the work at all, and whether anyone will answer. This repo collects the first and measures the second.

## What is here

- `data/ai_policies.csv`: 40 projects, their AI contribution stance, the disclosure they ask for, and a link to the policy.
- `data/pr_response_*.csv`: time to first human answer on outside-contributor PRs for 28 projects.
- `data/composite_ranking_*.csv`: those 28 ranked with an OECD/JRC composite indicator and a Monte Carlo robustness check.
- `FINDINGS.md`: method, results and limits.
- `tools/`: the two scripts that produce the numbers.

## Run it on your own list

Needs Python 3.10+ and the GitHub CLI (`gh`) logged in. No other dependencies.

```
python -I tools/pr_response_time.py --out results.csv owner/repo owner/repo
python -I tools/composite_rank.py results.csv --out ranking.csv
```

`pr_response_time.py` appends one row per repository and skips any already in the CSV, so a stopped run resumes with the same command. Very busy repositories need `--max-pages 40` to reach PRs older than the 72-hour cutoff.

Columns in the results CSV:

| Column | Meaning |
|---|---|
| `median_hours`, `p75_hours` | Hours from opening to the first comment or review by a human other than the author |
| `within_24h_pct` | Share of sampled PRs answered by a human within 24 hours |
| `merged_pct` | Share merged (projects that cherry-pick show 0) |
| `closed_silent` | Closed with no human comment or review |
| `open_unanswered`, `oldest_unanswered_days` | Still open with no human answer |

## Before you contribute

Read the project's own policy. Many require you to state AI use in the PR or with an `Assisted-by:` trailer; Kubernetes requires disclosure but forbids the trailer. Policies here change month to month.

## Licence

Code under MIT (`LICENSE`). Data and findings under CC BY 4.0 (`LICENSE-DATA`).
