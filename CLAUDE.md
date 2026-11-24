# CLAUDE.md

Public repo that answers one question: which open-source projects accept AI-assisted contributions and answer outside contributors quickly. Read `FINDINGS.md` before changing anything.

- `data/ai_policies.csv` is the policy list. Every row links to the page it came from. Add a row only after reading that page; a news article or third-party list is marked as such in `notes`.
- New measurements go in new dated CSVs (`data/pr_response_<date>.csv`); never overwrite an old one. Update `FINDINGS.md` to point at the new files.
- The ranking method (indicators, normalisation, weights, aggregation, Monte Carlo) is fixed in `FINDINGS.md`. Changing it is Felipe's decision; ask first.
- The scripts use only the standard library and `gh`. Keep it that way so anyone can run them.
- README and FINDINGS are read by strangers: plain English, no names of AI products or vendors.
