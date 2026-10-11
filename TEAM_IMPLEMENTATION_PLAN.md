# Team Implementation Plan --- PS-O2

**Status: Draft. All three members must review and approve before
implementation.**

## 1. Authoritative sources

`Problem_Statment_Details.pdf` is the sole source for PS-specific
requirements. The organizer's written clarification confirms the
equation and parameters. The updated Challenge Guide is used for
repository/reproducibility workflow. If information conflicts or is
missing, stop and resolve it; do not guess.

## 2. Confirmed formulation

`maximize r.T @ x - 2 * x.T @ Sigma @ x - 20 * (sum(x) - 2)**2`

-   `r = [5, 3, 4, 2]`
-   `lambda = 2` is risk aversion.
-   `A = 20` is the budget penalty.
-   `x_i` is binary and exactly `k = 2` assets must be selected.
-   `Sigma` is the 4×4 risk matrix, not yet supplied as common official
    data.
-   QAOA baseline `p = 1`.
-   Phase 1 compares Processor A and Processor B. Processor C and custom
    Processor D are out of scope.

Distinguish the portfolio objective `r.T @ x - 2 * x.T @ Sigma @ x` from
the penalized objective. Evaluate feasible portfolios separately from
the unconstrained penalized optimum.

## 3. Risk-matrix policy

Keep `Sigma` configurable. Until the official matrix is provided, use
custom matrices only for clearly labelled development/experimental runs.
Do not call these official results. Record the matrix
source/configuration and confirm with organizers whether custom-matrix
results are expected in the Phase 1 submission. Rerun the official
benchmark when the common matrix is released.

## 4. Member responsibilities

### Member 1 --- Mathematics and classical reference

Owns `src/problem.py`, `src/qubo.py`, `src/classical_solver.py`, and
tests. Validate inputs, implement/document objective and QUBO
conventions, enumerate 16 bitstrings and six feasible portfolios,
produce the best feasible classical reference, and test QUBO
consistency.

### Member 2 --- QAOA

Owns `src/qaoa_solver.py` and tests. Implement `p=1`, consume the shared
QUBO, test bit ordering/decoding, return counts and metadata, calculate
valid-solution frequency, and distinguish most-frequent sample from best
observed valid sample.

### Member 3 --- Processor A/B

Owns `processors/processor_A.json`, `processors/processor_B.json`,
`src/processors.py`, `src/routing.py`, and tests. Validate topologies,
test transpilation with a small circuit, benchmark the same agreed
logical QAOA circuit on A and B, and record CX count, depth, SWAP
overhead, and settings. Do not invent noise parameters.

### Integration lead

One of the three members maintains shared interfaces, reviews pull
requests, runs integration tests, assembles the notebook and checks that
reported outputs match actual runs. Module ownership remains with each
member.

## 5. Parallel workflow

Agree on `INTERFACES.md` before independent coding. Assign one primary
owner per file. Use feature branches, small commits, pull requests,
tests, and review. Do not merge untested code. Do not change shared
interfaces, math conventions, dependencies, or scope without team
review. AI suggestions are proposals, not requirements.

## 6. Implementation order

1.  Repository, branches and clean environment.
2.  Freeze interfaces, bit order, objective/QUBO convention.
3.  Validate inputs.
4.  Build QUBO and compare with direct math for all 16 bitstrings.
5.  Verify exact classical feasible baseline.
6.  Implement QAOA `p=1` using approved QUBO.
7.  Validate processor configurations and transpilation.
8.  Benchmark the same logical circuit on A and B.
9.  Generate metrics, tables and figures.
10. Assemble `main.ipynb`, README and report.
11. Restart runtime and run from a clean environment.

Preliminary tasks can run in parallel; final integration must respect
dependencies.

## 7. Required safeguards

Use one canonical objective evaluator. Test bit order. Document sign
convention and constant offset. Do not assume the penalty guarantees a
feasible optimum; check it. Define handling for zero/negative classical
objective ratios. Record shots, simulator, optimizer, seeds where
supported, transpiler settings, versions and input configuration.
Successful execution alone does not prove mathematical correctness.

## 8. Reporting

Report the classical optimal feasible portfolio/objective, QAOA results,
documented quantum/classical comparison, valid-solution frequency, CX
count, circuit depth, SWAP overhead for A and B, architecture
interpretation, limitations and reproducibility. Results must be actual
measurements.

## 9. Change control and acknowledgement

Changes to objective, parameters, scope, interfaces, metrics, topology
or dependencies require team review and updated tests. Each member must
confirm they understand their responsibilities and will not silently
change shared assumptions.
