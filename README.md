# Quantum Key Distribution (QKD) Protocol Simulation

This repository contains Python scripts for simulating Quantum Key Distribution (QKD) protocols, developed as part of my Ph.D. thesis. The project allows for local or IBM Quantum backend simulations of QKD protocols, including **BB84** and **BBM92**. The simulations use IBM's `ibm_sherbrooke` device noise model for fidelity to real-world conditions. Protocols are tested for various simulated distances using quantum swaps or circuit depth.

## Features

- **Protocols**: Implements BB84, BBM92, and single-qubit BB84 protocols.
- **Simulation Distances**: Uses quantum swaps for BB84, BBM92 or adjusts circuit depth to represent different communication distances for single-qubit BB84.
- **Noise Modeling**: Simulations reflect the noise characteristics of the `ibm_sherbrooke` quantum processor.
- **Circuit Parallelization**: Runs multiple QKD circuits (QKD runs) packed within a single execution to optimize runtime and reduce resource consumption on real quantum hardware.
- **Data Storage**: Saves raw and processed data to `/data` and generated images/plots to `/img`.
- **Configurable**: Custom simulation settings can be specified in `/config/sim_config.yaml`.
- **Image generation**: generate virtual and transpiled circuit figures, as well as backend topology highlighting the "master chain" (for this purpose use the script `plot_master_chain.py`). 

## Setup Instructions

1. **Environment Setup**: 
   - Create a new Python environment with `venv` or `conda` and install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Running on IBM Quantum Backends**:
   - For real-device simulations, create a `.env` file in the root directory with the following line:
     ```bash
     IBMQ_API_TOKEN=your_ibm_api_key
     ```
   - This will enable access to IBM Quantum backends through the API.

3. **Configuration**:
   - Customize simulation parameters in `/config/sim_config.yaml` as needed.

4. **Notes**:
   - For simulations involving deep circuits, avoid generating circuit images due to excessive processing time and poor image quality.
   - Use script `plot_master_chain.py` to generate the image of backend topology highlighting the "master chain". Be sure to have `graphviz` installed.

## Directory Structure

- `/src`: Contains source python files.
- `/data`: Contains raw and processed simulation data.
- `/img`: Stores generated images and plots from the simulations.
- `/config`: Houses the configuration file (`sim_config.yaml`) for customizing simulation parameters.

## Usage

After setting up the environment and configurations, run `/src/main.py`. To generate the image of backend topology highlighting the "master chain" use the script `plot_master_chain.py`. To generate plots use `plot_results.py`.

## License

This project is open-source under the MIT License.
