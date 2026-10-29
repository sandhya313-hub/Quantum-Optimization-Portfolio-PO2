"""
run_penalty_sweep.py
QFF Phase 2 PS-O2 — Processor D penalty sweep.

For each required lambda:
  * Rebuild the QUBO and its cost Hamiltonian.
  * Re-optimize p=1 QAOA with the five official initialization seeds.
  * Use the best ideal-statevector optimization result.
  * Evaluate Processor D under ideal and noisy simulation with official shots.
  * Save a CSV to results/tables/penalty_sweep.csv.

This script imports the official helper module and does not modify it.
"""

import csv
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector

import qff_phase2 as qff


ROOT = Path(__file__).resolve().parent
INSTANCE_PATH = ROOT / "instances.json"
PROCESSOR_D_PATH = ROOT / "processors" / "processor_D.json"
OUTPUT_PATH = ROOT / "results" / "tables" / "penalty_sweep.csv"

LAMBDA_VALUES = [0, 0.5, 1, 2, 5, 10]
MAX_ITERATIONS = 100


def load_instance():
    with INSTANCE_PATH.open("r", encoding="utf-8") as file:
        instance = json.load(file)["PS-O2"]

    mu = np.asarray(instance["expected_returns"], dtype=float)
    sigma = np.asarray(instance["risk_matrix"], dtype=float)

    return {
        "mu": mu,
        "sigma": sigma,
        "q": float(instance["risk_aversion_q"]),
        "k": int(instance["k"]),
        "seeds": [int(seed) for seed in instance["initialization_seeds"]],
        "shots": int(qff.SHOTS),
    }


def objective(x, mu, sigma, q):
    """Original return-risk objective F(x), to be maximized."""
    x = np.asarray(x, dtype=float)
    return float(mu @ x - q * (x @ sigma @ x))


def build_hamiltonian(mu, sigma, q, k, lam):
    """Build the QUBO cost Hamiltonian for the given penalty lambda."""
    n = len(mu)
    linear = q * np.diag(sigma) - mu + lam * (1 - 2 * k)
    pair = {
        (i, j): q * (sigma[i, j] + sigma[j, i]) + 2 * lam
        for i in range(n)
        for j in range(i + 1, n)
    }
    constant = lam * k**2
    identity = "I" * n
    terms = [(identity, constant)]

    for i in range(n):
        zi = ["I"] * n
        zi[n - 1 - i] = "Z"
        terms.append((identity, linear[i] / 2))
        terms.append(("".join(zi), -linear[i] / 2))

    for (i, j), coefficient in pair.items():
        zi = ["I"] * n
        zj = ["I"] * n
        zij = ["I"] * n
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

    return SparsePauliOp.from_list(terms).simplify()


def build_ansatz(n, hamiltonian):
    """Build p=1 QAOA ansatz from a diagonal Z Hamiltonian."""
    gamma = Parameter("gamma")
    beta = Parameter("beta")
    identity = "I" * n

    circuit = QuantumCircuit(n)
    circuit.h(range(n))

    for pauli, coefficient in zip(
        hamiltonian.paulis.to_labels(), hamiltonian.coeffs
    ):
        coefficient = float(np.real(coefficient))
        if pauli == identity:
            continue

        qubits = [
            n - 1 - position
            for position, symbol in enumerate(pauli)
            if symbol == "Z"
        ]
        target = qubits[-1]

        for control in qubits[:-1]:
            circuit.cx(control, target)

        circuit.rz(2 * coefficient * gamma, target)

        for control in reversed(qubits[:-1]):
            circuit.cx(control, target)

    for qubit in range(n):
        circuit.rx(2 * beta, qubit)

    return circuit, gamma, beta


def exact_classical_optimum(mu, sigma, q, k):
    """Enumerate all feasible bitstrings to get the true feasible optimum."""
    n = len(mu)
    feasible = []

    for mask in range(1 << n):
        x = np.asarray([(mask >> i) & 1 for i in range(n)], dtype=int)
        if int(np.sum(x)) == k:
            feasible.append({
                "x": x.tolist(),
                "assets": [i for i, bit in enumerate(x) if bit],
                "objective": objective(x, mu, sigma, q),
            })

    if not feasible:
        raise RuntimeError("No feasible portfolios found.")

    return max(feasible, key=lambda item: item["objective"])


def optimize_for_lambda(lam, instance):
    """Run all required initializations and return the best angles."""
    mu = instance["mu"]
    sigma = instance["sigma"]
    q = instance["q"]
    k = instance["k"]
    n = len(mu)

    hamiltonian = build_hamiltonian(mu, sigma, q, k, lam)
    ansatz, gamma, beta = build_ansatz(n, hamiltonian)

    def expected_cost(angles):
        bound = ansatz.assign_parameters({
            gamma: float(angles[0]),
            beta: float(angles[1]),
        })
        state = Statevector.from_instruction(bound)
        return float(np.real(state.expectation_value(hamiltonian)))

    candidates = []

    for seed in instance["seeds"]:
        rng = np.random.default_rng(seed)
        initial_angles = rng.uniform(0.0, np.pi, size=2)

        result = minimize(
            expected_cost,
            x0=initial_angles,
            method="COBYLA",
            bounds=[(0.0, np.pi), (0.0, np.pi)],
            options={
                "maxiter": MAX_ITERATIONS,
                "rhobeg": 0.5,
                "tol": 1e-4,
            },
        )

        candidates.append({
            "seed": seed,
            "gamma": float(result.x[0]),
            "beta": float(result.x[1]),
            "expected_cost": float(result.fun),
            "optimizer_success": bool(result.success),
            "iterations": int(result.nfev),
        })

    best = min(candidates, key=lambda item: item["expected_cost"])
    return ansatz, gamma, beta, hamiltonian, best, candidates


def evaluate(processor, ansatz, gamma, beta, angles, noisy, instance, optimum):
    """Run official simulator and calculate portfolio quality metrics."""
    n = len(instance["mu"])
    mu = instance["mu"]
    sigma = instance["sigma"]
    q = instance["q"]
    k = instance["k"]
    shots = instance["shots"]

    circuit = ansatz.assign_parameters({
        gamma: angles["gamma"],
        beta: angles["beta"],
    }).copy()
    circuit.measure_all()

    transpiled = qff.transpile_for(circuit, processor)
    backend = qff.simulator(noisy=noisy, processor=processor)
    counts = backend.run(transpiled, shots=shots).result().get_counts()

    total_shots = sum(counts.values())
    valid_shots = 0
    optimal_shots = 0
    valid_objective_sum = 0.0
    all_objective_sum = 0.0
    penalty_cost_sum = 0.0
    best_valid_score = None

    optimum_x = np.asarray(optimum["x"], dtype=int)

    for bitstring, count in counts.items():
        x = np.asarray(qff.counts_to_x(bitstring), dtype=int)[:n]
        if len(x) != n:
            raise ValueError(
                f"Expected {n} measured bits, got {len(x)}: {bitstring}"
            )

        score = objective(x, mu, sigma, q)
        valid = int(np.sum(x)) == k
        optimal = valid and np.array_equal(x, optimum_x)
        penalized_cost = -score + instance["current_lambda"] * (
            int(np.sum(x)) - k
        ) ** 2

        all_objective_sum += score * count
        penalty_cost_sum += penalized_cost * count

        if valid:
            valid_shots += count
            valid_objective_sum += score * count
            if best_valid_score is None or score > best_valid_score:
                best_valid_score = score
        if optimal:
            optimal_shots += count

    metrics = qff.circuit_metrics(transpiled, processor)

    return {
        "problem": "PS-O2",
        "processor": processor["name"],
        "lambda": instance["current_lambda"],
        "noise": "noisy" if noisy else "ideal",
        "shots": total_shots,
        "best_seed": angles["seed"],
        "gamma": angles["gamma"],
        "beta": angles["beta"],
        "optimized_expected_penalized_cost": angles["expected_cost"],
        "valid_solution_frequency": valid_shots / total_shots,
        "optimal_portfolio_probability": optimal_shots / total_shots,
        "mean_objective_all_samples": all_objective_sum / total_shots,
        "mean_objective_valid_samples": (
            valid_objective_sum / valid_shots if valid_shots else None
        ),
        "best_measured_feasible_objective": best_valid_score,
        "mean_penalized_cost": penalty_cost_sum / total_shots,
        "classical_optimal_objective": optimum["objective"],
        "physical_qubits": processor["num_qubits"],
        "transpiled_depth": metrics.get("depth"),
        "transpiled_cx": metrics.get("cx"),
    }


def main():
    instance = load_instance()
    processor_d = qff.load_processor(str(PROCESSOR_D_PATH))
    validation = qff.validate_processor_d(
        processor_d, required_qubits=len(instance["mu"])
    )
    if validation:
        raise ValueError(
            "Processor D failed validation:\n- " + "\n- ".join(validation)
        )

    optimum = exact_classical_optimum(
        instance["mu"], instance["sigma"], instance["q"], instance["k"]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    optimization_summary = []

    print("QFF Phase 2 — Processor D penalty sweep")
    print("Lambda values:", LAMBDA_VALUES)
    print("Seeds:", instance["seeds"])
    print("Shots per lambda/noise setting:", instance["shots"])
    print("Classical optimal portfolio:", optimum["assets"])
    print(f'Classical optimal objective: {optimum["objective"]:.4f}')
    print("-" * 76)

    for lam in LAMBDA_VALUES:
        print(f"\nOptimizing lambda={lam} ...")
        ansatz, gamma, beta, hamiltonian, best, candidates = optimize_for_lambda(
            lam, instance
        )
        optimization_summary.append({
            "lambda": lam,
            "best_initialization": best,
            "all_initializations": candidates,
        })

        print(
            f'  Best seed={best["seed"]}, gamma={best["gamma"]:.5f}, '
            f'beta={best["beta"]:.5f}, '
            f'expected cost={best["expected_cost"]:.6f}'
        )

        instance["current_lambda"] = lam

        for noisy in (False, True):
            result = evaluate(
                processor_d, ansatz, gamma, beta, best, noisy, instance, optimum
            )
            rows.append(result)
            print(
                f'  {result["noise"]:5s}: '
                f'valid={result["valid_solution_frequency"]:.4f}, '
                f'P_opt={result["optimal_portfolio_probability"]:.4f}, '
                f'mean F={result["mean_objective_all_samples"]:.4f}'
            )

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary_path = OUTPUT_PATH.with_name("penalty_sweep_optimization.json")
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(optimization_summary, file, indent=2)

    print("\nPenalty sweep completed.")
    print(f"Saved {len(rows)} result rows to: {OUTPUT_PATH}")
    print(f"Saved optimization details to: {summary_path}")


if __name__ == "__main__":
    main()
