
"""Problem definition and QUBO construction for Qiskit Fall Fest PS-O2."""

from dataclasses import dataclass

import numpy as np


NUM_ASSETS = 4

# Inputs matching main.ipynb.
RETURNS = np.array([0.12, 0.18, 0.10, 0.22], dtype=float)

SIGMA = np.array(
    [
        [0.04, 0.01, 0.02, 0.01],
        [0.01, 0.09, 0.01, 0.03],
        [0.02, 0.01, 0.05, 0.02],
        [0.01, 0.03, 0.02, 0.08],
    ],
    dtype=float,
)

RISK_AVERSION = 2.0
BUDGET_PENALTY = 20.0
TARGET_ASSETS = 2
QAOA_P = 1


def validate_risk_matrix(sigma):
    """Validate the covariance matrix."""
    sigma = np.asarray(sigma, dtype=float)

    if sigma.shape != (NUM_ASSETS, NUM_ASSETS):
        raise ValueError("Risk matrix must have shape (4, 4).")

    if not np.all(np.isfinite(sigma)):
        raise ValueError("Risk matrix must contain finite values.")

    if not np.allclose(sigma, sigma.T):
        raise ValueError("Risk matrix must be symmetric.")

    return sigma


@dataclass
class PortfolioProblem:
    """Configuration for the four-asset portfolio problem."""

    returns: np.ndarray
    sigma: np.ndarray
    risk_aversion: float = RISK_AVERSION
    budget_penalty: float = BUDGET_PENALTY
    target_assets: int = TARGET_ASSETS
    matrix_source: str = "notebook_benchmark"

    def __post_init__(self):
        self.returns = np.asarray(self.returns, dtype=float).copy()
        self.sigma = validate_risk_matrix(self.sigma).copy()

        if self.returns.shape != (NUM_ASSETS,):
            raise ValueError("Returns must contain exactly four values.")

        if not np.all(np.isfinite(self.returns)):
            raise ValueError("Returns must contain finite values.")

        if not np.isfinite(self.risk_aversion) or self.risk_aversion < 0:
            raise ValueError("Risk aversion must be finite and non-negative.")

        if not np.isfinite(self.budget_penalty) or self.budget_penalty < 0:
            raise ValueError("Budget penalty must be finite and non-negative.")

        if not isinstance(self.target_assets, (int, np.integer)):
            raise ValueError("Target assets must be an integer.")

        if not 0 <= self.target_assets <= NUM_ASSETS:
            raise ValueError("Target assets must be between 0 and 4.")


def load_problem():
    """Load the same inputs and parameters used in main.ipynb."""
    return PortfolioProblem(
        returns=RETURNS,
        sigma=SIGMA,
    )


def portfolio_objective(
    x,
    problem=None,
    include_budget_penalty=True,
):
    """
    Evaluate the notebook's minimization objective:

    E(x) = x.T @ Sigma @ x
           - q * (returns.T @ x)
           + penalty * (sum(x) - target_assets)**2
    """
    if problem is None:
        problem = load_problem()

    x = np.asarray(x)

    if x.shape != (NUM_ASSETS,):
        raise ValueError("Portfolio must contain exactly four values.")

    if not np.all(np.isin(x, [0, 1])):
        raise ValueError("Portfolio values must be binary (0 or 1).")

    x = x.astype(float)

    value = (
        x @ problem.sigma @ x
        - problem.risk_aversion * (problem.returns @ x)
    )

    if include_budget_penalty:
        value += problem.budget_penalty * (
            x.sum() - problem.target_assets
        ) ** 2

    return float(value)


def qubo_coefficients(problem=None):
    """
    Return the upper-triangular QUBO matrix and constant offset.

    Convention:
        E(x) = offset
             + sum_i Q[i, i] * x[i]
             + sum_(i < j) Q[i, j] * x[i] * x[j]

    The coefficients match the objective in main.ipynb.
    """
    if problem is None:
        problem = load_problem()

    q = np.zeros((NUM_ASSETS, NUM_ASSETS), dtype=float)

    penalty = problem.budget_penalty
    k = problem.target_assets

    for i in range(NUM_ASSETS):
        q[i, i] = (
            problem.sigma[i, i]
            - problem.risk_aversion * problem.returns[i]
            + penalty * (1 - 2 * k)
        )

        for j in range(i + 1, NUM_ASSETS):
            q[i, j] = 2 * problem.sigma[i, j] + 2 * penalty

    offset = penalty * k**2

    return q, float(offset)


def qubo_energy(x, problem=None):
    """Evaluate the QUBO energy using the notebook's convention."""
    if problem is None:
        problem = load_problem()

    x = np.asarray(x)

    if x.shape != (NUM_ASSETS,):
        raise ValueError("Portfolio must contain exactly four values.")

    if not np.all(np.isin(x, [0, 1])):
        raise ValueError("Portfolio values must be binary (0 or 1).")

    x = x.astype(float)
    q, offset = qubo_coefficients(problem)

    return float(offset + x @ q @ x)
