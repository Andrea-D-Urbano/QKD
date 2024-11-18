import os
import pickle
import matplotlib.pyplot as plt
import numpy as np

# Load the data
data_path = "data/processed_data.pkl"
output_folder = "img/"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load the dataframe
with open(data_path, "rb") as f:
    df = pickle.load(f)

# List of columns to plot (excluding error columns)
columns_to_plot = [
    "QUBER",
    "CHSH",
    "Norm of Expected Minus Observed Point",
    "Norm of Expected Minus Observed with Error Normalization",
    "Distance to Uncorrelated Surface",
    "Gaussian Overlap",
]

# Plot each column vs length
for column in columns_to_plot:
    plt.figure(figsize=(8, 6))
    plt.plot(df["length"], df[column], marker="o", linestyle="-", label=column)
    plt.xlabel("Length")
    plt.ylabel(column)
    plt.title(f"{column} vs Length")
    plt.grid(alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{column}_vs_length.png"))
    plt.close()

# Plot QUBER with error bars
plt.figure(figsize=(8, 6))
plt.errorbar(
    df["length"],
    df["QUBER"],
    yerr=df["QUBER_error"],
    fmt="o-",
    label="QUBER",
    capsize=4,
)
plt.xlabel("Length")
plt.ylabel("QUBER")
plt.title("QUBER vs Length with Error Bars")
plt.grid(alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "QUBER_with_error.png"))
plt.close()

# Plot CHSH with error bars
plt.figure(figsize=(8, 6))
plt.errorbar(
    df["length"], df["CHSH"], yerr=df["CHSH_error"], fmt="o-", label="CHSH", capsize=4
)
plt.xlabel("Length")
plt.ylabel("CHSH")
plt.title("CHSH vs Length with Error Bars")
plt.grid(alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "CHSH_with_error.png"))
plt.close()
