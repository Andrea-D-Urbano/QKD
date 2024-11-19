from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    transpile,
)
from qiskit.transpiler import Layout
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import Sampler
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.visualization import circuit_drawer
import matplotlib.pyplot as plt
from math import ceil
import random
from dotenv import load_dotenv
import os
import pickle
import gc


def generate_circuits(lengths, runs, master_chain, protocol, QPU="ibm_sherbrooke"):

    max_circuit_len = len(master_chain)
    if protocol != "Id-BB84":
        assert all(
            l <= max_circuit_len - 1 for l in lengths
        ), f"max len must be at most {max_circuit_len-1}"

    # (length, alice_basis, bob_basis, alice_bit, bob_bit, virtual_qubit_measured, classic_bit , circuit_index)
    data = []
    circuits = []

    qr = QuantumRegister(len(master_chain))
    if protocol == "Id-BB84":
        if QPU == "ibm_sherbrooke":
            # use all device
            qr_idBB84 = QuantumRegister(127)
        else:
            raise Exception("QPU unknown.")
    circuit_idx = 0

    for length in lengths:
        # cr = ClassicalRegister(len(master_chain) // length)
        if protocol == "Id-BB84":
            qc = QuantumCircuit(qr_idBB84)
        else:
            qc = QuantumCircuit(qr)
        current_qb = 0
        cl_bit = 0

        for r in range(runs):
            # simulate choices: remember total choices
            alice_basis = random.choice(["X", "Z"])
            bob_basis = random.choice(["X", "Z"])

            if protocol == "BB84":

                alice_bit = random.choice([0, 1])

                if alice_bit == 1:
                    qc.x(current_qb)  # Prepare |1⟩ in Z basis
                if alice_basis == "X":
                    qc.h(current_qb)  # Prepare |+⟩ or |-⟩

                for qb in range(current_qb, current_qb + length):
                    qc.swap(qb, qb + 1)
                current_qb = current_qb + length

                if bob_basis == "X":
                    qc.h(current_qb)  # Apply H-gate if Bob is measuring in the X basis

                data.append(
                    [
                        length,
                        alice_basis,
                        bob_basis,
                        alice_bit,
                        None,
                        current_qb,
                        cl_bit,
                        circuit_idx,
                    ]
                )

            elif protocol == "BBM92":

                # prepare entangled state
                qc.h(current_qb)
                qc.cx(current_qb, current_qb + 1)

                # Alice measurement basis choice
                if alice_basis == "X":
                    qc.h(current_qb)

                # transport entangled state
                for qb in range(current_qb + 1, current_qb + length):
                    qc.swap(qb, qb + 1)

                current_qb = current_qb + length

                # Bob measurement basis choice
                if bob_basis == "X":
                    qc.h(current_qb)

                data.append(
                    [
                        length,
                        alice_basis,
                        bob_basis,
                        None,
                        None,
                        current_qb,
                        cl_bit,
                        circuit_idx,
                    ]
                )

            elif protocol == "Id-BB84":

                alice_bit = random.choice([0, 1])

                if alice_bit == 1:
                    qc.x(current_qb)  # Prepare |1⟩ in Z basis
                if alice_basis == "X":
                    qc.h(current_qb)  # Prepare |+⟩ or |-⟩

                # vary depth
                for _ in range(length):
                    qc.id(current_qb)

                if bob_basis == "X":
                    qc.h(current_qb)  # Apply H-gate if Bob is measuring in the X basis

                data.append(
                    [
                        length,
                        alice_basis,
                        bob_basis,
                        alice_bit,
                        None,
                        current_qb,
                        cl_bit,
                        circuit_idx,
                    ]
                )

            else:
                raise Exception("Protocol unknown.")

            if protocol != "Id-BB84":
                # if a new chain would overflow the circuit, reset
                if current_qb + length + 1 > max_circuit_len - 1:
                    current_qb = 0
                    cl_bit = 0
                    circuit_idx += 1
                    qc.measure_all()
                    circuits.append(qc)
                    qc = QuantumCircuit(qr)
                else:
                    current_qb += 1
                    cl_bit += 1
            else:
                current_qb += 1
                cl_bit += 1
                if QPU == "ibm_sherbrooke":
                    if current_qb >= 127:
                        current_qb = 0
                        cl_bit = 0
                        circuit_idx += 1
                        qc.measure_all()
                        circuits.append(qc)
                        qc = QuantumCircuit(qr_idBB84)
                else:
                    raise Exception("QPU unknown.")

        # if there is still a circuit not written
        if len(circuits) != data[-1][-1] + 1:
            circuit_idx += 1
            qc.measure_all()
            circuits.append(qc)

    assert len(circuits) == data[-1][-1] + 1

    print("Circuit generation successful.")

    return data, circuits


def circuit_generator(circuits, backend, custom_layout):
    for circ in circuits:
        yield transpile(
            circ,
            backend=backend,
            initial_layout=custom_layout,
            optimization_level=0,
        )


def run_simulation(
    circuits, master_chain, device=False, QPU="ibm_sherbrooke", draw=False
):

    if circuits[0].num_qubits == len(master_chain):
        custom_layout = Layout.from_intlist(master_chain, circuits[0].qregs[0])
    else:
        # Id-BB84
        custom_layout = None

    if draw:
        circuit_drawer(circuits[0], output="mpl", fold=150).savefig("img/circuit.png")
        circuit_drawer(
            transpile(
                circuits[0],
                backend=backend,
                initial_layout=custom_layout,
                optimization_level=0,
            ),
            output="mpl",
            fold=150,
        ).savefig("img/transpiled_circuit.png")

    # Use Sampler for simulation
    if not device:
        # define simulator
        backend = FakeSherbrooke()

        # method = 'automatic', 'statevector', 'density_matrix', 'stabilizer', 'matrix_product_state', 'extended_stabilizer', 'unitary', 'superop', 'tensor_network'
        noise_model = NoiseModel.from_backend(backend)
        simulator = AerSimulator(
            method="matrix_product_state", noise_model=noise_model, device="CPU"
        )

        list_count = []
        num_circuits = len(circuits)
        for progress, transpiled_qc in zip(
            range(num_circuits), circuit_generator(circuits, backend, custom_layout)
        ):
            if progress % (ceil(num_circuits / 30)) == 0:
                print(
                    f"{100*progress/num_circuits:.2f}% completed: {progress} circuits run over {num_circuits}."
                )
                # force garbage collection
                gc.collect()
            result = simulator.run(transpiled_qc, shots=1).result()
            counts = result.get_counts()
            list_count.append(counts)
            del transpiled_qc

        print("100.00% Simulation completed.")

        with open("data/results_local.pkl", "wb") as file:
            pickle.dump(list_count, file)

    else:
        # load account and select real backend

        load_dotenv()  # Load environment variables from .env file
        api_token = os.getenv("IBMQ_API_TOKEN")
        if api_token:
            service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)
        else:
            raise Exception("Unable to find API token")
        # service = QiskitRuntimeService()
        backend = service.backend(QPU)
        # Transpile circuits for the simulator
        transpiled_circuits = transpile(
            circuits,
            backend=backend,
            initial_layout=custom_layout,
            optimization_level=0,
        )

        sampler = Sampler(backend)
        job = sampler.run(transpiled_circuits, shots=1)
        result = job.result()

        with open("data/raw_results_device.pkl", "wb") as file:
            pickle.dump(result, file)

        # Print results
        list_count = []
        for circ_res in result:
            for val in circ_res.data.values():
                list_count.append(val.get_counts())

        with open("data/results_device.pkl", "wb") as file:
            pickle.dump(list_count, file)

    return 0
