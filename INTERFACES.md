# Shared Interfaces --- Draft for Approval

**NOT FROZEN. All three members must approve this document before coding
against it.**

## Conventions to freeze

-   Map each bit/index to Asset 1--4; `1` means selected.
-   Document Qiskit measurement-string decoding and bit order.
-   Distinguish portfolio objective from penalized objective.
-   Document maximization-to-QAOA cost sign convention and QUBO constant
    offset.
-   Use one canonical objective evaluator.
-   Use one shared problem configuration.

## Proposed contracts (not implemented)

-   `load_problem(config)` in `src/problem.py`: validated data; reject
    missing official matrix when official benchmark requested; label
    custom matrices.
-   `build_qubo(problem)` in `src/qubo.py`: coefficients plus variable
    order, sign convention, constant offset and
    minimization/maximization convention.
-   `solve_classically(problem)` in `src/classical_solver.py`: best
    feasible portfolio with exactly two assets, objective and evaluation
    details; report penalized unconstrained optimum separately if
    calculated.
-   `run_qaoa(qubo, config)` in `src/qaoa_solver.py`: counts, decoded
    samples, settings and metadata.
-   `load_processor(name)` in `src/processors.py`: validated
    configuration and coupling map.
-   `benchmark_circuit(circuit, processor, config)` in `src/routing.py`:
    transpiled circuit, CX count, depth, SWAP metric and settings.
-   `evaluate_results(...)` in `src/metrics.py`: valid-solution
    frequency and documented objective comparisons.

Before coding, agree on exact arguments, return keys/types, error
behavior, seed handling, and how runs identify custom versus official
matrices. Change this file only through team review.
