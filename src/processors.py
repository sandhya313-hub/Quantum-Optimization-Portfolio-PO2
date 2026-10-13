
"""Load and validate Processor A and Processor B configurations."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSORS_DIR = PROJECT_ROOT / "processors"

EXPECTED_QUBITS = {
    "processor_A": 5,
    "processor_B": 9,
}


def load_processor(processor_name):
    """Load a processor configuration from processors/<name>.json."""
    if processor_name not in EXPECTED_QUBITS:
        raise ValueError(
            "processor_name must be 'processor_A' or 'processor_B'."
        )

    config_path = PROCESSORS_DIR / f"{processor_name}.json"

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Processor configuration not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    validate_processor(config, processor_name)
    return config


def validate_processor(config, processor_name):
    """Check the processor's qubit count and coupling-map structure."""
    if not isinstance(config, dict):
        raise ValueError("Processor configuration must be a JSON object.")

    expected_qubits = EXPECTED_QUBITS[processor_name]

    qubit_count = config.get(
        "num_qubits",
        config.get("n_qubits", config.get("qubits")),
    )

    if isinstance(qubit_count, list):
        qubit_count = len(qubit_count)

    if qubit_count != expected_qubits:
        raise ValueError(
            f"{processor_name} must describe {expected_qubits} qubits; "
            f"found {qubit_count!r}."
        )

    edges = config.get(
        "coupling_map",
        config.get("coupling_edges", config.get("edges")),
    )

    if not isinstance(edges, list):
        raise ValueError(
            f"{processor_name} must contain a list of coupling edges."
        )

    for edge in edges:
        if (
            not isinstance(edge, (list, tuple))
            or len(edge) != 2
            or any(
                not isinstance(q, int) or isinstance(q, bool)
                for q in edge
            )
        ):
            raise ValueError(f"Invalid coupling edge: {edge!r}")

        if any(q < 0 or q >= expected_qubits for q in edge):
            raise ValueError(
                f"Coupling edge {edge!r} references an invalid qubit."
            )

        if edge[0] == edge[1]:
            raise ValueError("A coupling edge cannot connect a qubit to itself.")

    return True


def load_both_processors():
    """Return validated Processor A and Processor B configurations."""
    return {
        name: load_processor(name)
        for name in EXPECTED_QUBITS
    }
