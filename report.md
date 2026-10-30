# Quantum Processor Optimization and QAOA Performance Analysis for Knapsack Problem (PS-O2)

**Qiskit Fall Fest 2026 — Phase 2 Final Report**  
**Team:** QSpark  
**Problem Statement:** PS-O2 (4-Item Knapsack Problem)  

---

## Executive Summary
This report presents a comprehensive evaluation of quantum processor topologies, transpilation efficiency, and Quantum Approximate Optimization Algorithm (QAOA) performance for solving the 4-item Knapsack Problem (**PS-O2**). We benchmark three distinct hardware architectures:
1. **Processor A:** 5-qubit linear chain with nearest-neighbor connectivity.
2. **Processor B:** 9-qubit $3 \times 3$ square grid topology.
3. **Processor D (Frozen Design):** 4-qubit custom ring topology enhanced with a cross-diagonal edge $(0,2)$.

Our findings demonstrate that **Processor D** achieves superior hardware efficiency and solution fidelity under realistic depolarizing noise. Specifically, Processor D reduces QAOA circuit depth by **24.5%** and CNOT count by **21.1%** compared to Processor A. Under noisy simulation ($p_{CX}=0.005$), Processor D preserves an optimal state probability ('1001') of **18.75%** and a feasible state probability of **95.03%**, yielding the lowest mean cost ($-2.2342$).

---

## 1. Problem Formulation & Hardware Topologies

### 1.1 Problem Statement (PS-O2)
The 4-item Knapsack Problem instance is defined by item weights $w = [2, 3, 4, 5]$, item values $v = [3, 4, 5, 8]$, and knapsack capacity $C = 7$. The optimization objective is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) problem:

$$\mathcal{H}_{QUBO}(x) = -\sum_{i=0}^{3} v_i x_i + \lambda \max\left(0, \sum_{i=0}^{3} w_i x_i - C\right)^2$$

Where $x_i \in \{0,1\}$ indicates whether item $i$ is selected, and $\lambda = 10.0$ is the penalty parameter enforcing the weight capacity constraint.

The ground state (optimal solution) corresponds to selecting items $x_0$ and $x_3$ (weights $2+5=7$, value $3+8=11$), represented by bitstring `'1001'` (where bit positions represent $[x_3, x_2, x_1, x_0]$).

### 1.2 Quantum Processor Architectures
* **Processor A (5 Qubits, 4 Edges):** Linear chain topology $(0-1-2-3-4)$ with gate error rates $p_{CX} = 0.010$.
* **Processor B (9 Qubits, 12 Edges):** $3 \times 3$ grid topology with $p_{CX} = 0.008$.
* **Processor D (4 Qubits, 5 Edges - Frozen Design):** Custom ring topology $(0-1-2-3-0)$ with an additional cross-diagonal edge between qubit 0 and qubit 2, with reduced error rates $p_{CX} = 0.005$.

---

## 2. Bell-State Verification & Hardware Noise Calibration

To calibrate entitlement fidelity across all three processors, a Bell state $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ was prepared on connected qubit pairs $(0,1)$ and executed under both ideal and noisy simulation environments (4,000 shots).

### Table 1: Bell State Entanglement Verification (`results/tables/bell.csv`)
| Processor | Qubit Pair | $p_{CX}$ Error Rate | Ideal Fidelity | Noisy Fidelity | Fidelity Drop ($\Delta F$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | (0, 1) | 0.0100 | 1.0000 | 0.9940 | 0.0060 |
| **Processor B** | (0, 1) | 0.0080 | 1.0000 | 0.9962 | 0.0038 |
| **Processor D** | (0, 1) | 0.0050 | 1.0000 | 0.9975 | 0.0025 |

Processor D exhibits the highest Bell state fidelity ($99.75\%$) due to lower two-qubit gate error rates ($p_{CX} = 0.005$).

---

## 3. Transpilation & QAOA Performance Benchmark

The $p=1$ QAOA ansatz was optimized using the COBYLA algorithm on an ideal simulator, achieving optimal variational parameters $\gamma = 0.5000, \beta = 0.5000$. The ansatz circuit was transpiled targeting each processor topology using Qiskit optimization level 3.

### Table 2: Comprehensive Benchmark Matrix (`results/tables/results.csv`)
| Processor | Qubits | Edges | Circuit Depth | CX Count | Total Gates | Ideal Opt Prob | Ideal Feas Prob | Noisy Opt Prob | Noisy Feas Prob | Noisy Mean Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | 5 | 4 | 49 | 19 | 98 | 0.1983 | 0.9762 | 0.1737 | 0.9030 | +4.1825 |
| **Processor B** | 9 | 12 | 57 | 18 | 88 | 0.1903 | 0.9765 | 0.1747 | 0.9237 | +0.1013 |
| **Processor D** | 4 | 5 | **37** | **15** | **74** | **0.1915** | **0.9790** | **0.1875** | **0.9503** | **-2.2342** |

---

## 4. Analysis & Discussion

### 4.1 Topology & Transpilation Efficiency
* **SWAP Gate Overhead:** Processor A's linear topology requires substantial SWAP insertion to execute non-nearest-neighbor quadratic terms in the cost Hamiltonian, resulting in 19 CNOT gates and a depth of 49.
* **Processor D Co-design Advantage:** Processor D's cross-diagonal edge $(0,2)$ eliminates SWAP overhead for non-adjacent qubit interactions, directly reducing the CNOT count to 15 and circuit depth to 37.

### 4.2 Noise Resilience & Solution Quality
Under noisy simulation, Processor D preserves:
1. **Optimal State Probability ('1001'):** **18.75%** (compared to 17.37% on Processor A and 17.47% on Processor B).
2. **Total Feasible State Probability:** **95.03%** (compared to 90.30% on Processor A).
3. **Noisy Mean Cost:** **-2.2342** (the only architecture achieving a negative mean cost expectation value).

---

## 5. Conclusion
The custom 4-qubit architecture (**Processor D**) provides an optimal co-designed substrate for the 4-item Knapsack problem. By matching processor connectivity to the interaction topology of the QUBO Hamiltonian, Processor D minimizes transpilation overhead, mitigates gate error accumulation, and delivers superior optimization performance.
