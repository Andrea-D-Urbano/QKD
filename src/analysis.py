from numpy import sqrt


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
        if not alice_bit:
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
        processed_data["D_QBER"].append(float(sqrt((qber * (1 - qber)) / len(val))))

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
        processed_data["D_CHSH"].append(float(sqrt(var_S)))

    print(processed_data)

    return 0
