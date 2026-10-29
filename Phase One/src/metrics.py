
"""Circuit metrics for the Qiskit Fall Fest PS-O2 benchmark."""

from typing import Any, Dict, Optional

from qiskit import QuantumCircuit


def count_gates(circuit: QuantumCircuit) -> Dict[str, int]:
    """Return counts of the gates relevant to this benchmark."""
    gate_counts = circuit.count_ops()

    return {
        "cx_count": int(gate_counts.get("cx", 0)),
        "swap_count": int(gate_counts.get("swap", 0)),
        "rz_count": int(gate_counts.get("rz", 0)),
        "sx_count": int(gate_counts.get("sx", 0)),
        "x_count": int(gate_counts.get("x", 0)),
    }


def calculate_circuit_metrics(
    circuit: QuantumCircuit,
    reference_cx: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate circuit depth, gate counts, and routing overhead.

    Args:
        circuit: The transpiled quantum circuit to measure.
        reference_cx: CX count of the reference circuit, if available.

    Returns:
        A dictionary containing the calculated circuit metrics.
    """
    gates = count_gates(circuit)
    cx_count = gates["cx_count"]

    if reference_cx is None:
        additional_cx = None
        swap_equivalent_estimate = None
    else:
        additional_cx = max(0, cx_count - reference_cx)
        swap_equivalent_estimate = additional_cx / 3.0

    return {
        "physical_qubits": circuit.num_qubits,
        "circuit_depth": circuit.depth(),
        "reference_cx": reference_cx,
        "transpiled_cx": cx_count,
        "additional_cx": additional_cx,
        "explicit_swap_count": gates["swap_count"],
        "swap_equivalent_estimate": swap_equivalent_estimate,
        "rz_count": gates["rz_count"],
        "sx_count": gates["sx_count"],
        "x_count": gates["x_count"],
    }


def compare_circuit_metrics(
    reference_circuit: QuantumCircuit,
    processor_a_circuit: QuantumCircuit,
    processor_b_circuit: QuantumCircuit,
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate comparable metrics for the reference and both processors.
    """
    reference_metrics = calculate_circuit_metrics(reference_circuit)
    reference_cx = reference_metrics["transpiled_cx"]

    return {
        "reference": reference_metrics,
        "processor_A": calculate_circuit_metrics(
            processor_a_circuit,
            reference_cx=reference_cx,
        ),
        "processor_B": calculate_circuit_metrics(
            processor_b_circuit,
            reference_cx=reference_cx,
        ),
    }
