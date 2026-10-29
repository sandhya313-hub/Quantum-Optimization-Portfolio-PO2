
import itertools
import json

# Load the official Phase 2 problem data
with open("instances.json", "r") as file:
    data = json.load(file)["PS-O2"]

returns = data["expected_returns"]
risk_matrix = data["risk_matrix"]
q = data["risk_aversion_q"]
k = data["k"]

def evaluate_portfolio(x):
    # Calculate total expected return
    total_return = sum(
        returns[i] * x[i] for i in range(len(x))
    )

    # Calculate portfolio risk: x^T Sigma x
    risk = sum(
        x[i] * risk_matrix[i][j] * x[j]
        for i in range(len(x))
        for j in range(len(x))
    )

    # Official objective: maximize return minus risk penalty
    score = total_return - q * risk

    return total_return, risk, score


results = []

# Generate all 16 possible portfolios
for x in itertools.product([0, 1], repeat=len(returns)):
    if sum(x) == k:
        total_return, risk, score = evaluate_portfolio(x)
        results.append((x, total_return, risk, score))

# Highest objective score is the best feasible portfolio
results.sort(key=lambda item: item[3], reverse=True)

print("CLASSICAL PORTFOLIO RESULTS")
print("-" * 60)

for x, total_return, risk, score in results:
    selected = [i for i, bit in enumerate(x) if bit == 1]
    print(
        f"Portfolio {x} | Assets {selected} | "
        f"Return={total_return:.2f} | "
        f"Risk={risk:.2f} | Score={score:.2f}"
    )

print("\nBEST PORTFOLIO")
print("Selected assets:", [
    i for i, bit in enumerate(results[0][0]) if bit == 1
])
print("Best score:", results[0][3])
