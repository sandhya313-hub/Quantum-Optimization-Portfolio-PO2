
"""Processor configuration loading for Qiskit Fall Fest PS-O2.

Processor topology is read from the repository's JSON configuration files.
Noise models are handled separately by the experiment.
"""

import json
from pathlib import Path

from qiskit.transpiler import CouplingMap


# Repository layout: project_root/processors/processor_A.json
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSOR_CONFIG_DIR = PROJECT_ROOT / "processors"

EXPECTED_QUBITS = {
    "A": 5,
    "B": 9,
}


def load_processor_config(processor):
    """Load and validate Processor A or Processor B from its JSON file.

    Args:
        processor: "A", "B", "processor_A", or "processor_B".

    Returns:
        The validated configuration dictionary.
    """
    aliases = {
        "A": "processor_A",
        "B": "processor_B",
        "processor_A": "processor_A",
        "processor_B": "processor_B",
    }

    if processor not in aliases:
        raise ValueError(
            "Processor must be 'A', 'B', 'processor_A', or 'processor_B'."
        )

    config_name = aliases[processor]
    config_path = PROCESSOR_CONFIG_DIR / f"{config_name}.json"

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Processor configuration not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    validate_processor_config(config, config_name)
    return config


def validate_processor_config(config, processor_name):
    """Validate qubit count and coupling edges in a processor configuration."""
    if not isinstance(config, dict):
        raise ValueError("Processor configuration must be a JSON object.")

    processor_letter = processor_name[-1]
    expected_qubits = EXPECTED_QUBITS[processor_letter]

    if config.get("qubit_count") != expected_qubits:
        raise ValueError(
            f"{processor_name} must have {expected_qubits} qubits."
        )

    edges = config.get("coupling_edges")

    if not isinstance(edges, list):
        raise ValueError("'coupling_edges' must be a list.")

    seen_edges = set()

    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"Invalid coupling edge: {edge!r}")

        source, target = edge

        if (
            not isinstance(source, int)
            or isinstance(source, bool)
            or not isinstance(target, int)
            or isinstance(target, bool)
        ):
            raise ValueError(f"Qubit indices must be integers: {edge!r}")

        if not (
            0 <= source < expected_qubits
            and 0 <= target < expected_qubits
        ):
            raise ValueError(
                f"Coupling edge {edge!r} references an invalid qubit."
            )

        if source == target:
            raise ValueError("A qubit cannot be coupled to itself.")

        undirected_edge = tuple(sorted((source, target)))

        if undirected_edge in seen_edges:
            raise ValueError(f"Duplicate coupling edge: {edge!r}")

        seen_edges.add(undirected_edge)

    return True


def get_coupling_edges(processor):
    """Return the configured coupling edges for a processor."""
    config = load_processor_config(processor)
    return [tuple(edge) for edge in config["coupling_edges"]]


def get_coupling_map(processor):
    """Create a symmetric Qiskit CouplingMap from the configured topology.

    The JSON files describe physical connectivity as undirected edges.
    The returned map includes both directions for each connection.
    """
    edges = get_coupling_edges(processor)

    coupling_map = CouplingMap(couplinglist=edges)
    coupling_map.make_symmetric()

    return coupling_map


def get_processor_summary(processor):
    """Return a concise summary of a processor's configured topology."""
    config = load_processor_config(processor)

    return {
        "name": config["name"],
        "qubit_count": config["qubit_count"],
        "coupling_edges": len(config["coupling_edges"]),
        "noise_model": config.get("noise_model"),
        "source": config.get("source"),
    }
