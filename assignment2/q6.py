
weights = [25, 20, 20, 20, 15]

techniques = [
    "FDMA", "TDMA", "CDMA", "OFDMA", "SDMA"
]

deployments = {
    "Cellular Voice": [
        [3, 3, 4, 2, 3],
        [4, 3, 3, 3, 4],
        [4, 4, 4, 4, 4],
        [5, 4, 4, 5, 4],
        [4, 3, 4, 3, 3]
    ],

    "Tactical Link": [
        [2, 2, 4, 2, 3],
        [3, 3, 3, 3, 4],
        [4, 5, 4, 4, 3],
        [4, 3, 4, 4, 4],
        [3, 3, 4, 3, 3]
    ],

    "Stadium Downlink": [
        [2, 3, 3, 2, 3],
        [3, 3, 3, 3, 4],
        [3, 3, 3, 3, 3],
        [5, 4, 5, 5, 4],
        [4, 4, 4, 4, 3]
    ],

    "Sensor Network": [
        [2, 3, 3, 2, 3],
        [4, 4, 4, 5, 4],
        [4, 4, 4, 4, 3],
        [4, 3, 4, 4, 4],
        [3, 3, 3, 3, 3]
    ]
}


def calculate_score(rating, weight):
    total = 0

    for i in range(5):
        total += rating[i] * weight[i]

    return total / sum(weight)


for deployment in deployments:

    print("\nDEPLOYMENT:", deployment)

    scores = []

    for i in range(5):

        score = calculate_score(
            deployments[deployment][i],
            weights
        )

        scores.append(score)

        print(
            techniques[i],
            "Score:", round(score, 2)
        )

    best = 0

    for i in range(1, 5):
        if scores[i] > scores[best]:
            best = i

    print(
        "Recommended:",
        techniques[best]
    )



print("\nINDIVIDUAL WEIGHT SENSITIVITY ANALYSIS")

for deployment in deployments:

    print("\nDEPLOYMENT:", deployment)

    for criterion in range(5):

        for factor in [0.8, 1.2]:

            new_weights = weights.copy()
            new_weights[criterion] *= factor

            scores = []

            for i in range(5):
                score = calculate_score(
                    deployments[deployment][i],
                    new_weights
                )

                scores.append(score)

            best = 0

            for i in range(1, 5):
                if scores[i] > scores[best]:
                    best = i

            print(
                "Criterion:", criterion + 1,
                "Factor:", factor,
                "Winner:", techniques[best]
            )
