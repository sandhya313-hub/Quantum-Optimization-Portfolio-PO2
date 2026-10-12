# Qiskit Fall Fest 2026 — PS-O2: Constrained Portfolio Optimization

**Report status:** Preliminary Phase 1 experimental results  
**Risk matrix:** Custom experimental matrix; not the official benchmark matrix  
**QAOA depth:** p = 1

## 1. Problem Statement

This project implements PS-O2, Constrained Portfolio Optimization, using a Quadratic Unconstrained Binary Optimization (QUBO) formulation and the Quantum Approximate Optimization Algorithm (QAOA).

The objective defined by the organizers is:

```text
Maximize:
f(x) = r.T @ x
       - 2 * x.T @ Sigma @ x
       - 20 * (sum(x) - 2)^2
```

where:

- `r = [5, 3, 4, 2]` is the vector of asset returns.
- `Sigma` is the 4 × 4 risk matrix.
- Risk aversion parameter: `lambda = 2`.
- Budget constraint penalty: `A = 20`.
- Target number of selected assets: `k = 2`.
- Each decision variable `x[i]` is binary: 0 means the asset is not selected; 1 means it is selected.

The penalty term encourages solutions containing exactly two assets.

## 2. Risk Matrix and Experimental Scope

The organizers clarified that the common official risk matrix would be provided for the later benchmark after Phase 1 shortlisting. Custom matrices are permitted for additional experiments, provided their results are recorded and explained separately.

This experiment uses the following custom matrix:

```text
SIGMA_TEST =
[[0.40, 0.05, 0.02, 0.01],
 [0.05, 0.30, 0.04, 0.02],
 [0.02, 0.04, 0.35, 0.03],
 [0.01, 0.02, 0.03, 0.25]]
```

**This matrix is experimental test data, not the official common benchmark matrix.** All numerical portfolio and QAOA results in this report refer to this matrix.

Phase 1 focuses on Processor A and Processor B. Processor C and custom Processor D are outside the scope of this Phase 1 implementation.

## 3. Methodology and Implementation

The implementation follows these steps:

1. Define the organizer-provided portfolio parameters.
2. Validate the custom risk matrix.
3. Construct the QUBO representation of the negative maximization objective.
4. Check the QUBO conversion against all possible binary portfolios.
5. Find a classical reference solution through exhaustive enumeration.
6. Construct a QAOA circuit with `p = 1`.
7. Optimize the QAOA parameters using SciPy COBYLA.
8. Calculate the resulting portfolio measurement probabilities using an ideal statevector simulation.
9. Transpile the same logical circuit for Processor A and Processor B.
10. Record and compare circuit metrics and experimental limitations.

### 3.1 QUBO Formulation

The maximization objective is converted into a minimization problem:

```text
C(x) = -f(x)
```

The implementation stores the QUBO pair coefficients in the upper triangle of the matrix, counting each pair interaction once. The constant offset from the budget penalty is retained when evaluating the complete QUBO cost.

The QUBO representation was checked against all 16 possible binary portfolios.

**Observed maximum absolute equivalence error:** approximately `1.42e-14`.

This verifies numerical agreement between the implemented QUBO cost and the negative of the original objective for the custom matrix.

### 3.2 Classical Baseline

All `2^4 = 16` binary portfolios were enumerated. The implementation records the return, risk value, penalized objective, selected asset indices, and feasibility of each portfolio.

The classical result provides a reference against which the QAOA measurement distribution can be evaluated.

### 3.3 QAOA Optimization

A depth-one QAOA circuit was constructed using the QUBO cost Hamiltonian and a standard X-mixer layer. The expected QUBO cost was evaluated using an ideal statevector simulator.

Five COBYLA starting points were tested. The best candidate found was:

| Parameter | Observed value |
|---|---:|
| Gamma | 1.1752997926 |
| Beta | 0.7884162398 |
| Expected QUBO cost | 1.7013351916 |
| Evaluations in the best run | 34 |
| SciPy optimizer success flag | True |

The best run stopped because the trust-region radius reached its lower bound. This indicates successful termination according to the optimizer's stopping criterion; it does not prove that the global minimum was found.

## 4. Classical and QAOA Results

### 4.1 Best Classical Feasible Portfolio

The best feasible portfolio for the custom matrix is:

```text
Binary vector: [1, 0, 1, 0]
Selected asset indices: [0, 2]
Number of selected assets: 2
Total return: 9.00
Risk value x.T @ Sigma @ x: 0.79
Penalized objective: 7.42
Constraint satisfied: Yes
```

The portfolio selects assets 0 and 2 and satisfies the requirement to select exactly two assets.

### 4.2 QAOA Measurement Probabilities

The following results were calculated using the best candidate parameters and the custom matrix.

| Metric | Observed value |
|---|---:|
| Probability of measuring the classical-optimal portfolio | 29.2331% |
| Probability of selecting exactly two assets | 63.6831% |
| Probability of violating the asset-count constraint | 36.3169% |

The most probable measured portfolio was the classical-optimal portfolio, with binary vector `[1, 0, 1, 0]` and objective value `7.42`.

The probability of measuring the optimal portfolio is different from the probability of satisfying the asset-count constraint. A measurement may satisfy the two-asset constraint without being optimal.

These probabilities come from an ideal statevector simulation. They are not hardware measurement results.

## 5. Processor A and Processor B Comparison

The same logical QAOA circuit was transpiled for both processor connectivity maps.

The benchmark configuration used:

- Basis gates: `rz`, `sx`, `x`, `cx`.
- Optimization level: `0`.
- Transpiler seed: `42`.
- The same logical input circuit for both processors.
- No hardware noise model or device error rates.

An unconstrained reference circuit was transpiled with the same basis and optimization settings, but without a processor coupling-map constraint.

### 5.1 Measured Circuit Metrics

| Metric | Unconstrained reference | Processor A | Processor B |
|---|---:|---:|---:|
| Physical qubits | 4 | 5 | 9 |
| Circuit depth | 25 | 91 | 85 |
| CX gates | 12 | 21 | 24 |
| Additional CX gates vs. reference | 0 | 9 | 12 |
| CX increase vs. reference | 0% | 75% | 100% |
| Explicit SWAP instructions in output | 0 | 0 | 0 |

These values are measurements from the current Qiskit transpilation configuration and should be interpreted in that context.

### 5.2 Architecture-Related Observations

**Processor A**

- Uses 5 physical qubits in the transpiled output.
- Has a measured circuit depth of 91.
- Contains 21 CX gates, nine more than the unconstrained reference.

**Processor B**

- Uses 9 physical qubits in the transpiled output.
- Has a measured circuit depth of 85.
- Contains 24 CX gates, twelve more than the unconstrained reference.

Processor B's measured circuit depth is lower than Processor A's in this experiment, while Processor A uses fewer CX gates.

The measured depth difference is six layers, with Processor B's depth approximately 6.6% lower relative to Processor A. Processor A uses three fewer CX gates than Processor B.

These observations demonstrate differences in the transpiled circuits under the chosen benchmark settings. They do not establish that one processor is universally better, because the results depend on the transpiler configuration and do not include hardware noise, device error rates, or execution times.

### 5.3 Routing and SWAP Interpretation

The output circuits contain zero explicit SWAP instructions. However, this does not independently prove that routing overhead is zero.

The additional CX counts are topology-associated gate overhead relative to the unconstrained reference. They must not be treated as an isolated SWAP count. A separate, validated routing-stage analysis is required to quantify routing overhead and any SWAP operations that may be decomposed into other gates.

Therefore, the present results do not claim a definitive isolated SWAP overhead for either processor.

## 6. Reproducibility

The experiment was developed and executed in Google Colab using Python, NumPy, Qiskit, Qiskit Aer, and SciPy.

The recorded environment during the experiment included:

| Component | Recorded version |
|---|---|
| Python | 3.13.16 |
| NumPy | 2.1.3 |
| Qiskit | 2.5.2 |
| Qiskit Aer | 0.17.2 |

The notebook records the experimental setup, QUBO validation, classical baseline, QAOA optimization, probability calculations, processor transpilation, and exported results.

These version records describe the observed runtime. They do not, by themselves, establish that the notebook has been tested successfully from a completely clean environment with a pinned dependency file.

## 7. Limitations

The following limitations apply to the current results:

1. The risk matrix is custom experimental data, not the official common benchmark matrix.
2. The QAOA probabilities are from an ideal statevector simulation rather than a noisy quantum device.
3. COBYLA successfully terminated for the best run, but global optimality has not been established.
4. The constraint satisfaction probability is approximately 63.68%, so the simulated QAOA distribution still assigns probability to invalid portfolios.
5. The measured Processor A/B gate counts and depths depend on the specified Qiskit transpiler settings.
6. Additional CX gates are not an isolated measurement of routing or SWAP overhead.
7. The explicit SWAP count of zero must not be interpreted as proof of zero routing overhead.
8. A clean-environment execution and dependency reproducibility check must be confirmed before claiming complete end-to-end reproducibility.

## 8. Next Steps

Before treating the project as a final submission, the team should:

- Validate the routing-stage analysis and report routing/SWAP metrics only when supported by measurements.
- Ensure the Processor A/B benchmark uses identical logical inputs and documented transpiler settings.
- Verify the processor configuration files against the official connectivity definitions.
- Confirm that the requirements file supports a reproducible notebook run.
- Verify that the notebook executes from a clean environment.
- Ensure the README explains installation, execution, methodology, results, and limitations.
- Keep custom-matrix results separate from any future official benchmark.
- When the organizers supply the official common risk matrix, rerun the prescribed benchmark with that matrix for the applicable phase.

## 9. Conclusion

This preliminary implementation demonstrates the formulation of PS-O2 as a QUBO minimization problem, numerical verification of that formulation over all 16 portfolios, exhaustive classical optimization, a depth-one QAOA simulation, and a comparative transpilation study of Processor A and Processor B.

For the custom risk matrix, the classical reference selects assets 0 and 2 with an objective value of 7.42. The best QAOA candidate assigns approximately 29.23% probability to that portfolio and approximately 63.68% probability to portfolios satisfying the two-asset constraint.

The topology comparison shows that Processor B produced a shallower transpiled circuit, while Processor A used fewer CX gates under the tested settings. Further routing-stage validation and reproducibility checks are required before making stronger conclusions.

**All numerical results in this report are preliminary custom-matrix experimental results. They must not be presented as results from the official common-matrix benchmark.**                                                                                                                                     ## 10. Routing-Stage Analysis

The routing stage was inspected separately using Qiskit's preset pass manager at optimization level 0, with the same coupling maps, target basis gates, and transpiler seed used in the processor benchmark.

| Routing metric | Processor A | Processor B |
|---|---:|---:|
| CX gates before routing | 12 | 12 |
| CX gates after routing | 12 | 12 |
| SWAP instructions after routing | 3 | 4 |
| Routing-stage depth | 29 | 25 |
| Estimated additional CX gates from SWAP decomposition | 9 | 12 |
| Final transpiled CX gates | 21 | 24 |

Each SWAP can be decomposed into three CX gates. Based on the observed routing-stage SWAP counts, the corresponding decomposition adds an estimated nine CX gates for Processor A and twelve for Processor B. These estimates match the differences between the 12-CX logical circuit and the final transpiled circuits in the current experiment.

Processor A required three routing-stage SWAP instructions, while Processor B required four. Processor B nevertheless had a lower measured routing-stage depth (25 versus 29) and a lower final circuit depth (85 versus 91).

These results illustrate why the routing-stage output and final transpiled output should both be recorded: SWAP instructions can be decomposed into the target gate basis, so the final circuit may report zero explicit SWAP instructions even when the routing stage inserted them.

The measurements are specific to the tested logical circuit and transpiler configuration. They do not imply that either processor is universally superior.
