import random
import math

BITS = 5000
CODE_LENGTHS = [8, 16, 64]
USER_COUNTS = [2, 4, 8]
NOISE = 0.5

def make_walsh(n):
    matrix = [[1]]

    while len(matrix) < n:
        old = matrix
        matrix = []

        for row in old:
            matrix.append(row + row)

        for row in old:
            matrix.append(row + [-x for x in row])

    return matrix


def simulate(L, users, mode):
    mode_number = {
        "walsh": 1,
        "random": 2,
        "nearfar_ideal": 3,
        "nearfar_offset": 4
    }

    rng = random.Random(
        42 + L * 100 + users * 10 + mode_number[mode]
    )

    if mode == "random":
        codes = []

        for u in range(users):
            code = []

            for k in range(L):
                code.append(rng.choice([-1, 1]))

            codes.append(code)

    else:
        codes = make_walsh(L)[:users]

    errors = 0
    previous_bits = []

    for u in range(users):
        previous_bits.append(rng.choice([-1, 1]))

    for b in range(BITS):

        bits = []

        for u in range(users):
            bits.append(rng.choice([-1, 1]))

        received = []

        for k in range(L):
            received.append(0.0)

        for u in range(users):

            amplitude = 1.0

            if mode in ["nearfar_ideal", "nearfar_offset"]:
                if u == 1:
                    amplitude = math.sqrt(10)

            code = codes[u]

            for k in range(L):

                if mode == "nearfar_offset" and u == 1:

                    if k == 0:
                        chip = previous_bits[u] * code[L - 1]
                    else:
                        chip = bits[u] * code[k - 1]

                else:
                    chip = bits[u] * code[k]

                received[k] += amplitude * chip

        for k in range(L):
            received[k] += rng.gauss(0, NOISE)

        decision = 0

        for k in range(L):
            decision += received[k] * codes[0][k]

        detected = 1

        if decision < 0:
            detected = -1

        if detected != bits[0]:
            errors += 1

        previous_bits = bits

    ber = errors / BITS

    return errors, ber


def correlation(codes):
    maximum = 0

    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):

            total = 0

            for k in range(len(codes[i])):
                total += codes[i][k] * codes[j][k]

            value = abs(total) / len(codes[i])

            if value > maximum:
                maximum = value

    return maximum


modes = [
    "walsh",
    "random",
    "nearfar_ideal",
    "nearfar_offset"
]

for L in CODE_LENGTHS:

    print("\nCODE LENGTH:", L)
    print("PROCESSING GAIN:", L)

    for users in USER_COUNTS:

        if users <= L:

            print("\nUsers:", users)

            for mode in modes:

                errors, ber = simulate(L, users, mode)

                print(
                    mode,
                    "Errors:", errors,
                    "BER:", round(ber, 4)
                )

            if users > 1:

                codes = make_walsh(L)[:users]

                print(
                    "Walsh cross-correlation:",
                    correlation(codes)
                )

                random_rng = random.Random(42 + L * 100 + users * 10 + 2)
                random_codes = []
                for u in range(users):
                    code = []
                    for k in range(L):
                        code.append(random_rng.choice([-1, 1]))
                    random_codes.append(code)
                print(
                    "Random-code maximum correlation:",
                    correlation(random_codes)
                )

print("\nUSER CAPACITY ESTIMATION")
print("Target BER: 1%")
for L in CODE_LENGTHS:
    print("\nCode length:", L)
    for users in [2, 4, 8, 16, 32, 64]:
        if users <= L:
            errors, ber = simulate(L, users, "random")
            if ber <= 0.01:
                print(
                    users,
                    "users: ACCEPTED",
                    "BER:", round(ber * 100, 2), "%"
                )
            else:
                print(
                    users,
                    "users: EXCEEDS TARGET",
                    "BER:", round(ber * 100, 2), "%"
                )