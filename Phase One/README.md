# Qiskit Fall Fest 2026 — PS-O2: Constrained Portfolio Optimization

A Phase 1 implementation of **Problem Statement PS-O2** using a QUBO formulation, exact classical enumeration, depth-one QAOA, and a comparative Processor A/Processor B simulation.

> **Scope:** This project uses the official PS-O2 return vector and covariance matrix from the Phase 1 guide. The risk-aversion parameter `q = 2` and constraint penalty `A = 20` are documented experimental choices because the guide does not prescribe numerical values for them. Processor results are simulated, not measurements from real quantum hardware.

## 1. Problem Statement

The task is to formulate a four-asset portfolio-selection problem with a return reward and risk penalty, subject to selecting exactly `k = 2` assets.

For binary decision variables \(x_i \in \{0,1\}\), the experiment minimizes

\[
C(x) = x^T \Sigma x - q\,\mu^T x + A\left(\sum_i x_i-k\right)^2.
\]

Here, `x[i] = 1` means asset `i` is selected. The penalty encourages exactly two selected assets.

### Problem inputs

Returns:

```text
mu = [0.12, 0.18, 0.10, 0.22]
```

Covariance / risk matrix:

```text
Sigma = [
  [0.04, 0.01, 0.02, 0.01],
  [0.01, 0.09, 0.01, 0.03],
  [0.02, 0.01, 0.05, 0.02],
  [0.01, 0.03, 0.02, 0.08]
]
```

Experimental settings used for the reported run:

- `k = 2` assets
- Risk-aversion coefficient `q = 2`
- Constraint penalty `A = 20`
- QAOA depth `p = 1`

The official guide supplies the return vector, matrix, and budget. It does **not** specify numerical values for `q` or `A`; those are chosen and documented by this project for the experiment.

## 2. Methodology

The notebook (`main.ipynb`) performs the following steps:

1. Loads and validates the PS-O2 inputs.
2. Enumerates all \(2^4 = 16\) bitstrings and evaluates the portfolio objective.
3. Converts the objective to an upper-triangular QUBO representation and checks its energy against the direct objective for all bitstrings.
4. Computes the exact classical optimum by exhaustive enumeration.
5. Builds a depth-one QAOA cost-and-mixer circuit and optimizes its parameters using a classical optimizer.
6. Calculates an ideal statevector output distribution as a baseline.
7. Transpiles the logical circuit for the Processor A and Processor B coupling maps.
8. Runs a synthetic-noise, 4096-shot comparison for the two processor configurations.
9. Exports comparison tables and plots to `results/`.

The notebook's results are simulations. They are not results from executing on real quantum hardware.

## 3. Classical and Ideal-QAOA Baseline

For the experimental settings above, exhaustive enumeration finds:

| Metric | Result |
|---|---:|
| Best feasible bitstring | `[0, 1, 0, 1]` |
| Selected asset indices (zero-based) | `[1, 3]` |
| Selected assets | 2 |
| Total return \(\mu^T x\) | 0.40 |
| Risk \(x^T \Sigma x\) | 0.23 |
| Objective including penalty | −0.57 |
| Ideal QAOA probability of the optimal bitstring | 12.4503% |
| Ideal QAOA probability of any feasible bitstring | 73.8718% |
| Ideal QAOA probability of an infeasible bitstring | 26.1282% |

The exact classical optimum is the reference solution for these chosen objective parameters. The ideal QAOA probability describes how often the optimum appears in the simulated distribution; it does not mean QAOA always returns the optimum.

## 4. Processor A vs Processor B

The following are the measured results from the notebook's reported synthetic-noise run with 4096 shots per processor configuration.

| Metric | Processor A | Processor B |
|---|---:|---:|
| Physical qubits in transpiled circuit | 5 | 9 |
| Transpiled circuit depth | 46 | 37 |
| Reference CX gates | 12 | 12 |
| Transpiled CX gates | 18 | 15 |
| Additional CX gates vs. reference | 6 | 3 |
| Explicit SWAP instructions after basis translation | 0 | 0 |
| SWAP-equivalent estimate (additional CX / 3) | 2 | 1 |
| Shots | 4096 | 4096 |
| Optimal portfolio hits | 471 | 486 |
| Optimal portfolio hit rate | 11.4990% | 11.8652% |
| Feasible samples | 2833 | 2861 |
| Feasible-output rate | 69.1650% | 69.8486% |
| Infeasible-output rate | 30.8350% | 30.1514% |
| Empirical mean objective | 6.974014 | 6.822458 |
| Best sampled feasible bitstring | `[0, 1, 0, 1]` | `[0, 1, 0, 1]` |
| Best sampled feasible objective | −0.57 | −0.57 |

In this run, Processor B had a lower transpiled depth (37 versus 46) and fewer CX gates (15 versus 18), along with slightly higher observed optimal-hit rate (11.8652% versus 11.4990%) and feasible-output rate (69.8486% versus 69.1650%). The hit-rate difference is small and comes from one finite-shot run; it should not be described as statistically significant without further analysis.

### Interpreting routing metrics

The final basis-translated circuits contain zero explicit SWAP instructions. This does not mean routing added no overhead: routing SWAPs can be decomposed into CX gates. The notebook therefore reports an **SWAP-equivalent estimate** based on additional CX gates. This estimate is not an exact routing-stage SWAP count.

The processor comparison is specific to the chosen circuit, topology, transpiler settings, and synthetic-noise model. It does not establish that one architecture is universally superior.

## 5. Repository Structure

```text
.
├── README.md
├── requirements.txt
├── main.ipynb
├── report.md
├── processors/
│   ├── processor_A.json
│   └── processor_B.json
├── src/
│   ├── __init__.py
│   ├── problem.py
│   ├── processors.py
│   ├── routing.py
│   ├── metrics.py
│   └── visualization.py
└── results/
    ├── figures/
    │   ├── processor_ab_circuit_metrics.png
    │   ├── processor_ab_noisy_quality.png
    │   └── processor_topologies.png
    └── tables/
        ├── benchmark_metadata.json
        ├── ideal_qaoa_distribution.csv
        ├── noisy_processor_comparison.csv
        ├── noisy_shot_distribution.csv
        ├── processor_ab_final_comparison.csv
        └── transpilation_metrics.csv
```

This tree documents the core files expected in the workflow. Keep it aligned with the files actually committed to GitHub; if any result filename differs in your repository, update that filename here. Git does not track empty folders by themselves, so `results/tables/` and `results/figures/` appear when they contain files.

### What the `src/` modules do

| File | Purpose |
|---|---|
| `src/__init__.py` | Makes `src` importable as a Python package. |
| `src/problem.py` | Defines the PS-O2 inputs and parameters, validates the portfolio problem, evaluates the objective, and builds/evaluates the QUBO representation. |
| `src/processors.py` | Loads and validates the Processor A/B topology and configuration data used by the experiment. |
| `src/routing.py` | Provides shared routines for transpiling the same logical circuit against each processor's coupling map. |
| `src/metrics.py` | Calculates comparable circuit/resource measurements, including circuit depth and CX-gate counts, plus routing-related metrics available from the transpilation workflow. |
| `src/visualization.py` | Provides plotting and visual-comparison functions for processor topologies and benchmark results. |

The notebook imports these shared modules so reusable logic is kept in `src/` instead of being duplicated in notebook cells. Keep `main.ipynb` and these modules consistent when updating the implementation.

### Other important files

- `main.ipynb` — end-to-end experiment and result generation.
- `processors/processor_A.json` and `processors/processor_B.json` — processor topology/configuration inputs.
- `results/tables/` — exported CSV/JSON result tables.
- `results/figures/` — generated comparison plots.
- `report.md` — detailed methodology, results, interpretation, and limitations.
- `requirements.txt` — Python dependencies needed to run the notebook.

## 6. How to Run

1. Open `main.ipynb` in Google Colab.
2. Restart the runtime to avoid relying on variables left over from earlier executions.
3. Run the notebook cells from top to bottom.
4. Confirm the notebook's final checks pass and the results under `results/tables/` and `results/figures/` are created.
5. Review `report.md` for the detailed formulation, results, and limitations.

Install the dependencies from `requirements.txt` if needed. The notebook's recorded runtime versions and dependency file should be checked together when reproducing the experiment in a different environment.

## 7. Reproducibility and Limitations

- The risk matrix and return vector in the reported experiment are the PS-O2 inputs from the Phase 1 guide.
- `q = 2` and `A = 20` are experimental choices, not values prescribed by the guide.
- QAOA uses `p = 1`; results may vary with optimizer settings and parameter initialization.
- The ideal statevector results and the synthetic-noise, finite-shot results are distinct and should not be conflated.
- The noisy comparison uses 4096 shots per processor configuration; observed hit rates can vary between runs.
- A successful optimizer termination does not prove global optimality.
- Additional CX gates are not an exact measurement of routing-stage SWAP count.
- All processor results are simulated and should not be described as real-device hardware results.
- Do not commit API keys, passwords, tokens, or other secrets.

## 8. Conclusion

This project formulates PS-O2 as a QUBO, validates the encoding over all 16 bitstrings, computes an exact classical baseline, and compares depth-one QAOA simulations transpiled for Processor A and Processor B. Under the documented experimental choices and the reported synthetic-noise run, Processor B had a shallower circuit and slightly higher observed optimal-hit and feasible-output rates. These results are specific to this setup and do not imply a universal architecture advantage.
