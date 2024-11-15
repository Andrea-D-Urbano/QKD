from qiskit.visualization import plot_gate_map
from pack_chains import master_chains
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

backend = FakeSherbrooke()

chain = master_chains["ibm_sherbrooke"]

# Create a color map for qubits
total_qubits = backend.configuration().num_qubits
qubit_color = ["#808080"] * total_qubits

for qubit in chain:
    qubit_color[qubit] = "#FF0000"

fig = plot_gate_map(backend, qubit_color=qubit_color)
fig.savefig("img/ibm_sherbrooke_topology_master_chain.png")
