"""
src/qubo.py
Constructs the QUBO formulation for 4-item Knapsack Problem (PS-O2).
"""

import numpy as np

def build_knapsack_qubo(weights, values, capacity, penalty_lambda):
    """
    Constructs QUBO matrix Q for Knapsack problem.
    decision variables: x_0, x_1, x_2, x_3
    Slack variable approach or penalty formulation:
    Cost = - sum(v_i x_i) + lambda * (sum(w_i x_i) - C)^2
    For 4 items with weights [2, 3, 4, 5], capacity 7:
    """
    n = len(weights)
    Q = np.zeros((n, n))
    
    # Linear objective term: -v_i + lambda * (w_i^2 - 2*C*w_i)
    for i in range(n):
        Q[i, i] = -values[i] + penalty_lambda * (weights[i]**2 - 2 * capacity * weights[i])
        
    # Quadratic cross terms: 2 * lambda * w_i * w_j for i < j
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] = 2 * penalty_lambda * weights[i] * weights[j]
            
    return Q

def evaluate_solution(x, weights, values, capacity):
    total_weight = sum(w * x_i for w, x_i in zip(weights, x))
    total_value = sum(v * x_i for v, x_i in zip(values, x))
    is_feasible = total_weight <= capacity
    return total_weight, total_value, is_feasible
