# Qiskit Fall Fest 2026 - Phase 2: Constrained Portfolio Optimization (PS-O2)

Welcome to Phase 2 of the **Qiskit Fall Fest 2026** Optimization Track!

## Project Structure

```
qiskit-fallfest-ps-o2/
├── Phase One/                 # Preserved Phase 1 source code, reports, and configurations
│   ├── assets/
│   ├── data/
│   ├── processors/
│   ├── results/
│   ├── src/
│   ├── main.ipynb
│   ├── README.md
│   ├── report.md
│   └── requirements.txt
├── processors/                # Phase 2 Processor configurations
│   └── processor_D_template.json
├── example_usage.py           # Example script demonstrating Phase 2 helper usage
├── instances.json             # Phase 2 problem instances and specifications
├── qff_phase2.py              # Phase 2 core helper functions and validation framework
├── requirements.txt           # Phase 2 dependencies
└── README.md                  # Phase 2 repository overview
```

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Helper Framework**:
   ```bash
   python example_usage.py
   ```

## Development & Phase 2 Objectives

All Phase 2 development, optimization algorithm code, and results should remain in the repository root or dedicated root-level subfolders (e.g., `src/`, `results/`).
