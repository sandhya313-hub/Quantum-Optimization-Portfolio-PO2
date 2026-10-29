import csv
import json
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector
import qff_phase2 as qff

# 1. Load the official PS-O2 instance
with open("instances.json", "r", encoding="utf-8") as file:
    data = json.load(file)["PS-O2"]
mu = np.array(data["expected_returns"], dtype=float)
Sigma = np.array(data["risk_matrix"], dtype=float)
q = float(data["risk_aversion_q"])
k = int(data["k"])
lam = float(data["reference_penalty_lambda"])
n = len(mu)
seeds = [int(seed) for seed in data["initialization_seeds"]]
max_iterations = 100
shots = int(qff.SHOTS)

# 2. QUBO coefficients: C(x) = -F(x) + lambda * (sum(x)-k)^2
a = q * np.diag(Sigma) - mu + lam * (1 - 2 * k)
b = {
    (i, j): q * (Sigma[i, j] + Sigma[j, i]) + 2 * lam
    for i in range(n) for j in range(i + 1, n)
}
constant = lam * k**2

def portfolio_objective(x):
    x = np.asarray(x, dtype=float)
    return float(mu @ x - q * (x @ Sigma @ x))

def qubo_cost(x):
    x = np.asarray(x, dtype=float)
    return float(-portfolio_objective(x) + lam * (np.sum(x) - k) ** 2)

# 3. Cost Hamiltonian using x_i = (1-Z_i)/2
identity = "I" * n
terms = [(identity, constant)]
for i in range(n):
    zi = ["I"] * n
    zi[n - 1 - i] = "Z"
    terms.append((identity, a[i] / 2))
    terms.append(("".join(zi), -a[i] / 2))
for (i, j), coefficient in b.items():
    zi, zj, zij = ["I"] * n, ["I"] * n, ["I"] * n
    zi[n - 1 - i] = "Z"
    zj[n - 1 - j] = "Z"
    zij[n - 1 - i] = "Z"
    zij[n - 1 - j] = "Z"
    terms.extend([
        (identity, coefficient / 4),
        ("".join(zi), -coefficient / 4),
        ("".join(zj), -coefficient / 4),
        ("".join(zij), coefficient / 4),
    ])
cost_hamiltonian = SparsePauliOp.from_list(terms).simplify()

# 4. Build the p=1 QAOA ansatz
gamma = Parameter("gamma")
beta = Parameter("beta")
ansatz = QuantumCircuit(n)
ansatz.h(range(n))
for pauli, coefficient in zip(
    cost_hamiltonian.paulis.to_labels(), cost_hamiltonian.coeffs
):
    coefficient = float(np.real(coefficient))
    if pauli == identity:
        continue
    qubits = [
        n - 1 - position
        for position, symbol in enumerate(pauli) if symbol == "Z"
    ]
    target = qubits[-1]
    for control in qubits[:-1]:
        ansatz.cx(control, target)
    ansatz.rz(2 * coefficient * gamma, target)
    for control in reversed(qubits[:-1]):
        ansatz.cx(control, target)
for qubit in range(n):
    ansatz.rx(2 * beta, qubit)

# 5. Optimize using exact ideal Statevector expectation
def expected_cost(parameters):
    bound = ansatz.assign_parameters({
        gamma: float(parameters[0]), beta: float(parameters[1])
    })
    state = Statevector.from_instruction(bound)
    return float(np.real(state.expectation_value(cost_hamiltonian)))

optimization_results = []
print("\nPS-O2: QAOA p=1 optimization")
print("Optimizer: COBYLA | max iterations:", max_iterations)
print("Cost evaluation: exact ideal statevector")
for seed in seeds:
    rng = np.random.default_rng(seed)
    initial_angles = rng.uniform(0.0, np.pi, size=2)
    result = minimize(
        expected_cost, x0=initial_angles, method="COBYLA",
        bounds=[(0.0, np.pi), (0.0, np.pi)],
        options={"maxiter": max_iterations, "rhobeg": 0.5, "tol": 1e-4},
    )
    optimization_results.append({
        "seed": seed,
        "initial_gamma": float(initial_angles[0]),
        "initial_beta": float(initial_angles[1]),
        "gamma": float(result.x[0]),
        "beta": float(result.x[1]),
        "expected_cost": float(result.fun),
        "optimizer_success": bool(result.success),
        "iterations": int(result.nfev),
    })
    print(
        f"Seed {seed}: initial=({initial_angles[0]:.4f}, "
        f"{initial_angles[1]:.4f}) | optimized=({result.x[0]:.4f}, "
        f"{result.x[1]:.4f}) | expected cost={result.fun:.6f}"
    )
best = min(optimization_results, key=lambda item: item["expected_cost"])

# 6. Exact classical benchmark over all feasible portfolios
classical_results = []
for mask in range(1 << n):
    x = np.array([(mask >> i) & 1 for i in range(n)], dtype=int)
    if int(np.sum(x)) == k:
        classical_results.append({
            "assets": [i for i, bit in enumerate(x) if bit],
            "x": x.tolist(),
            "return": float(mu @ x),
            "risk": float(x @ Sigma @ x),
            "score": portfolio_objective(x),
            "cost": qubo_cost(x),
        })
classical_results.sort(key=lambda item: item["score"], reverse=True)
classical_best = classical_results[0]

print("\nBEST QAOA INITIALIZATION")
print("Seed:", best["seed"])
print(f'Optimized gamma: {best["gamma"]:.6f}')
print(f'Optimized beta:  {best["beta"]:.6f}')
print(f'Expected penalized cost: {best["expected_cost"]:.6f}')
print("\nEXACT CLASSICAL OPTIMUM")
print("Selected assets:", classical_best["assets"])
print(f'Expected return: {classical_best["return"]:.4f}')
print(f'Risk: {classical_best["risk"]:.4f}')
print(f'Objective F*: {classical_best["score"]:.4f}')
print("\nAll feasible classical portfolios:")
for item in classical_results:
    print(
        f'Assets {item["assets"]} | Return={item["return"]:.2f} | '
        f'Risk={item["risk"]:.2f} | F={item["score"]:.2f}'
    )
with open("qaoa_optimization_results.json", "w", encoding="utf-8") as file:
    json.dump({
        "problem": "PS-O2", "optimizer": "COBYLA",
        "max_iterations": max_iterations,
        "cost_evaluation": "exact ideal statevector",
        "lambda": lam, "initialization_results": optimization_results,
        "best_initialization": best, "classical_optimum": classical_best,
        "classical_feasible_portfolios": classical_results,
    }, file, indent=2)
print("\nSaved qaoa_optimization_results.json")

# 7. Load and validate Processors A, B, and custom Processor D
processor_d = qff.load_processor("processors/processor_D.json")
processors = (qff.PROCESSOR_A, qff.PROCESSOR_B, processor_d)
qff.validate_processor_d(processor_d, required_qubits=n)

# 8. Benchmark all processors with identical optimized angles
def evaluate_processor(processor, gamma_value, beta_value, noisy):
    circuit = ansatz.assign_parameters({
        gamma: float(gamma_value), beta: float(beta_value)
    }).copy()
    circuit.measure_all()
    transpiled = qff.transpile_for(circuit, processor)
    backend = qff.simulator(noisy=noisy, processor=processor)
    counts = backend.run(transpiled, shots=shots).result().get_counts()

    total_shots = sum(counts.values())
    valid_shots = 0
    optimal_shots = 0
    objective_sum = 0.0
    best_measured_score = None

    for bitstring, count in counts.items():
        x = np.asarray(qff.counts_to_x(bitstring), dtype=int)[:n]
        if len(x) != n:
            raise ValueError(
                f"Expected {n} measured bits, got {len(x)}: {bitstring}"
            )
        score = portfolio_objective(x)
        valid = int(np.sum(x)) == k
        optimal = valid and np.array_equal(
            x, np.asarray(classical_best["x"], dtype=int)
        )
        if valid:
            valid_shots += count
            objective_sum += score * count
            if best_measured_score is None or score > best_measured_score:
                best_measured_score = score
        if optimal:
            optimal_shots += count

    # Metrics are calculated from the transpiled circuit actually submitted.
    metrics = qff.circuit_metrics(transpiled, processor)
    return {
        "problem": "PS-O2",
        "processor": processor["name"],
        "noise": "noisy" if noisy else "ideal",
        "shots": total_shots,
        "valid_solution_frequency": valid_shots / total_shots,
        "optimal_portfolio_probability": optimal_shots / total_shots,
        "mean_objective_valid": (
            objective_sum / valid_shots if valid_shots else None
        ),
        "best_measured_feasible_objective": best_measured_score,
        "gamma": float(gamma_value),
        "beta": float(beta_value),
        "logical_qubits": n,
        "physical_qubits": processor["num_qubits"],
        "transpiled_depth": metrics.get("depth"),
        "transpiled_cx": metrics.get("cx"),
        "cx_overhead": metrics.get("cx_overhead"),
    }

benchmark_results = []
print("\nPROCESSOR BENCHMARKS")
print("Shots per processor/noise setting:", shots)
print("Using the same optimized angles for A, B, and D.")
print("-" * 72)
for processor in processors:
    for noisy in (False, True):
        result = evaluate_processor(
            processor, best["gamma"], best["beta"], noisy
        )
        benchmark_results.append(result)
        print(
            f'{result["processor"]} | {result["noise"]} | '
            f'valid={result["valid_solution_frequency"]:.4f} | '
            f'P_opt={result["optimal_portfolio_probability"]:.4f} | '
            f'depth={result["transpiled_depth"]} | '
            f'CX={result["transpiled_cx"]}'
        )

# One consistent CSV containing Processor A, B, and D results
with open("processor_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=benchmark_results[0].keys())
    writer.writeheader()
    writer.writerows(benchmark_results)
print("\nSaved all Processor A/B/D results to processor_results.csv")
print("QAOA optimization and processor benchmarking completed.")
