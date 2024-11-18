import pandas as pd
import numpy as np
from scipy.stats import norm, ttest_ind, ks_2samp


def update_data(data, counts):

    for idx, dat in enumerate(data):
        (
            length,
            alice_basis,
            bob_basis,
            alice_bit,
            bob_bit,
            virtual_qb,
            cl_bit,
            circuit_idx,
        ) = dat
        bob_bit = int(list(counts[circuit_idx])[0][::-1][virtual_qb])
        data[idx][4] = bob_bit
        if alice_bit == None:
            alice_bit = int(list(counts[circuit_idx])[0][::-1][virtual_qb - length])
            data[idx][3] = alice_bit

    return data


def process_data(data):

    processed_data = {
        "distance": [],
        "QBER": [],
        "D_QBER": [],
        "CHSH": [],
        "D_CHSH": [],
    }

    # accumulation dictionaries
    acc_qber = {}
    acc_chsh = {}

    for (
        length,
        alice_basis,
        bob_basis,
        alice_bit,
        bob_bit,
        virtual_qb,
        cl_bit,
        circuit_idx,
    ) in data:
        if not acc_qber.get(length):
            acc_qber[length] = []
        if not acc_chsh.get(length):
            acc_chsh[length] = {"XX": [0, 0], "XZ": [0, 0], "ZX": [0, 0], "ZZ": [0, 0]}

        # accumulate results
        if alice_basis == bob_basis:
            if alice_bit == bob_bit:
                acc_qber[length].append(1)
            else:
                acc_qber[length].append(0)

        if alice_basis == "X" and bob_basis == "X":
            if alice_bit == bob_bit:
                acc_chsh[length]["XX"][0] += 1
            else:
                acc_chsh[length]["XX"][0] -= 1

            acc_chsh[length]["XX"][1] += 1

        if alice_basis == "X" and bob_basis == "Z":
            if alice_bit == bob_bit:
                acc_chsh[length]["XZ"][0] += 1
            else:
                acc_chsh[length]["XZ"][0] -= 1

            acc_chsh[length]["XZ"][1] += 1

        if alice_basis == "Z" and bob_basis == "X":
            if alice_bit == bob_bit:
                acc_chsh[length]["ZX"][0] += 1
            else:
                acc_chsh[length]["ZX"][0] -= 1

            acc_chsh[length]["ZX"][1] += 1

        if alice_basis == "Z" and bob_basis == "Z":
            if alice_bit == bob_bit:
                acc_chsh[length]["ZZ"][0] += 1
            else:
                acc_chsh[length]["ZZ"][0] -= 1

            acc_chsh[length]["ZZ"][1] += 1

    for length, val in acc_qber.items():
        processed_data["distance"].append(length)
        # binomial distribution estimation (big sample size and p far from 0 or 1 -> Wald interval)
        qber = 1 - (sum(val) / len(val))
        processed_data["QBER"].append(qber)
        processed_data["D_QBER"].append(float(np.sqrt((qber * (1 - qber)) / len(val))))

    for length, correlations in acc_chsh.items():
        S = 0
        var_S = 0
        for key, val in correlations.items():
            sum_product, counts = val
            expval = sum_product / counts if counts != 0 else 0
            # Var(x)=⟨x^2⟩−⟨x⟩^2
            # propagatioin errors
            if key == "XZ":
                S -= expval
            else:
                S += expval
            var_S += (1 - expval**2) / counts if counts != 0 else 0

        processed_data["CHSH"].append(S)
        processed_data["D_CHSH"].append(float(np.sqrt(var_S)))

    print(processed_data)

    return 0


def process_data_pandas(data):

    # Convert data into a DataFrame
    columns = [
        "length",
        "alice_basis",
        "bob_basis",
        "alice_bit",
        "bob_bit",
        "virtual_qb",
        "cl_bit",
        "circuit_idx",
    ]
    df = pd.DataFrame(data, columns=columns)

    # Function to compute Wald confidence interval
    def wald_error(p, n):
        if n == 0 or np.isnan(p):
            return (np.nan, np.nan)
        margin = np.sqrt((p * (1 - p)) / n)
        return margin

    # Group by length and calculate quantities
    results = []
    for length, group in df.groupby("length"):
        # total = len(group)

        # 1. QUBER
        same_basis = group[group["alice_basis"] == group["bob_basis"]]
        mismatched = (same_basis["alice_bit"] != same_basis["bob_bit"]).sum()
        quber = mismatched / len(same_basis) if len(same_basis) > 0 else np.nan
        quber_error = (
            wald_error(quber, len(same_basis)) if len(same_basis) > 0 else np.nan
        )

        # 2. CHSH
        def correlation(df_subset):
            if len(df_subset) == 0:
                return np.nan
            p_equal = (df_subset["alice_bit"] == df_subset["bob_bit"]).mean()
            return 2 * p_equal - 1

        e_xx = correlation(
            group[(group["alice_basis"] == "X") & (group["bob_basis"] == "X")]
        )
        e_xz = correlation(
            group[(group["alice_basis"] == "X") & (group["bob_basis"] == "Z")]
        )
        e_zx = correlation(
            group[(group["alice_basis"] == "Z") & (group["bob_basis"] == "X")]
        )
        e_zz = correlation(
            group[(group["alice_basis"] == "Z") & (group["bob_basis"] == "Z")]
        )
        chsh = abs(e_xx - e_xz) + abs(e_zx + e_zz)

        # Error for CHSH: propagate variance assuming independence
        def variance_term(corr):
            return 0 if np.isnan(corr) else (1 - corr**2) / len(group)

        chsh_variance = (
            variance_term(e_xx)
            + variance_term(e_xz)
            + variance_term(e_zx)
            + variance_term(e_zz)
        )
        chsh_error = np.sqrt(chsh_variance)

        # 3. Fractions
        fractions = {}
        errors = {}
        for person, basis in [
            ("alice", "X"),
            ("alice", "Z"),
            ("bob", "X"),
            ("bob", "Z"),
        ]:
            sub_group = group[group[f"{person}_basis"] == basis]
            fraction = (
                (sub_group[f"{person}_bit"] == 1).mean()
                if len(sub_group) > 0
                else np.nan
            )
            fraction_error = (
                wald_error(fraction, len(sub_group)) if len(sub_group) > 0 else np.nan
            )
            fractions[f"{person[0].upper()}{basis}"] = fraction
            errors[f"{person[0].upper()}{basis}_error"] = fraction_error

        for ab in ["X", "Z"]:
            for bb in ["X", "Z"]:
                sub_group = group[
                    (group["alice_basis"] == ab) & (group["bob_basis"] == bb)
                ]
                fraction = (
                    ((sub_group["alice_bit"] == 1) & (sub_group["bob_bit"] == 1)).mean()
                    if len(sub_group) > 0
                    else np.nan
                )
                fraction_error = (
                    wald_error(fraction, len(sub_group))
                    if len(sub_group) > 0
                    else np.nan
                )
                fractions[f"{ab}{bb}"] = fraction
                errors[f"{ab}{bb}_error"] = fraction_error

        # explored quantities
        quantities = compute_quantities(fractions, errors)

        # Store results
        results.append(
            {
                "length": length,
                "QUBER": quber,
                "QUBER_error": quber_error,
                "CHSH": chsh,
                "CHSH_error": chsh_error,
                **quantities,
            }
        )

    # Convert results to DataFrame
    result_df = pd.DataFrame(results)

    return result_df


def compute_quantities(fractions, errors):
    # Constants
    expected = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.5])
    uncorrelated_surface = lambda a0, a1, c0, c1: np.array(
        [a0, a1, c0, c1, a0 * c0, a0 * c1, a1 * c0, a1 * c1]
    )
    normalization = np.linalg.norm(expected - uncorrelated_surface(*expected[:4]))

    observed = np.array(list(fractions.values()))
    errors = np.array(list(errors.values()))

    # 1. Norm of Expected Minus Observed Point
    norm_diff = np.linalg.norm(observed - expected)

    # 2. Norm of Expected Minus Observed with Error Normalization
    norm_diff_normalized = np.sqrt(np.sum(((observed - expected) / errors) ** 2))

    # 3. Distance to the Uncorrelated Surface with Fixed Parameters
    a0, a1, c0, c1 = observed[:4]  # Use observed parameters for the surface
    surface_point = uncorrelated_surface(a0, a1, c0, c1)
    # add as normalization the distance between expected and surface?
    distance_to_surface = np.linalg.norm(observed - surface_point) / normalization

    # 4. Gaussian Overlap (Separability Test)
    combined_variance = np.sum(errors**2)
    overlap = norm.cdf(norm_diff / np.sqrt(combined_variance))

    return {
        "Norm of Expected Minus Observed Point": norm_diff,
        "Norm of Expected Minus Observed with Error Normalization": norm_diff_normalized,
        "Distance to Uncorrelated Surface": distance_to_surface,
        "Gaussian Overlap": overlap,
    }
