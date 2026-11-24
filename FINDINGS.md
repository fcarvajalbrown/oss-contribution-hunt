# Findings

## Question

Which open-source projects accept AI-assisted contributions under a written policy, take pull requests, and answer outside contributors quickly?

## Policies

`data/ai_policies.csv` lists 70 projects with their stance, what disclosure they require, and a link to the source. Most game engines and game projects that publish a policy restrict or ban AI-generated code (Godot, Widelands, mGBA, Avian, the Zelda and Banjo recomps), and so does Ardour among audio projects. Most infrastructure, language and scientific projects allow it with a human accountable for every line, and many ask for an `Assisted-by:` trailer or a line in the PR description. Kubernetes is the exception that requires disclosure but bans the trailer; cpal is one of the few that does not require disclosure at all.

The second round of searches covered scientific and numerical software and game and audio tooling in Python and Rust. Scientific Python projects converge on the SciPy/SymPy template: disclose the tools and which parts they wrote, no autonomous agents, no AI writing your replies to reviewers. Several (MQT, Matplotlib, silx, LLVM) close AI-assisted PRs on issues reserved for newcomers.

Policies change often. Read the linked page before you contribute.

## Responsiveness

`tools/pr_response_time.py` sampled the 40 most recent pull requests from outside contributors in each of 56 GitHub projects whose policy allows or restricts (but does not ban) AI assistance, skipping PRs younger than 72 hours. The raw numbers are in `data/pr_response_2026-11-24.csv`.

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
| 1 | MQT Core (Munich Quantum Toolkit) | 1-5 | 65% | 3.9 h | 78% |
| 2 | Astropy | 1-6 | 62% | 1.0 h | 62% |
| 3 | statsmodels | 1-10 | 70% | 11.4 h | 80% |
| 4 | Ghostty | 2-9 | 55% | 1.7 h | 62% |
| 5 | Privacy Badger (EFF) | 1-8 | 80% | 5.3 h | 52% |
| 6 | Matplotlib | 6-16 | 60% | 4.5 h | 48% |
| 7 | Neovim | 2-27 | 68% | 1.8 h | 32% |
| 8 | systemd | 7-17 | 55% | 11.3 h | 55% |

The top five overlap, so the data cannot order them reliably. Neovim's range is wide because its merge rate is low. Adding 28 projects moved every earlier project down, because min-max normalisation rescales against the whole set. At the bottom, Rapier answered 5 of 40 sampled outside PRs and Symphonia's median first answer was 309 hours; uv left 25 of 40 unanswered, and pybind11's range (12-54) is too wide to read.

## Not covered

The Linux kernel, Mesa, Firefox, Fedora and Debian allow AI-assisted work but do not take GitHub pull requests, so the script cannot measure them.
