import os
import pickle
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Function to load data
def load_data(folder):
    data_path = os.path.join(folder, "processed_data.pkl")
    if not os.path.exists(data_path):
        print(f"Warning: No processed data found in {folder}. Skipping.")
        return None
    with open(data_path, "rb") as f:
        return pickle.load(f)


# Function to create plots for a folder
def plot_protocol_metrics(folder, df):

    # Output folder for plots
    output_folder = "img/protocols_metrics/"
    os.makedirs(output_folder, exist_ok=True)

    # Metrics
    right_axis_metrics = [
        "Norm of Expected Minus Observed Point",
        "Distance to Uncorrelated Surface",
        "Gaussian Overlap",
    ]
    left_axis_metrics = ["QUBER", "CHSH"]
    metrics = left_axis_metrics + right_axis_metrics

    # Colors for the metrics
    # colors = ["tab:blue", "lightblue", "tab:green", "lightgreen", "lime"]
    # colors = ["tab:purple", "plum", "mediumpurple", "darkorange", "goldenrod"]
    # colors = ["tab:red", "lightcoral", "firebrick", "darkcyan", "paleturquoise"]
    # colors = ["saddlebrown", "peru", "chocolate", "darkmagenta", "orchid"]
    # colors = ["teal", "darkcyan", "mediumaquamarine", "gold", "khaki"]
    colors = ["mediumaquamarine", "darkcyan", "chocolate", "firebrick", "saddlebrown"]

    folder_name = folder.split("/")[-1]
    fig, host = plt.subplots(figsize=(12, 10))

    # Create parasite axes for left and right metrics
    left_axes = [host.twinx() for _ in range(len(left_axis_metrics))]
    right_axes = [host.twinx() for _ in range(len(right_axis_metrics))]

    # Offset the left parasite axes
    for i, ax in enumerate(left_axes):
        ax.spines["left"].set_position(("outward", 60 * i))
        ax.spines["left"].set_visible(True)
        ax.yaxis.set_ticks_position("left")
        ax.yaxis.set_label_position("left")

    # Offset the right parasite axes
    for i, ax in enumerate(right_axes):
        ax.spines["right"].set_position(("outward", 60 * i))
        ax.spines["right"].set_visible(True)
        ax.yaxis.set_ticks_position("right")
        ax.yaxis.set_label_position("right")

    # Combine all axes
    all_axes = left_axes + right_axes

    # Plot data and customize axes
    lines = []
    for ax, metric, color in zip(all_axes, metrics, colors):
        if metric in df:
            (line,) = ax.plot(
                df["length"],
                df[metric],
                label=metric,
                color=color,
                marker="o",
                linestyle="-",
            )
            ax.set_ylabel(metric, color=color)
            ax.tick_params(axis="y", labelcolor=color)
            ax.yaxis.set_major_locator(MaxNLocator(5))  # Limit number of ticks
            ax.set_ylim(min(df[metric]) * 0.9, max(df[metric]) * 1.1)  # Auto-scale
            lines.append(line)

    # Host axis labels and grid (remove default number and ticks)
    host.set_xlabel("Distance")
    host.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
    host.grid(alpha=0.5)

    # Combine legends
    host.legend(
        lines[::-1],  # Reorder to get the similar shades on the same column
        [line.get_label() for line in lines][::-1],  # Idem
        loc="upper center",  # Place the legend at the top-center of the axes
        bbox_to_anchor=(0.5, -0.07),  # Move it below the plot (y-offset negative)
        fancybox=True,  # Optional: Rounded box
        shadow=True,  # Optional: Add a shadow
        ncol=2,  # Arrange legend entries in two columns
        fontsize=10,
    )

    # Adjust layout
    plt.tight_layout(
        rect=[0, 0.05, 1, 0.95]
    )  # Reserve space: [left, bottom, right, top]

    # Save the plot
    plt.title(f"Metrics Comparison for {folder_name}")
    plt.savefig(os.path.join(output_folder, f"{folder_name}_metrics.png"))
    plt.close()


def plot_metrics_comparison(folder, df_sim, df_device):
    # TODO: scale and legend placement (Id-BB84)
    # Create output folder for comparison plots
    comparison_output_folder = "img/metrics_comparison/"
    os.makedirs(comparison_output_folder, exist_ok=True)

    # Define metric groups for the two plots
    group1_metrics = ["QUBER", "Norm of Expected Minus Observed Point"]
    group2_metrics = [
        "CHSH",
        "Distance to Uncorrelated Surface",
        "Gaussian Overlap",
    ]
    metric_groups = [group1_metrics, group2_metrics]

    # Colors for the metrics
    colors = ["darkcyan", "chocolate", "saddlebrown", "firebrick", "mediumaquamarine"]

    # Loop through metric groups and create plots
    for idx, metrics in enumerate(metric_groups):
        fig, host = plt.subplots(figsize=(12, 10))

        # Create parasite axes for each metric
        axes = [host.twinx() for _ in metrics]

        # Offset axes appropriately
        for i, ax in enumerate(axes):
            if i < len(metrics) // 2:
                ax.spines["left"].set_position(("outward", 60 * i))
                ax.spines["left"].set_visible(True)
                ax.yaxis.set_ticks_position("left")
                ax.yaxis.set_label_position("left")
            else:
                ax.spines["right"].set_position(("outward", 60 * (i - 1)))
                ax.spines["right"].set_visible(True)
                ax.yaxis.set_ticks_position("right")
                ax.yaxis.set_label_position("right")

        # Plot the metrics
        lines = []
        for ax, metric, color in zip(axes, metrics, colors):
            # Plot simulation data (dashed line)
            if metric in df_sim:
                (line_sim,) = ax.plot(
                    df_sim["length"],
                    df_sim[metric],
                    label=f"{metric} (Simulation)",
                    color=color,
                    linestyle="--",
                    marker="o",
                )
                lines.append(line_sim)

            # Plot device data (solid line)
            if metric in df_device:
                (line_dev,) = ax.plot(
                    df_device["length"],
                    df_device[metric],
                    label=f"{metric} (Device)",
                    color=color,
                    linestyle="-",
                    marker="s",
                )
                lines.append(line_dev)

            # Customize axis
            ax.set_ylabel(metric, color=color)
            ax.tick_params(axis="y", labelcolor=color)
            ax.yaxis.set_major_locator(MaxNLocator(5))  # Limit number of ticks
            all_data = []
            if metric in df_sim:
                all_data.extend(df_sim[metric])
            if metric in df_device:
                all_data.extend(df_device[metric])
            if all_data:
                ax.set_ylim(min(all_data) * 0.9, max(all_data) * 1.1)  # Auto-scale

        # Customize host axis
        host.set_xlabel("Distance")
        host.tick_params(
            axis="y", which="both", left=False, right=False, labelleft=False
        )
        host.grid(alpha=0.5)

        # Add title and legend
        plot_title = f"{folder} - Comparison Plot {idx + 1}: " + ", ".join(metrics)
        plt.title(plot_title)
        host.legend(
            lines,
            [line.get_label() for line in lines],
            loc="upper center",  # Place the legend at the top-center of the axes
            bbox_to_anchor=(0.5, -0.07),  # Move it below the plot (y-offset negative)
            fancybox=True,  # Optional: Rounded box
            shadow=True,  # Optional: Add a shadow
            ncol=2,  # Arrange legend entries in two columns
            fontsize=10,
        )

        # Adjust layout and save the plot
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig(
            os.path.join(
                comparison_output_folder,
                f"{folder}_comparison_plot_{idx + 1}.png",
            )
        )
        plt.close()


def plot_protocols_comparison(protocol1, protocol2, df1_sim, df1_dev, df2_sim, df2_dev):
    # TODO: scale and legend placement
    # Output folder for protocols comparison
    protocols_output_folder = "img/protocols_comparison/"
    os.makedirs(protocols_output_folder, exist_ok=True)

    # Define metric groups for comparison
    group1_metrics = ["QUBER", "Norm of Expected Minus Observed Point"]
    group2_metrics = ["CHSH", "Distance to Uncorrelated Surface"]
    metric_groups = [group1_metrics, group2_metrics]

    # Data sources for comparison
    data_types = [("Simulation", df1_sim, df2_sim), ("Device", df1_dev, df2_dev)]

    # Colors for protocols and their shades
    protocol_colors = {
        protocol1: ["darkcyan", "mediumaquamarine"],
        protocol2: ["chocolate", "saddlebrown"],
    }

    # Marker shapes for metrics
    markers = ["o", "s", "^", "D", "P"]

    # Create plots for each metric group and data type
    for idx, metrics in enumerate(metric_groups):
        for data_type, df1, df2 in data_types:
            fig, host = plt.subplots(figsize=(12, 10))

            # Create parasite axes for each metric
            axes = [host.twinx() for _ in metrics]

            # Offset parasite axes for readability
            for i, ax in enumerate(axes):
                if i < len(metrics) // 2:
                    ax.spines["left"].set_position(("outward", 60 * i))
                    ax.spines["left"].set_visible(True)
                    ax.yaxis.set_ticks_position("left")
                    ax.yaxis.set_label_position("left")
                else:
                    ax.spines["right"].set_position(("outward", 60 * (i - 1)))
                    ax.spines["right"].set_visible(True)
                    ax.yaxis.set_ticks_position("right")
                    ax.yaxis.set_label_position("right")

            # Plot metrics for both protocols
            lines = []
            for ax, metric, marker1, marker2 in zip(
                axes, metrics, markers[: len(metrics)], markers[len(metrics) :]
            ):
                # Protocol 1 - Data for current metric
                if metric in df1:
                    color1 = protocol_colors[protocol1][metrics.index(metric) % 2]
                    (line1,) = ax.plot(
                        df1["length"],
                        df1[metric],
                        label=f"{metric} ({protocol1})",
                        color=color1,
                        linestyle="-",  # Always solid
                        marker=marker1,
                    )
                    lines.append(line1)

                # Protocol 2 - Data for current metric
                if metric in df2:
                    color2 = protocol_colors[protocol2][metrics.index(metric) % 2]
                    (line2,) = ax.plot(
                        df2["length"],
                        df2[metric],
                        label=f"{metric} ({protocol2})",
                        color=color2,
                        linestyle="-",  # Always solid
                        marker=marker2,
                    )
                    lines.append(line2)

                # Customize axis for metric
                ax.set_ylabel(metric, color="gray")
                ax.tick_params(axis="y", labelcolor="gray")
                ax.yaxis.set_major_locator(MaxNLocator(5))  # Limit number of ticks
                all_data = []
                if metric in df1:
                    all_data.extend(df1[metric])
                if metric in df2:
                    all_data.extend(df2[metric])
                if all_data:
                    ax.set_ylim(min(all_data) * 0.9, max(all_data) * 1.1)  # Auto-scale

            # Customize host axis
            host.set_xlabel("Distance")
            host.tick_params(
                axis="y", which="both", left=False, right=False, labelleft=False
            )
            host.grid(alpha=0.5)

            # Add title and legend
            plot_title = (
                f"{protocol1} vs {protocol2} - {data_type} Comparison: "
                + ", ".join(metrics)
            )
            plt.title(plot_title)
            host.legend(
                lines,
                [line.get_label() for line in lines],
                loc="upper center",  # Place the legend at the top-center of the axes
                bbox_to_anchor=(0.5, -0.07),  # Move it below the plot
                fancybox=True,  # Optional: Rounded box
                shadow=True,  # Optional: Add a shadow
                ncol=2,  # Arrange legend entries in two columns
                fontsize=10,
            )

            # Adjust layout and save the plot
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            plt.savefig(
                os.path.join(
                    protocols_output_folder,
                    f"{protocol1}_vs_{protocol2}_{data_type.lower()}_plot_{idx + 1}.png",
                )
            )
            plt.close()


if __name__ == "__main__":

    folders = [
        "data/BB84",
        "data/BB84-device",
        "data/BB84-device2",
        "data/BBM92",
        "data/BBM92-device",
        "data/BBM92-device2",
        "data/Id-BB84",
        "data/Id-BB84-device",
    ]

    # plot protocols metrics
    for folder in folders:
        df = load_data(folder)
        if df is not None:
            plot_protocol_metrics(folder, df)

    # plot metrics comparisons
    for protocol in ["BB84", "BBM92", "Id-BB84"]:
        df_sim = load_data(f"data/{protocol}")
        df_device = load_data(f"data/{protocol}-device")
        if df_sim is not None and df_device is not None:
            # Call the new comparison plotting function
            plot_metrics_comparison(protocol, df_sim, df_device)

    # plot protocols comparison
    protocols_pairs = [
        ("BB84", "BBM92"),
        ("BB84", "Id-BB84"),
    ]

    for protocol1, protocol2 in protocols_pairs:
        # Load data for both protocols
        df1_sim = load_data(f"data/{protocol1}")
        df1_dev = load_data(f"data/{protocol1}-device")
        df2_sim = load_data(f"data/{protocol2}")
        df2_dev = load_data(f"data/{protocol2}-device")

        # Ensure all data is available
        if (
            df1_sim is not None
            and df1_dev is not None
            and df2_sim is not None
            and df2_dev is not None
        ):
            # Call the comparison plotting function
            plot_protocols_comparison(
                protocol1, protocol2, df1_sim, df1_dev, df2_sim, df2_dev
            )
