
import json
import numpy as np
from itertools import product

# Load the official PS-O2 problem data
with open("instances.json", "r") as file:
    data = json.load(file)["PS-O2"]

mu = np.array(data["expected_returns"], dtype=float)
Sigma = np.array(data["risk_matrix"], dtype=float)
q = float(data["risk_aversion_q"])
k = int(data["k"])
lam = float(data["reference_penalty_lambda"])

# Build the QUBO matrix Q for:
# C(x) = -mu.T @ x + q * x.T @ Sigma @ x
#        + lam * (sum(x) - k)**2

n = len(mu)

# x_i squared equals x_i for binary variables
Q = q * Sigma.copy()
np.fill_diagonal(Q, np.diag(Q) - mu)

# Expand the penalty:
# lam * (sum(x) - k)**2
# = lam * ((1 - 2k) * sum(x)
#          + 2 * sum_{i<j}(x_i*x_j) + k**2)

for i in range(n):
    Q[i, i] += lam * (1 - 2 * k)

for i in range(n):
    for j in range(i + 1, n):
        Q[i, j] += 2 * lam

constant = lam * k**2

print("QUBO matrix Q:")
print(Q)
print("\nConstant offset:", constant)

# Verify the QUBO against the original objective
def original_cost(x):
    x = np.array(x, dtype=float)
    return (
        -mu @ x
        + q * (x @ Sigma @ x)
        + lam * (sum(x) - k) ** 2
    )

def qubo_cost(x):
    x = np.array(x, dtype=float)
    return x @ Q @ x + constant

print("\nQUBO verification:")
for x in product([0, 1], repeat=n):
    print(
        f"x={x}, "
        f"original={original_cost(x):.4f}, "
        f"QUBO={qubo_cost(x):.4f}"
    )

# Report the best valid portfolio using the QUBO cost
valid = [
    (qubo_cost(x), x)
    for x in product([0, 1], repeat=n)
    if sum(x) == k
]
best_cost, best_x = min(valid)

print("\nBest feasible portfolio:", best_x)
print("Minimum QUBO cost:", round(best_cost, 4))
