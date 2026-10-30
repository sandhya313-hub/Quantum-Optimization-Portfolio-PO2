# Qiskit Fall Fest 2026 - Phase 2 (PS-O2 Optimization Track)

## Team Information
* **Team Name:** QSpark
* **Problem Statement:** PS-O2 (4-Item Knapsack Problem with Connectivity and Noise Constraints)

---

## Overview
This repository contains the complete reproducible implementation for **PS-O2** in Phase 2 of the Qiskit Fall Fest 2026 Optimization Track. The goal is to formulate, transpile, simulate, and analyze QAOA circuits for a 4-item Knapsack Problem across three distinct quantum processor architectures:
* **Processor A:** 5-qubit linear topology
* **Processor B:** 9-qubit 2D grid topology
* **Processor D:** 4-qubit custom ring + cross-diagonal topology (Frozen Design)

---

## Project Structure
```text
project/
├── README.md                 # Team info, PS code, execution instructions & key results
├── main.ipynb                # End-to-end execution notebook (runs within 5 mins on CPU)
├── generate_results.py       # Python script generating all tables and figures
├── requirements.txt          # Python dependencies
├── qff_phase2.py             # Starter utilities module
├── data/
│   └── instance.json         # PS-O2 instance data
├── processors/
│   ├── processor_A.json      # 5-qubit linear architecture
│   ├── processor_B.json      # 9-qubit grid architecture
│   └── processor_D.json      # 4-qubit ring + cross-diagonal architecture
├── src/
│   └── qubo.py               # QUBO formulation & evaluation
└── results/
    ├── tables/
    │   ├── bell.csv          # Bell-state verification metrics across Processors A, B, D
    │   └── results.csv       # QAOA performance and transpilation metrics
    └── figures/
        ├── processor_topologies.png
        ├── transpilation_comparison.png
        ├── noisy_quality_comparison.png
        ├── noisy_shot_distribution.png
        └── penalty_sweep.png
```

---

## Key Benchmark Results

### Bell-State Verification (`results/tables/bell.csv`)
| Processor | Qubit Pair | Gate Error ($p_{CX}$) | Ideal Fidelity | Noisy Fidelity | Fidelity Drop |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | (0,1) | 0.010 | 1.0000 | 0.9940 | 0.0060 |
| **Processor B** | (0,1) | 0.008 | 1.0000 | 0.9962 | 0.0038 |
| **Processor D** | (0,1) | 0.005 | 1.0000 | 0.9975 | 0.0025 |

### Comprehensive Transpilation & QAOA Performance (`results/tables/results.csv`)
| Processor | Qubits | Edges | Circuit Depth | CX Count | Total Gates | Ideal Opt Prob | Ideal Feas Prob | Noisy Opt Prob | Noisy Feas Prob | Noisy Mean Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | 5 | 4 | 49 | 19 | 98 | 0.1983 | 0.9762 | 0.1737 | 0.9030 | 4.1825 |
| **Processor B** | 9 | 12 | 57 | 18 | 88 | 0.1903 | 0.9765 | 0.1747 | 0.9237 | 0.1013 |
| **Processor D** | 4 | 5 | **37** | **15** | **74** | **0.1915** | **0.9790** | **0.1875** | **0.9503** | **-2.2342** |

---

## How to Run

### 1. Installation
Install the exact required packages:
```bash
pip install -r requirements.txt
```

### 2. Execution Options
* **Option A (Jupyter Notebook):** Open and run `main.ipynb` from top to bottom. It will execute the complete pipeline in under 2 minutes.
* **Option B (Python Script):** Run the automated results generator:
```bash
python generate_results.py
```

---

## AI Tools Acknowledgment
AI tools (Morph Agent / LLM) were used to assist in automated script generation, workspace restructuring, transpilation benchmarking, and report compilation. All physics calculations, QUBO models, and numerical outputs were rigorously verified against Qiskit Aer simulations.
