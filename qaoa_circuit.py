
from qiskit import QuantumCircuit

# Four assets mean four qubits.
num_assets = 4

# Create a quantum circuit with four qubits
# and four classical bits to store measurements.
qc = QuantumCircuit(num_assets, num_assets)

# Put every qubit into superposition.
for qubit in range(num_assets):
    qc.h(qubit)

# Measure each qubit and store its result.
qc.measure(range(num_assets), range(num_assets))

# Display the circuit.
print(qc.draw())
