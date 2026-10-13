
"""Problem definition and QUBO construction for Qiskit Fall Fest PS-O2."""

from dataclasses import dataclass
import numpy as np


NUM_ASSETS = 4

# Inputs used in the current notebook benchmark.
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
    """Validate a finite, symmetric 4x4 risk matrix."""
    if sigma is None:
        raise ValueError("A risk matrix must be provided.")

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
    """Configuration for the four-asset portfolio optimization problem."""

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
    """Load the current notebook benchmark configuration."""
    return PortfolioProblem(
        returns=RETURNS,
        sigma=SIGMA,
    )


def portfolio_objective(
    x,
    problem=None,
    include_budget_penalty=True,
):
    """Evaluate the maximization objective used in the notebook.

    f(x) = returns.T @ x
           - risk_aversion * (x.T @ Sigma @ x)
           - budget_penalty * (sum(x) - target_assets)**2

    Returns the maximization score. The QUBO energy is its negative.
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
        problem.returns @ x
        - problem.risk_aversion * (x @ problem.sigma @ x)
    )

    if include_budget_penalty:
        value -= problem.budget_penalty * (
            int(x.sum()) - problem.target_assets
        ) ** 2

    return float(value)


def qubo_coefficients(problem=None):
    """Return Q and the constant offset for minimizing -portfolio_objective.

    Uses the convention:
        energy(x) = x.T @ Q @ x + offset

    Q is returned as an upper-triangular matrix so that its off-diagonal
    coefficients can be used directly in a standard QUBO expression.
    """
    if problem is None:
        problem = load_problem()

    q = (
        problem.risk_aversion * problem.sigma
        - np.diag(problem.returns)
    )

    # Convert the squared budget penalty into a quadratic polynomial.
    penalty = problem.budget_penalty
    k = problem.target_assets

    q += penalty * (np.ones((NUM_ASSETS, NUM_ASSETS)) - np.eye(NUM_ASSETS))
    q += np.diag(penalty * (1 - 2 * k) * np.ones(NUM_ASSETS))

    offset = penalty * (k ** 2)

    # Keep diagonal terms unchanged and combine symmetric off-diagonal terms.
    q_upper = np.triu(q + np.triu(q, 1).T)

    return q_upper, float(offset)


def qubo_energy(x, problem=None):
    """Evaluate the QUBO minimization energy."""
    if problem is None:
        problem = load_problem()

    x = np.asarray(x)

    if x.shape != (NUM_ASSETS,):
        raise ValueError("Portfolio must contain exactly four values.")

    if not np.all(np.isin(x, [0, 1])):
        raise ValueError("Portfolio values must be binary (0 or 1).")

    x = x.astype(float)
    q, offset = qubo_coefficients(problem)

    return float(x @ q @ x + offset)
