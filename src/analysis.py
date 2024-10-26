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

    acc = {}

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
        if not acc.get(length):
            acc[length] = []

        # modify to count correlation for CHSH and my test
        if alice_basis == bob_basis:
            if alice_bit == bob_bit:
                acc[length].append(1)
            else:
                acc[length].append(0)

    for length, val in acc.items():
        processed_data["distance"].append(length)
        # binomial distribution estimation (big sample size and p far from 0 or 1 -> Wald interval)
        qber = 1 - (sum(val) / len(val))
        processed_data["QBER"].append(qber)

    print(processed_data)

    return 0
