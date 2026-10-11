# Qiskit Fall Fest 2026 --- PS-O2

Shared workspace for our three-person team implementing PS-O2:
Constrained Portfolio Optimization.

## Confirmed scope

-   Phase 1: Processor A and Processor B only.
-   Returns: `[5, 3, 4, 2]`; risk aversion `lambda = 2`; budget penalty
    `A = 20`; exactly `k = 2` assets; QAOA baseline `p = 1`.
-   Organizer-confirmed penalized objective:
    `maximize r.T @ x - 2 * x.T @ Sigma @ x - 20 * (sum(x) - 2)**2`.
-   The common official 4×4 risk matrix is pending. Never invent it or
    label custom-matrix results as official.

## Source of truth

1.  Official `Problem_Statment_Details.pdf` and organizer
    clarifications.
2.  `TEAM_IMPLEMENTATION_PLAN.md`.
3.  Team-approved `INTERFACES.md`, configuration and tests.
4.  AI suggestions only if consistent with the above.

## Repository

`src/` reusable code; `tests/` automated tests; `processors/` processor
configurations; `data/` inputs; `results/` generated outputs;
`main.ipynb` reproducible experiment; `report.md` analysis.

## Setup

Use Google Colab for execution and GitHub for version control.
`requirements.txt` is an initial scaffold, not a tested or pinned
environment. Validate it in a clean runtime before benchmarking.

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd qiskit-fallfest-ps-o2
pip install -r requirements.txt
pytest -q
```

Do not claim tests pass until executed. Before coding, read
`TEAM_IMPLEMENTATION_PLAN.md`, `AI_WORKING_RULES.md`, and approve
`INTERFACES.md`. Work on feature branches and merge only reviewed,
tested changes.

Never commit secrets. Every reported result must come from an actual run
and include reproducibility details. Keep custom-matrix results separate
from official common-matrix results.
