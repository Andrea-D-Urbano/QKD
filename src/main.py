from pack_chains import master_chains
from analysis import update_data, process_data
from simulation import generate_circuits, run_simulation
import pickle
import yaml


def main():
    # inizialize parameters (read from config file?)
    with open("config/sim_config.yaml", "r") as file:
        config = yaml.safe_load(file)

    protocol = config["simulation"]["protocol"]
    run_sim = config["simulation"]["run_sim"]
    device = config["simulation"]["device"]
    QPU = config["simulation"]["QPU"]
    lengths = config["simulation"]["lengths"]
    runs = config["simulation"]["runs"]
    draw = config["simulation"]["draw"]

    if run_sim:

        master_chain = master_chains[QPU]

        data, circuits = generate_circuits(
            lengths=lengths,
            runs=runs,
            master_chain=master_chain,
            protocol=protocol,
        )

        with open("data/data.pkl", "wb") as file:
            pickle.dump(data, file)

        run_simulation(
            circuits=circuits, master_chain=master_chain, device=device, draw=draw
        )

    # process: quber, plots, remember a lot of images (circuits and processor, processor with circuits highlighted)
    with open("data/data.pkl", "rb") as file:
        data = pickle.load(file)

    if device:
        with open("data/results_device.pkl", "rb") as file:
            counts = pickle.load(file)
    else:
        with open("data/results_local.pkl", "rb") as file:
            counts = pickle.load(file)

    data = update_data(data, counts)

    process_data(data)


if __name__ == "__main__":
    main()
