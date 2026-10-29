"""
run_bell_experiment.py
Qiskit Fall Fest 2026 Phase 2 — Bell-state verification for PS-O2.

Uses the official helper functions in qff_phase2.py without modifying them.
Runs connected and farthest-pair Bell experiments for Processors A, B, and D,
under ideal and official noisy simulation, and saves results to CSV.
"""

import csv
import json
from pathlib import Path

import qff_phase2 as qff


ROOT = Path(__file__).resolve().parent
PROCESSOR_D_PATH = ROOT / "processors" / "processor_D.json"
RESULTS_PATH = ROOT / "results" / "tables" / "bell.csv"


def all_pairs(processor):
    """Return all unique physical pairs (a, b), with a < b."""
    n = processor["num_qubits"]
    edges = {tuple(sorted((int(a), int(b)))) for a, b in processor["edges"]}
    return n, edges


def choose_bell_pairs(processor):
    """
    Pick one directly connected pair and one maximum-distance pair.
    If every pair is equally farthest (as in a complete graph), choose a
    different pair at that same maximum distance and state this in the output.
    """
    from qff_phase2 import coupling_map_from_edges

    n, edges = all_pairs(processor)
    cmap = coupling_map_from_edges(processor["edges"], n)

    connected_pair = sorted(edges)[0] if edges else None
    if connected_pair is None:
        raise ValueError(f'{processor["name"]} has no coupling edges.')

    distances = []
    for a in range(n):
        for b in range(a + 1, n):
            distances.append((int(cmap.distance(a, b)), (a, b)))

    max_distance = max(distance for distance, _ in distances)
    farthest_candidates = [
        pair for distance, pair in distances
        if distance == max_distance and pair != connected_pair
    ]

    if farthest_candidates:
        farthest_pair = farthest_candidates[0]
    else:
        # A two-qubit processor could have only one pair; keep the runner robust.
        farthest_pair = max(distances, key=lambda item: item[0])[1]

    return connected_pair, farthest_pair, max_distance, int(cmap.distance(*connected_pair))


def main():
    if not PROCESSOR_D_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find {PROCESSOR_D_PATH}. "
            "Create processors/processor_D.json before running this script."
        )

    processor_d = qff.load_processor(str(PROCESSOR_D_PATH))
    violations = qff.validate_processor_d(processor_d, required_qubits=4)
    if violations:
        raise ValueError(
            "Processor D failed official validation:\n- "
            + "\n- ".join(violations)
        )

    processors = [qff.PROCESSOR_A, qff.PROCESSOR_B, processor_d]
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    print("QFF Phase 2 — Bell-state verification")
    print(f"Shots per basis: {qff.SHOTS}")
    print("Processors: A, B, D")
    print("Conditions: ideal and noisy")
    print("-" * 72)

    for processor in processors:
        connected_pair, farthest_pair, max_distance, connected_distance = choose_bell_pairs(processor)
        pairs = [
            ("connected", connected_pair),
            ("farthest", farthest_pair),
        ]

        print(
            f'\n{processor["name"]}: {processor["num_qubits"]} qubits; '
            f'connected pair={connected_pair} (distance {connected_distance}); '
            f'farthest pair={farthest_pair} (maximum graph distance {max_distance})'
        )

        for pair_label, pair in pairs:
            for noisy in (False, True):
                result = qff.bell_experiment(
                    processor=processor,
                    physical_pair=pair,
                    noisy=noisy,
                    shots=qff.SHOTS,
                )

                row = {
                    "problem": "PS-O2",
                    "processor": processor["name"],
                    "pair_type": pair_label,
                    "qubit_0": pair[0],
                    "qubit_1": pair[1],
                    "pair_distance": result["pair_distance"],
                    "noise": "noisy" if noisy else "ideal",
                    "shots": result["shots"],
                    "XX": result["XX"],
                    "XX_se": result["XX_se"],
                    "YY": result["YY"],
                    "YY_se": result["YY_se"],
                    "ZZ": result["ZZ"],
                    "ZZ_se": result["ZZ_se"],
                    "fidelity": result["fidelity"],
                    "fidelity_se": result["fidelity_se"],
                    "cx": result.get("cx"),
                }
                rows.append(row)

                print(
                    f'  {pair_label:9s} | {row["noise"]:5s} | '
                    f'F={row["fidelity"]:.4f} ± {row["fidelity_se"]:.4f} | '
                    f'XX={row["XX"]:.4f}, YY={row["YY"]:.4f}, '
                    f'ZZ={row["ZZ"]:.4f}'
                )

    fieldnames = list(rows[0].keys())
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nBell experiment completed successfully.")
    print(f"Saved {len(rows)} result rows to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
