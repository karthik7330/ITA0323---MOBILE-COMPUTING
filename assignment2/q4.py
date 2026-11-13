
import random
import math
import csv

USERS = 8
SUBCARRIERS = 64
REALISATIONS = 1000
SNR = 10

def calculate_rate(gain):
    return math.log2(1 + SNR * gain)


def calculate_fairness(throughput):
    total = 0
    squares = 0

    for value in throughput:
        total += value
        squares += value * value

    if squares == 0:
        return 0

    return (total * total) / (USERS * squares)


def verify_orthogonality():
    print("ORTHOGONALITY VERIFICATION")

    for k in range(3):
        for m in range(3):

            real = 0
            imaginary = 0

            for n in range(SUBCARRIERS):
                angle = 2 * math.pi * (k - m) * n / SUBCARRIERS

                real += math.cos(angle)
                imaginary += math.sin(angle)

            real = real / SUBCARRIERS
            imaginary = imaginary / SUBCARRIERS

            magnitude = math.sqrt(
                real * real + imaginary * imaginary
            )

            print(k, m, round(magnitude, 6))


def simulate():
    methods = ["Fixed", "Interleaved", "Channel_Aware"]

    total_throughput = {}

    for method in methods:
        total_throughput[method] = [0.0] * USERS

    fairness_total = {}
    sum_total = {}

    for method in methods:
        fairness_total[method] = 0
        sum_total[method] = 0

    with open("Q4_Experimental_Results.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Realisation", "Method", "Sum_Throughput",
            "Jain_Index",
            "User1", "User2", "User3", "User4",
            "User5", "User6", "User7", "User8"
        ])

        for r in range(REALISATIONS):

            rng = random.Random(2026 + r)

            gains = []

            for u in range(USERS):
                user_gains = []

                for n in range(SUBCARRIERS):
                    user_gains.append(rng.expovariate(1.0))

                gains.append(user_gains)

            for method in methods:

                throughput = [0.0] * USERS

                for n in range(SUBCARRIERS):

                    if method == "Fixed":
                        user = n // 8

                    elif method == "Interleaved":
                        user = n % USERS

                    else:
                        user = 0
                        best_gain = gains[0][n]

                        for u in range(1, USERS):
                            if gains[u][n] > best_gain:
                                best_gain = gains[u][n]
                                user = u

                    throughput[user] += calculate_rate(
                        gains[user][n]
                    )

                total = 0

                for value in throughput:
                    total += value

                fairness = calculate_fairness(throughput)

                for u in range(USERS):
                    total_throughput[method][u] += throughput[u]

                fairness_total[method] += fairness
                sum_total[method] += total

                writer.writerow([
                    r + 1, method, total, fairness
                ] + throughput)

    print("\nFINAL RESULTS")

    for method in methods:

        print("\nMethod:", method)

        print(
            "Average sum throughput:",
            round(sum_total[method] / REALISATIONS, 3)
        )

        print(
            "Average Jain fairness:",
            round(fairness_total[method] / REALISATIONS, 4)
        )

        print("Average per-user throughput:")

        for u in range(USERS):
            print(
                "User", u + 1,
                round(
                    total_throughput[method][u] / REALISATIONS,
                    3
                )
            )


verify_orthogonality()
simulate()
