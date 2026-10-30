"""
generate_results.py
Executes full PS-O2 benchmark across Processor A, Processor B, and Processor D.
Generates all required figures comparing Processors A, B, and D, and tables.
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from scipy.optimize import minimize

from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# Set seeds for reproducibility
SEED = 42
np.random.seed(SEED)

os.makedirs("results/tables", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)

# 1. Load Instance & Processors
with open("data/instance.json") as f:
    instance = json.load(f)

processors = {}
for p_name in ["processor_A.json", "processor_B.json", "processor_D.json"]:
    path = os.path.join("processors", p_name)
    with open(path) as f:
        data = json.load(f)
        processors[data["name"]] = data

# Helper: Noise model construction
def create_noise_model(proc):
    noise_model = NoiseModel()
    p_cx = proc.get("cx_error", 0.01)
    p_single = proc.get("single_qubit_error", 0.001)
    
    err_cx = depolarizing_error(p_cx, 2)
    err_single = depolarizing_error(p_single, 1)
    
    noise_model.add_all_qubit_quantum_error(err_single, ["rz", "sx", "x"])
    noise_model.add_all_qubit_quantum_error(err_cx, ["cx"])
    return noise_model

# 1. Bell State Verification (Section 4)
def run_bell_verification():
    print("=== Running Bell State Verification (A, B, D) ===")
    bell_records = []
    
    for name, proc in processors.items():
        edges = proc.get("edges", proc.get("coupling_edges"))
        e = edges[0]
        q0, q1 = e[0], e[1]
        
        qc = QuantumCircuit(proc["num_qubits"], 2)
        qc.h(q0)
        qc.cx(q0, q1)
        qc.measure([q0, q1], [0, 1])
        
        # Ideal execution
        backend_ideal = AerSimulator()
        t_qc = transpile(qc, backend=backend_ideal, seed_transpiler=SEED)
        res_ideal = backend_ideal.run(t_qc, shots=4000, seed_simulator=SEED).result()
        counts_ideal = res_ideal.get_counts()
        ideal_fidelity = (counts_ideal.get('00', 0) + counts_ideal.get('11', 0)) / 4000.0
        
        # Noisy execution
        noise_model = create_noise_model(proc)
        backend_noisy = AerSimulator(noise_model=noise_model)
        t_qc_noisy = transpile(qc, backend=backend_noisy, seed_transpiler=SEED)
        res_noisy = backend_noisy.run(t_qc_noisy, shots=4000, seed_simulator=SEED).result()
        counts_noisy = res_noisy.get_counts()
        noisy_fidelity = (counts_noisy.get('00', 0) + counts_noisy.get('11', 0)) / 4000.0
        
        bell_records.append({
            "processor": name,
            "qubit_pair": f"({q0},{q1})",
            "cx_gate_error": proc.get("cx_error", 0.01),
            "ideal_fidelity": round(ideal_fidelity, 4),
            "noisy_fidelity": round(noisy_fidelity, 4),
            "fidelity_drop": round(ideal_fidelity - noisy_fidelity, 4)
        })
        
    df_bell = pd.DataFrame(bell_records)
    df_bell.to_csv("results/tables/bell.csv", index=False)
    print("Saved results/tables/bell.csv")
    return df_bell

# 2. QAOA & Transpilation Benchmark
weights = instance["weights"]
values = instance["values"]
capacity = instance["capacity"]

def knapsack_cost(bitstring, penalty_lambda=10.0):
    x = [int(b) for b in reversed(bitstring)]
    w_sum = sum(x[i] * weights[i] for i in range(4))
    v_sum = sum(x[i] * values[i] for i in range(4))
    
    if w_sum <= capacity:
        cost = -v_sum
    else:
        cost = -v_sum + penalty_lambda * ((w_sum - capacity) ** 2)
    return cost

def build_qaoa_circuit(gamma, beta):
    qc = QuantumCircuit(4)
    for i in range(4):
        qc.h(i)
        
    for i in range(4):
        qc.rz(gamma * values[i], i)
    for i in range(4):
        for j in range(i + 1, 4):
            qc.cx(i, j)
            qc.rz(gamma * weights[i] * weights[j] * 0.5, j)
            qc.cx(i, j)
            
    for i in range(4):
        qc.rx(2 * beta, i)
        
    return qc

def run_qaoa_benchmark():
    print("=== Running QAOA Benchmark across Processors A, B, D ===")
    
    def objective(params):
        gamma, beta = params
        qc = build_qaoa_circuit(gamma, beta)
        qc.measure_all()
        backend = AerSimulator()
        t_qc = transpile(qc, backend=backend, seed_transpiler=SEED)
        counts = backend.run(t_qc, shots=2000, seed_simulator=SEED).result().get_counts()
        
        total_cost = 0.0
        for bitstr, cnt in counts.items():
            clean_b = bitstr.replace(" ", "")[-4:]
            total_cost += cnt * knapsack_cost(clean_b)
        return total_cost / 2000.0

    res_opt = minimize(objective, [0.5, 0.5], method="COBYLA", bounds=[(0, np.pi), (0, np.pi)])
    opt_gamma, opt_beta = res_opt.x
    
    qc_base = build_qaoa_circuit(opt_gamma, opt_beta)
    qc_base.measure_all()
    
    results_records = []
    processor_distributions = {}
    
    feasible_states = ['0000','0001','0010','0100','1000','0011','0101','1001','0110']
    
    for name, proc in processors.items():
        edges = proc.get("edges", proc.get("coupling_edges"))
        num_q = proc["num_qubits"]
        backend = GenericBackendV2(num_qubits=num_q, coupling_map=edges)
        
        t_qc = transpile(qc_base, backend=backend, optimization_level=3, seed_transpiler=SEED)
        
        depth = t_qc.depth()
        cx_count = t_qc.count_ops().get("cx", 0)
        total_gates = sum(t_qc.count_ops().values())
        
        # Ideal execution
        aer_sim = AerSimulator()
        res_ideal = aer_sim.run(t_qc, shots=4000, seed_simulator=SEED).result()
        counts_ideal = {k.replace(" ", "")[-4:]: v for k, v in res_ideal.get_counts().items()}
        
        prob_optimal_ideal = counts_ideal.get('1001', 0) / 4000.0
        prob_feasible_ideal = sum(counts_ideal.get(st, 0) for st in feasible_states) / 4000.0
        
        # Noisy execution
        noise_model = create_noise_model(proc)
        aer_noisy = AerSimulator(noise_model=noise_model)
        res_noisy = aer_noisy.run(t_qc, shots=4000, seed_simulator=SEED).result()
        counts_noisy = {k.replace(" ", "")[-4:]: v for k, v in res_noisy.get_counts().items()}
        
        processor_distributions[name] = counts_noisy
        
        prob_optimal_noisy = counts_noisy.get('1001', 0) / 4000.0
        prob_feasible_noisy = sum(counts_noisy.get(st, 0) for st in feasible_states) / 4000.0
        mean_cost_noisy = sum(counts_noisy.get(st, 0) * knapsack_cost(st) for st in counts_noisy) / 4000.0
        
        results_records.append({
            "processor": name,
            "num_qubits": num_q,
            "connectivity_edges": len(edges),
            "circuit_depth": depth,
            "cx_count": cx_count,
            "total_gates": total_gates,
            "ideal_optimal_prob": round(prob_optimal_ideal, 4),
            "ideal_feasible_prob": round(prob_feasible_ideal, 4),
            "noisy_optimal_prob": round(prob_optimal_noisy, 4),
            "noisy_feasible_prob": round(prob_feasible_noisy, 4),
            "noisy_mean_cost": round(mean_cost_noisy, 4)
        })
        
    df_results = pd.DataFrame(results_records)
    df_results.to_csv("results/tables/results.csv", index=False)
    print("Saved results/tables/results.csv")
    return df_results, processor_distributions

# 3. Generate Complete Figure Suite (Processors A, B, D)
def generate_all_figures(df_results, distributions):
    print("=== Generating Visualizations for Processors A, B, and D ===")
    sns.set_theme(style="whitegrid")
    
    # Figure 1: Processor Topology Comparison (A, B, D)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for ax, (name, proc) in zip(axes, processors.items()):
        edges = proc.get("edges", proc.get("coupling_edges"))
        G = nx.Graph()
        G.add_nodes_from(range(proc["num_qubits"]))
        G.add_edges_from(edges)
        
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#4285F4', node_size=600)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#555555', width=2)
        nx.draw_networkx_labels(G, pos, ax=ax, font_color='white', font_weight='bold')
        
        ax.set_title(f"{name}\n({proc['num_qubits']} Qubits, {len(edges)} Edges)", fontsize=12, fontweight='bold')
        ax.axis('off')
        
    plt.suptitle("Processor Topologies Comparison (A, B, D)", fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("results/figures/processor_topologies.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Figure 2: Transpilation Comparison across A, B, D
    plt.figure(figsize=(10, 6))
    x = np.arange(len(df_results))
    width = 0.25
    
    plt.bar(x - width, df_results["circuit_depth"], width, label="Circuit Depth", color="#2b5c8f")
    plt.bar(x, df_results["cx_count"], width, label="CX Gate Count", color="#d95f02")
    plt.bar(x + width, df_results["total_gates"], width, label="Total Gate Count", color="#7570b3")
    
    plt.xlabel("Processor Architecture", fontsize=12, fontweight="bold")
    plt.ylabel("Count / Depth", fontsize=12, fontweight="bold")
    plt.title("Transpilation Complexity Across Processors A, B, D (p=1 QAOA)", fontsize=14, fontweight="bold")
    plt.xticks(x, df_results["processor"], fontsize=11)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("results/figures/transpilation_comparison.png", dpi=300)
    plt.close()
    
    # Figure 3: Noisy Quality Comparison across A, B, D
    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, df_results["noisy_optimal_prob"], width, label="Optimal State '1001' Probability", color="#1b9e77")
    plt.bar(x + width/2, df_results["noisy_feasible_prob"], width, label="Total Feasible States Probability", color="#e7298a")
    
    plt.xlabel("Processor Architecture", fontsize=12, fontweight="bold")
    plt.ylabel("Probability", fontsize=12, fontweight="bold")
    plt.title("QAOA Solution Success Probabilities Under Hardware Noise (A, B, D)", fontsize=14, fontweight="bold")
    plt.xticks(x, df_results["processor"], fontsize=11)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("results/figures/noisy_quality_comparison.png", dpi=300)
    plt.close()
    
    # Figure 4: Noisy Shot Distributions across Processors A, B, D
    all_bitstrings = [f"{i:04b}" for i in range(16)]
    df_dist = pd.DataFrame(index=all_bitstrings)
    
    for name, cnts in distributions.items():
        total_shots = sum(cnts.values())
        df_dist[name] = [cnts.get(b, 0) / total_shots for b in all_bitstrings]
        
    plt.figure(figsize=(12, 6))
    df_dist.plot(kind='bar', figsize=(12, 6), width=0.8, colormap='viridis')
    plt.xlabel("Bitstring (Item Selection x3 x2 x1 x0)", fontsize=12, fontweight="bold")
    plt.ylabel("Probability", fontsize=12, fontweight="bold")
    plt.title("Noisy Shot Probability Distribution Across Processors A, B, D", fontsize=14, fontweight="bold")
    plt.axvline(x=9, color='red', linestyle='--', label='Optimal State (1001)') # 1001 is index 9
    plt.legend(fontsize=11)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("results/figures/noisy_shot_distribution.png", dpi=300)
    plt.close()
    
    # Figure 5: Penalty Parameter Sweep (Processor D)
    plt.figure(figsize=(8, 5))
    lambdas = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0]
    proc_D = processors["Processor D"]
    backend_D = GenericBackendV2(num_qubits=proc_D["num_qubits"], coupling_map=proc_D["edges"])
    
    probs = []
    for lam in lambdas:
        def obj_lam(params):
            g, b = params
            qc = build_qaoa_circuit(g, b)
            qc.measure_all()
            sim = AerSimulator()
            t_c = transpile(qc, backend=sim, seed_transpiler=SEED)
            c = sim.run(t_c, shots=1000, seed_simulator=SEED).result().get_counts()
            return sum(cnt * knapsack_cost(b_str.replace(" ","")[-4:], lam) for b_str, cnt in c.items()) / 1000.0
        
        r = minimize(obj_lam, [0.5, 0.5], method="COBYLA")
        g_opt, b_opt = r.x
        qc_opt = build_qaoa_circuit(g_opt, b_opt)
        qc_opt.measure_all()
        t_opt = transpile(qc_opt, backend=backend_D, optimization_level=3, seed_transpiler=SEED)
        
        aer_n = AerSimulator(noise_model=create_noise_model(proc_D))
        cnts = aer_n.run(t_opt, shots=2000, seed_simulator=SEED).result().get_counts()
        probs.append(cnts.get("1001", 0) / 2000.0)
        
    plt.plot(lambdas, probs, 'o-', color='#386cb0', linewidth=2.5, markersize=8)
    plt.xlabel("Penalty Parameter (λ)", fontsize=12, fontweight="bold")
    plt.ylabel("Optimal State '1001' Probability", fontsize=12, fontweight="bold")
    plt.title("Processor D Solution Quality vs. Penalty Parameter λ", fontsize=14, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("results/figures/penalty_sweep.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    run_bell_verification()
    df_res, dists = run_qaoa_benchmark()
    generate_all_figures(df_res, dists)
    print("=== All Results & Figures Successfully Generated ===")
