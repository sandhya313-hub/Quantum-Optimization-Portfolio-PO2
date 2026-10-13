
"""Circuit transpilation and routing for Qiskit Fall Fest PS-O2."""

from qiskit import transpile

from .processors import get_coupling_map


BASIS_GATES = ["rz", "sx", "x", "cx"]
TRANSPILE_SEED = 42
OPTIMIZATION_LEVEL = 1


def transpile_reference(circuit):
    """Transpile a logical circuit without a processor coupling constraint."""
    return transpile(
        circuit,
        basis_gates=BASIS_GATES,
        optimization_level=OPTIMIZATION_LEVEL,
        seed_transpiler=TRANSPILE_SEED,
    )


def transpile_for_processor(circuit, processor):
    """Transpile a circuit for Processor A or Processor B.

    Args:
        circuit: The same logical Qiskit circuit used for both processors.
        processor: "A", "B", "processor_A", or "processor_B".

    Returns:
        The transpiled QuantumCircuit.
    """
    coupling_map = get_coupling_map(processor)

    return transpile(
        circuit,
        coupling_map=coupling_map,
        basis_gates=BASIS_GATES,
        optimization_level=OPTIMIZATION_LEVEL,
        seed_transpiler=TRANSPILE_SEED,
    )


def compare_processor_transpilation(circuit):
    """Transpile one logical circuit for the reference and both processors."""
    reference = transpile_reference(circuit)
    processor_a = transpile_for_processor(circuit, "A")
    processor_b = transpile_for_processor(circuit, "B")

    return {
        "reference": reference,
        "processor_A": processor_a,
        "processor_B": processor_b,
    }
