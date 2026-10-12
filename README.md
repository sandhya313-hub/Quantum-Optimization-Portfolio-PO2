# Qiskit Fall Fest 2026 — PS-O2: Constrained Portfolio Optimization

A Qiskit Fall Fest 2026 Phase 1 implementation of PS-O2 using QUBO formulation, classical exhaustive search, QAOA with p = 1, and a comparative Processor A/B transpilation study.

**Status:** Preliminary experimental implementation using a custom risk matrix. Not an official common-matrix benchmark.

## 1. Problem Statement

The objective defined by the organizers is:

```text
Maximize:
f(x) = r.T @ x - 2 * x.T @ Sigma @ x
       - 20 * (sum(x) - 2)^2
```

Parameters:

- Returns: `r = [5, 3, 4, 2]`
- Risk aversion: `lambda = 2`
- Budget penalty: `A = 20`
- Target portfolio size: `k = 2`
- QAOA depth: `p = 1`
- Decision variables: binary values indicating whether each asset is selected

## 2. Risk Matrix

The organizers stated that the common official 4 × 4 risk matrix would be supplied for the later benchmark. Custom matrices are permitted for additional experiments if they are clearly documented and kept separate from official benchmark results.

This repository currently contains preliminary experiments using `SIGMA_TEST`, a custom matrix documented in `report.md` and `main.ipynb`.

**Do not interpret the reported numerical results as official common-matrix benchmark results.**

## 3. Repository Structure

```text
.
├── README.md
├── requirements.txt
├── main.ipynb
├── report.md
├── temporary_experiment_results.json
├── processors/
└── results/
```

The notebook contains the mathematical formulation, QUBO verification, classical baseline, QAOA simulation, probability calculations, and Processor A/B transpilation experiments. The report documents the methodology, measurements, and limitations.

## 4. Environment

The experiment was developed in Google Colab.

Recorded runtime versions include:

- Python 3.13.16
- NumPy 2.1.3
- Qiskit 2.5.2
- Qiskit Aer 0.17.2

The `requirements.txt` file lists the main Python dependencies. A successful clean-environment installation and end-to-end reproducibility check must be confirmed before claiming the environment is fully validated.

## 5. How to Run

1. Open `main.ipynb` in Google Colab.
2. Install the dependencies listed in `requirements.txt` if they are not already installed.
3. Run the notebook cells in order.
4. Confirm that the QUBO verification, classical baseline, QAOA simulation, and processor comparison cells complete successfully.
5. Review the outputs and limitations in `report.md`.

The notebook currently uses a custom experimental risk matrix. The corresponding results must remain labeled as preliminary.

## 6. Methodology

The implementation:

1. Defines the organizer-provided objective parameters.
2. Builds a QUBO representation of the negative maximization objective.
3. Checks the QUBO conversion against all 16 possible binary portfolios.
4. Evaluates all portfolios using a classical exhaustive-search baseline.
5. Builds a depth-one QAOA circuit.
6. Optimizes QAOA parameters using COBYLA with multiple starting points.
7. Evaluates portfolio measurement probabilities using an ideal statevector simulator.
8. Transpiles the same logical circuit for Processor A and Processor B.
9. Records circuit depth, CX gates, and routing-stage SWAP instructions.

## 7. Preliminary Results

All values below refer to the custom experimental matrix.

- Best feasible classical portfolio: assets 0 and 2.
- Best feasible objective value: `7.42`.
- Best QAOA candidate expected QUBO cost: approximately `1.70133519`.
- Probability of measuring the classical-optimal portfolio: approximately `29.23%`.
- Probability of selecting exactly two assets: approximately `63.68%`.

### Processor Comparison

| Metric | Processor A | Processor B |
|---|---:|---:|
| Physical qubits in transpiled output | 5 | 9 |
| Final circuit depth | 91 | 85 |
| Final CX gates | 21 | 24 |
| Routing-stage SWAP instructions | 3 | 4 |

The measurements use the same logical circuit, basis gates, optimization level, and transpiler seed. They are topology-only results without a hardware noise model. The routing-stage and final-transpilation measurements are described in `report.md`.

## 8. Results and Detailed Analysis

- `report.md` — mathematical formulation, classical and QAOA results, processor comparison, and limitations.
- `temporary_experiment_results.json` — exported preliminary experiment metrics.
- `results/` — saved result tables, figures, and other generated outputs.

## 9. Limitations

- The common official risk matrix has not yet been used in these results.
- Statevector probabilities are ideal simulation results, not hardware measurements.
- COBYLA termination does not prove global optimality.
- The QAOA measurement distribution does not always satisfy the two-asset constraint.
- Routing and transpilation measurements depend on the Qiskit version and settings.
- Clean-environment reproducibility must be validated separately.

## 10. Phase Scope

Phase 1 covers Processor A and Processor B. When the organizers provide the common official matrix for the applicable benchmark, the team should rerun the experiments with the prescribed input and report those results separately.

## 11. Reproducibility and Integrity

Results should be supported by actual notebook executions. Do not report unmeasured performance claims, claim that tests pass without running them, or present custom-matrix results as official benchmark results. Never commit API keys, passwords, tokens, or other secrets.
