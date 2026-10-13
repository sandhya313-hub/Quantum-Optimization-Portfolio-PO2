
"""Plotting and coupling-graph visualization for the processor benchmark."""

import matplotlib.pyplot as plt
import networkx as nx


PROCESSOR_EDGES = {
    "A": [(0, 1), (1, 2), (1, 3), (3, 4)],
    "B": [
        (0, 1), (1, 2), (1, 6), (2, 3), (2, 6), (2, 5),
        (3, 4), (4, 5), (5, 6), (6, 7), (6, 8), (8, 0),
    ],
}

PROCESSOR_QUBITS = {"A": 5, "B": 9}


def plot_coupling_graph(processor="A", ax=None):
    """Visualize the qubits and connections of Processor A or B."""
    processor = processor.upper()

    if processor not in PROCESSOR_EDGES:
        raise ValueError("processor must be 'A' or 'B'.")

    graph = nx.Graph()
    graph.add_nodes_from(range(PROCESSOR_QUBITS[processor]))
    graph.add_edges_from(PROCESSOR_EDGES[processor])

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    positions = nx.spring_layout(graph, seed=42)

    nx.draw_networkx(
        graph,
        pos=positions,
        ax=ax,
        with_labels=True,
        node_size=900,
        font_size=10,
        width=1.8,
    )

    ax.set_title(f"Processor {processor} Coupling Graph")
    ax.axis("off")
    return ax


def plot_metric_comparison(metrics, metric, ax=None):
    """
    Compare one numeric metric across the reference and processors.

    Args:
        metrics: Dictionary returned by compare_circuit_metrics().
        metric: Metric key, such as 'circuit_depth' or 'transpiled_cx'.
        ax: Optional Matplotlib axes.
    """
    labels = []
    values = []

    for processor, result in metrics.items():
        value = result.get(metric)

        if value is not None:
            labels.append(processor.replace("_", " ").title())
            values.append(value)

    if not values:
        raise ValueError(f"No numeric values available for metric: {metric}")

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    ax.bar(labels, values)
    ax.set_title(f"Processor Comparison: {metric.replace('_', ' ').title()}")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_xlabel("Circuit")
    ax.tick_params(axis="x", rotation=15)

    return ax


def plot_processor_comparison():
    """Display Processor A and B coupling graphs side by side."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    plot_coupling_graph("A", ax=axes[0])
    plot_coupling_graph("B", ax=axes[1])

    fig.tight_layout()
    return fig, axes
