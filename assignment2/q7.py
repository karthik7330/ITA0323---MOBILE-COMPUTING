
import random
import math
import csv

USERS = 8
SUBCARRIERS = 64
REALISATIONS = 1000
MINIMUM = 4
SNR = 10

def calculate_rate(gain):
    return math.log2(1 + SNR * gain)


def calculate_fairness(values):
    total = 0
    squares = 0

    for value in values:
        total += value
        squares += value * value

    return (total * total) / (USERS * squares)


def original_scheduler(gains):

    throughput = [0.0] * USERS
    count = [0] * USERS
    comparisons = 0

    for n in range(SUBCARRIERS):

        best_user = 0

        for u in range(1, USERS):
            comparisons += 1

            if gains[u][n] > gains[best_user][n]:
                best_user = u

        throughput[best_user] += calculate_rate(
            gains[best_user][n]
        )

        count[best_user] += 1

    return throughput, count, comparisons


def fair_scheduler(gains, realisation):

    throughput = [0.0] * USERS
    count = [0] * USERS
    assigned = [False] * SUBCARRIERS
    comparisons = 0

    start = realisation % USERS

    # Stage 1: Minimum four subcarriers per user

    for step in range(USERS):

        user = (start + step) % USERS

        for q in range(MINIMUM):

            best_n = -1
            best_gain = -1

            for n in range(SUBCARRIERS):

                if not assigned[n]:

                    comparisons += 1

                    if gains[user][n] > best_gain:
                        best_gain = gains[user][n]
                        best_n = n

            assigned[best_n] = True
            count[user] += 1

            throughput[user] += calculate_rate(best_gain)

    # Stage 2: Assign remaining subcarriers

    for n in range(SUBCARRIERS):

        if not assigned[n]:

            best_user = 0

            for u in range(1, USERS):

                comparisons += 1

                if gains[u][n] > gains[best_user][n]:
                    best_user = u

            count[best_user] += 1

            throughput[best_user] += calculate_rate(
                gains[best_user][n]
            )

    return throughput, count, comparisons


def main():

    original_total = 0
    redesigned_total = 0

    original_fairness = 0
    redesigned_fairness = 0

    original_zero = 0
    redesigned_zero = 0

    original_comparisons = 0
    redesigned_comparisons = 0

    original_minimum = 0
    redesigned_minimum = 0

    with open(
        "Q7_Validation_Results.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Realisation",
            "Method",
            "Sum_Throughput",
            "Jain_Fairness",
            "Minimum_User_Throughput",
            "Zero_Allocation_Users",
            "Channel_Comparisons"
        ])

        for r in range(REALISATIONS):

            rng = random.Random(2026 + r)

            gains = []

            for u in range(USERS):

                user_gains = []

                for n in range(SUBCARRIERS):
                    user_gains.append(
                        rng.expovariate(1.0)
                    )

                gains.append(user_gains)

            old, old_count, old_comp = original_scheduler(gains)

            new, new_count, new_comp = fair_scheduler(
                gains, r
            )

            old_sum = sum(old)
            new_sum = sum(new)

            old_fair = calculate_fairness(old)
            new_fair = calculate_fairness(new)

            old_min = min(old)
            new_min = min(new)

            old_zero = old_count.count(0)
            new_zero = new_count.count(0)

            original_total += old_sum
            redesigned_total += new_sum

            original_fairness += old_fair
            redesigned_fairness += new_fair

            original_minimum += old_min
            redesigned_minimum += new_min

            original_zero += old_zero
            redesigned_zero += new_zero

            original_comparisons += old_comp
            redesigned_comparisons += new_comp

            writer.writerow([
                r + 1,
                "Original",
                old_sum,
                old_fair,
                old_min,
                old_zero,
                old_comp
            ])

            writer.writerow([
                r + 1,
                "Redesigned",
                new_sum,
                new_fair,
                new_min,
                new_zero,
                new_comp
            ])

    print("AVERAGE RESULTS")

    print(
        "Original Throughput:",
        round(original_total / REALISATIONS, 3)
    )

    print(
        "Redesigned Throughput:",
        round(redesigned_total / REALISATIONS, 3)
    )

    print(
        "Original Fairness:",
        round(original_fairness / REALISATIONS, 4)
    )

    print(
        "Redesigned Fairness:",
        round(redesigned_fairness / REALISATIONS, 4)
    )

    print(
        "Original Minimum User Throughput:",
        round(original_minimum / REALISATIONS, 3)
    )

    print(
        "Redesigned Minimum User Throughput:",
        round(redesigned_minimum / REALISATIONS, 3)
    )

    print(
        "Original Zero Allocations:",
        original_zero
    )

    print(
        "Redesigned Zero Allocations:",
        redesigned_zero
    )

    print(
        "Original Comparisons:",
        original_comparisons / REALISATIONS
    )

    print(
        "Redesigned Comparisons:",
        redesigned_comparisons / REALISATIONS
    )


main()
