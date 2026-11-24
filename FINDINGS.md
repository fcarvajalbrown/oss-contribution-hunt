# Findings

## Question

Which open-source projects accept AI-assisted contributions under a written policy, take pull requests, and answer outside contributors quickly?

## Policies

`data/ai_policies.csv` lists 40 projects with their stance, what disclosure they require, and a link to the source. Most game engines and game projects that publish a policy restrict or ban AI-generated code (Godot, Widelands, mGBA, the Zelda and Banjo recomps). Most infrastructure, language and scientific projects allow it with a human accountable for every line, and many ask for an `Assisted-by:` trailer or a line in the PR description. Kubernetes is the exception that requires disclosure but bans the trailer.

Policies change often. Read the linked page before you contribute.

## Responsiveness

`tools/pr_response_time.py` sampled the 40 most recent pull requests from outside contributors in each of 28 GitHub projects whose policy allows AI assistance, skipping PRs younger than 72 hours. The raw numbers are in `data/pr_response_2026-11-24.csv`.

- First response means the first comment or review by a human other than the author. Bot accounts are excluded, including automation accounts that post as ordinary users (`nodejs-github-bot`, `ansibot`).
- OpenSSL shows 0% merged because it lands changes by cherry-pick, not by merging the PR.
- One snapshot of 40 PRs per project. It describes recent behaviour, not a guarantee.

## Ranking

`tools/composite_rank.py` follows the OECD/JRC Handbook on Constructing Composite Indicators (2008):

1. Indicators: share of PRs answered by a human within 24 hours, median hours to first answer (log, inverted), share merged.
2. Min-max normalisation with a 0.01 floor.
3. Equal weights, geometric aggregation, so a project that answers fast but never merges cannot hide the weak indicator.
4. Robustness: 10,000 Monte Carlo runs with Dirichlet(1,1,1) weights, alternating geometric and arithmetic aggregation, fixed seed. Each project gets a median rank and a 5th-95th percentile rank range.

Result in `data/composite_ranking_2026-11-24.csv`. Top eight:

| Rank | Project | Rank range | Answered in 24 h | Median first answer | Merged |
|---|---|---|---|---|---|
| 1 | Ghostty | 1-5 | 55% | 1.7 h | 62% |
| 2 | Privacy Badger (EFF) | 1-4 | 80% | 5.3 h | 52% |
| 3 | Neovim | 1-11 | 68% | 1.8 h | 32% |
| 4 | systemd | 3-9 | 55% | 11.3 h | 55% |
| 5 | Ruff | 4-9 | 60% | 11.9 h | 50% |
| 6 | NumPy | 3-15 | 70% | 4.9 h | 28% |
| 7 | Apache Airflow | 3-10 | 45% | 3.2 h | 40% |
| 8 | ESLint | 4-12 | 65% | 9.9 h | 35% |

Ghostty and Privacy Badger overlap almost completely, so the data cannot separate them. Neovim's range is wide because its merge rate is low. At the bottom, uv left 25 of 40 sampled outside PRs unanswered, and pybind11's range (4-28) is too wide to read.

## Not covered

The Linux kernel, Mesa, Firefox, Fedora and Debian allow AI-assisted work but do not take GitHub pull requests, so the script cannot measure them.
