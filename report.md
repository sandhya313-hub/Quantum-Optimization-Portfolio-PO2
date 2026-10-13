# Qiskit Fall Fest 2026 — PS-O2: Constrained Portfolio Optimization

**Phase:** Phase 1 — Processor A and Processor B comparison  
**QAOA depth:** `p = 1`  
**Benchmark status:** Notebook executed successfully; reported values are from the current Google Colab run  
**Important parameter note:** The problem guide provides the official returns, covariance matrix, and target asset count, but does not prescribe numerical values for risk-aversion parameter `q` or penalty coefficient `A`. This experiment uses `q = 2` and `A = 20` as documented experimental choices.

## 1. Problem statement

This project implements PS-O2, portfolio selection with a return objective and risk penalty, using a Quadratic Unconstrained Binary Optimization (QUBO) formulation and the Quantum Approximate Optimization Algorithm (QAOA).

The portfolio has four binary decision variables. `x[i] = 1` means asset `i` is selected and `x[i] = 0` means it is not selected. The target is to select exactly `k = 2` assets.

The optimization objective used in this experiment is

```text
Minimize C(x) = x.T @ Sigma @ x - q * (mu.T @ x)
                 + A * (sum(x) - k)^2
```

where `mu` is the return vector, `Sigma` is the covariance/risk matrix, `q = 2` is the experimental risk-aversion parameter, and `A = 20` is the experimental penalty coefficient. The penalty discourages portfolios that do not contain exactly two assets.

## 2. Official problem inputs

The notebook uses the inputs listed in the Phase 1 problem guide:

```text
mu = [0.12, 0.18, 0.10, 0.22]
k = 2

Sigma =
[[0.04, 0.01, 0.02, 0.01],
 [0.01, 0.09, 0.01, 0.03],
 [0.02, 0.01, 0.05, 0.02],
 [0.01, 0.03, 0.02, 0.08]]
```

The covariance matrix is symmetric. The notebook checks the input dimensions and evaluates all `2^4 = 16` binary strings. The earlier custom matrix and its associated results are not used in the reported benchmark below.

## 3. QUBO formulation and verification

The implementation expands the objective and the squared cardinality penalty into a QUBO. Pair coefficients are stored in the upper triangle and each pair interaction is counted once. The constant offset from the penalty is retained when calculating the full QUBO energy.

The notebook checks the QUBO energy against the direct objective for all 16 bitstrings. The maximum observed absolute discrepancy was approximately `2.49e-14`, which is numerical floating-point error and confirms that the two calculations agree for the tested inputs and parameter choices.

## 4. Exact classical baseline

All 16 portfolios are exhaustively enumerated. The best feasible portfolio for the selected experimental parameters is:

| Quantity | Value |
|---|---:|
| Bitstring (asset indices 0–3) | `[0, 1, 0, 1]` |
| Selected asset indices | `[1, 3]` |
| Number of selected assets | 2 |
| Total return, `mu.T @ x` | 0.40 |
| Risk, `x.T @ Sigma @ x` | 0.23 |
| Objective, `risk - q * return` | -0.57 |
| Cardinality constraint satisfied | Yes |

The QUBO penalty is zero for this feasible portfolio, so its QUBO energy (including the constant offset) is approximately `-0.57`. This is the exact classical reference for the stated inputs and experimental parameter values. It is not a claim about an unspecified official value of `q` or `A`.

## 5. QAOA method and ideal simulation

A depth-one QAOA (`p = 1`) circuit was constructed from the QUBO cost Hamiltonian and an X-mixer layer. Its parameters were optimized using SciPy's Differential Evolution procedure over the bounds used in the notebook. The selected parameter values were approximately:

| Parameter | Value |
|---|---:|
| Gamma | 0.13238249 |
| Beta | 1.28843026 |
| Expected QUBO energy | 5.60402820 |

The expected energy was independently recalculated from the statevector probability distribution and agreed with the objective function to within approximately `5.33e-15`.

The ideal statevector output distribution gave:

| Metric | Result |
|---|---:|
| Probability of the exact classical-optimal portfolio | 12.4503% |
| Probability of any feasible two-asset portfolio | 73.8718% |
| Probability of an infeasible portfolio | 26.1282% |

The circuit can produce the classical-optimal bitstring, but its probability is modest. The ideal simulation therefore does not show that this `p = 1` QAOA setup matches the quality of exhaustive classical optimization. Optimizer termination also does not prove global optimality of the QAOA parameters.

## 6. Processor A and Processor B benchmark

The same logical QAOA circuit and selected parameters were benchmarked against the two Phase 1 reference connectivity maps. The notebook used the target basis gates `rz`, `sx`, `x`, and `cx`, optimization level `1`, transpiler seed `42`, and `4096` measurement shots for each processor. The reported noisy results use the synthetic noise model configured in the notebook: one-qubit depolarizing error rate `0.001`, CX depolarizing error rate `0.005`, and readout error rate `0.01`.

### 6.1 Final comparison

| Metric | Processor A | Processor B |
|---|---:|---:|
| Physical qubits in processor topology | 5 | 9 |
| Transpiled circuit depth | 46 | 37 |
| Reference CX count | 12 | 12 |
| Transpiled CX count | 18 | 15 |
| Additional CX gates vs. reference | 6 | 3 |
| Explicit SWAP instructions after basis translation | 0 | 0 |
| SWAP-equivalent estimate (`additional CX / 3`) | 2.0 | 1.0 |
| RZ gates | 30 | 30 |
| SX gates | 12 | 12 |
| X gates | 0 | 0 |
| Shots | 4096 | 4096 |
| Optimal portfolio hits | 471 | 486 |
| Optimal portfolio hit rate | 11.4990% | 11.8652% |
| Feasible samples | 2833 | 2861 |
| Feasible-output rate | 69.1650% | 69.8486% |
| Infeasible-output rate | 30.8350% | 30.1514% |
| Empirical mean objective | 6.974014 | 6.822458 |
| Best sampled feasible bitstring | `[0, 1, 0, 1]` | `[0, 1, 0, 1]` |
| Best sampled feasible objective | -0.57 | -0.57 |

### 6.2 Interpretation

In this run, Processor B had a lower transpiled depth (37 versus 46) and fewer transpiled CX gates (15 versus 18). It also had a slightly higher observed optimal-portfolio hit rate (11.8652% versus 11.4990%) and feasible-output rate (69.8486% versus 69.1650%). Both processors sampled the classical-optimal portfolio and recorded the same best feasible objective of `-0.57`.

The observed hit-rate difference is small: 486 optimal hits for Processor B versus 471 for Processor A out of 4096 shots. These are finite-shot results from one benchmark run; they do not establish statistical significance or prove that Processor B is universally superior. The conclusion is limited to the tested circuits, topology definitions, transpiler configuration, noise model, and random seed.

The empirical mean objective is positive even though the best feasible objective is `-0.57`, because the mean includes samples that violate the two-asset constraint and therefore incur the penalty. The feasible-output rate and optimal-hit rate measure different things: a feasible sample may satisfy the asset-count constraint without being the optimal portfolio.

### 6.3 Routing and SWAP interpretation

The final basis-translated circuits contain zero explicit SWAP instructions. This does not mean routing introduced no overhead: SWAP operations may be decomposed into CX gates during basis translation. The notebook therefore reports additional CX gates relative to the 12-CX logical reference and a **SWAP-equivalent estimate** of additional CX divided by three.

The estimates of `2.0` for Processor A and `1.0` for Processor B are not exact observed routing-stage SWAP counts. They are a proxy for overhead and should be labelled as such. The final report does not claim a separately verified count of routing-stage SWAP instructions from these final metrics alone.

## 7. Reproducibility and generated artifacts

The experiment was developed and run in Google Colab. The executed notebook reported `ALL NOTEBOOK CHECKS PASSED` and generated the following artifacts:

```text
results/figures/processor_ab_circuit_metrics.png
results/figures/processor_ab_noisy_quality.png
results/figures/processor_topologies.png
results/tables/benchmark_metadata.json
results/tables/ideal_qaoa_distribution.csv
results/tables/noisy_processor_comparison.csv
results/tables/noisy_shot_distribution.csv
results/tables/processor_ab_final_comparison.csv
results/tables/transpilation_metrics.csv
```

The repository should contain the executed `main.ipynb` and these generated tables and figures. Results under Colab's `/content/` directory are temporary until downloaded and committed to the repository.

## 8. Limitations

1. The guide does not prescribe numeric values for `q` and `A`; this experiment uses `q = 2` and `A = 20` as documented choices.
2. QAOA uses `p = 1`; this is a shallow variational circuit and does not match the exact classical optimum with high probability in the observed distribution.
3. The ideal-statevector expected energy is approximately `5.604`, well above the exact feasible optimum of `-0.57`; the QAOA result should not be presented as outperforming exhaustive classical optimization.
4. Noisy hit rates and feasibility rates are empirical estimates from 4096 shots per processor and one configured benchmark run.
5. Processor A/B results depend on the stated topology maps, target basis, optimization level, transpiler seed, and synthetic noise assumptions. They do not represent measurements on real hardware.
6. The SWAP-equivalent metric is an estimate based on additional CX gates, not an exact routing-stage SWAP count.
7. The experiment's results are only reproducible to the extent that the notebook, dependency versions, processor configuration files, and generated result artifacts are preserved together.

## 9. Conclusion

This Phase 1 implementation formulates PS-O2 as a QUBO, verifies the formulation against all 16 binary strings, computes an exact classical baseline, runs a depth-one QAOA simulation, and compares Processor A and Processor B under a documented synthetic noise model and 4096-shot evaluation.

For the chosen experimental parameters (`q = 2`, `A = 20`), exhaustive enumeration finds the best feasible portfolio `[0, 1, 0, 1]`, selecting assets 1 and 3, with return `0.40`, risk `0.23`, and objective `-0.57`. In the noisy benchmark, Processor A achieved an 11.4990% optimal hit rate and 69.1650% feasible-output rate; Processor B achieved an 11.8652% optimal hit rate and 69.8486% feasible-output rate. Processor B also produced a shallower circuit and fewer CX gates in this run.

These results support a limited, reproducible comparison under the specified simulation settings. They do not establish real-hardware performance or universal architectural superiority. The experimental parameter choices and routing proxy are explicitly identified so that the findings are not overstated.
