import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. NETWORK PARAMETERS
# -------------------------------------------------

R = 0.5
TOTAL_CHANNELS = 336
TOTAL_AREA = 12
PATH_LOSS = [2.5, 3, 4]
CLUSTER_SIZES = [3, 4, 7, 12]
SAMPLES = 10000

np.random.seed(42)

# -------------------------------------------------
# 2. GENERATE A 19-CELL HEXAGONAL NETWORK
# -------------------------------------------------

cells = []

for q in range(-2, 3):
    for r in range(-2, 3):
        if max(abs(q), abs(r), abs(q + r)) <= 2:
            x = np.sqrt(3) * R * (q + r / 2)
            y = 1.5 * R * r
            cells.append([q, r, x, y])

cells = pd.DataFrame(
    cells, columns=["q", "r", "x", "y"]
)

print("Number of cells:", len(cells))

plt.figure(figsize=(8, 7))

for i in range(len(cells)):
    x = cells.loc[i, "x"]
    y = cells.loc[i, "y"]

    angles = np.arange(0, 361, 60)
    hx = x + R * np.cos(np.radians(angles))
    hy = y + R * np.sin(np.radians(angles))

    plt.plot(hx, hy, "b-")
    plt.text(x, y, str(i + 1), ha="center", va="center")

plt.title("19-Cell Hexagonal Network")
plt.xlabel("Distance (km)")
plt.ylabel("Distance (km)")
plt.axis("equal")
plt.grid()
plt.show()

# -------------------------------------------------
# 3. FREQUENCY CHANNEL ALLOCATION
# -------------------------------------------------

# Co-channel colouring coefficients for the
# valid cluster sizes: 3, 4, 7 and 12.

coefficients = {
    3: (1, 2),
    4: (2, 1),
    7: (3, 1),
    12: (5, 1)
}

def assign_channels(N):
    a, b = coefficients[N]
    channels_per_cell = TOTAL_CHANNELS // N

    cells["group"] = (
        a * cells["q"] + b * cells["r"]
    ) % N

    cells["first_channel"] = (
        cells["group"] * channels_per_cell + 1
    )

    cells["last_channel"] = (
        (cells["group"] + 1) * channels_per_cell
    )

    return channels_per_cell

print("\nFREQUENCY ALLOCATION")

for N in CLUSTER_SIZES:
    C = assign_channels(N)
    print(
        "N =", N,
        "Channels per cell =", C
    )

# -------------------------------------------------
# 4. MONTE CARLO MOBILE POSITION GENERATION
# -------------------------------------------------

def generate_mobile_positions(number):
    positions = []

    while len(positions) < number:
        x = np.random.uniform(-R, R)
        y = np.random.uniform(
            -np.sqrt(3) * R / 2,
            np.sqrt(3) * R / 2
        )

        # Check whether the point lies inside
        # the regular hexagonal cell.

        if abs(x) + abs(y) / np.sqrt(3) <= R:
            positions.append([x, y])

    return np.array(positions)


# -------------------------------------------------
# 5. MONTE CARLO SIR CALCULATION
# -------------------------------------------------

def calculate_sir(N, n, sectorised=False):
    positions = generate_mobile_positions(SAMPLES)

    D = R * np.sqrt(3 * N)

    angles = np.arange(0, 360, 60)
    interferers = []

    for angle in angles:
        ix = D * np.cos(np.radians(angle))
        iy = D * np.sin(np.radians(angle))
        interferers.append([ix, iy])

    interferers = np.array(interferers)

    sir_values = []

    for i in range(SAMPLES):
        x = positions[i, 0]
        y = positions[i, 1]

        desired_distance = np.sqrt(x*x + y*y)

        if desired_distance < 0.001:
            desired_distance = 0.001

        desired_power = desired_distance ** (-n)

        interference = []

        for j in range(6):
            dx = x - interferers[j, 0]
            dy = y - interferers[j, 1]

            distance = np.sqrt(dx*dx + dy*dy)

            interference.append(distance ** (-n))

        if sectorised:
            # Idealised sector model:
            # retain the two strongest interferers.

            interference.sort(reverse=True)
            total_interference = (
                interference[0] + interference[1]
            )
        else:
            total_interference = sum(interference)

        sir = desired_power / total_interference

        sir_db = 10 * np.log10(sir)
        sir_values.append(sir_db)

    return np.array(sir_values)


# -------------------------------------------------
# 6. COMPARE SIR FOR DIFFERENT CLUSTER SIZES
# -------------------------------------------------

sir_results = []

for N in CLUSTER_SIZES:
    for n in PATH_LOSS:
        sir = calculate_sir(N, n)

        sir_results.append([
            N, n,
            np.mean(sir),
            np.min(sir),
            np.percentile(sir, 5)
        ])

sir_table = pd.DataFrame(
    sir_results,
    columns=[
        "Cluster Size",
        "Path Loss Exponent",
        "Average SIR (dB)",
        "Minimum SIR (dB)",
        "5th Percentile SIR (dB)"
    ]
)

print("\nSIR SIMULATION RESULTS")
print(sir_table.round(2))

# -------------------------------------------------
# 7. SECTORISATION ANALYSIS
# -------------------------------------------------

fixed_sir = calculate_sir(7, 3, False)
sector_sir = calculate_sir(7, 3, True)

print("\nSECTORISATION RESULTS")

print(
    "Fixed reuse average SIR:",
    round(np.mean(fixed_sir), 2), "dB"
)

print(
    "Sectorised average SIR:",
    round(np.mean(sector_sir), 2), "dB"
)

# -------------------------------------------------
# 8. ERLANG-B BLOCKING PROBABILITY
# -------------------------------------------------

def erlang_b(channels, traffic):
    B = 1.0

    for i in range(1, channels + 1):
        B = (traffic * B) / (i + traffic * B)

    return B


def find_capacity(channels, target_blocking):
    low = 0.0
    high = channels * 2.0

    for i in range(100):
        middle = (low + high) / 2
        blocking = erlang_b(channels, middle)

        if blocking > target_blocking:
            high = middle
        else:
            low = middle

    return (low + high) / 2


# -------------------------------------------------
# 9. FIXED, SECTORISED AND DCA CAPACITY
# -------------------------------------------------

target = 0.02

fixed_channels = 48
sector_channels = 16
dca_channels = 336

fixed_capacity = find_capacity(
    fixed_channels, target
)

sector_capacity = (
    3 * find_capacity(sector_channels, target)
)

dca_capacity = find_capacity(
    dca_channels, target
)

capacity_table = pd.DataFrame({
    "Strategy": [
        "Fixed Frequency Reuse",
        "120-degree Sectorisation",
        "Idealised Dynamic Channel Allocation"
    ],
    "Channels": [
        fixed_channels,
        sector_channels,
        dca_channels
    ],
    "Traffic Capacity (Erlangs)": [
        fixed_capacity,
        sector_capacity,
        dca_capacity
    ]
})

print("\nCAPACITY COMPARISON")
print(capacity_table.round(2))

# -------------------------------------------------
# 10. PLOT SIR RESULTS
# -------------------------------------------------

plt.figure(figsize=(8, 5))

for n in PATH_LOSS:
    values = []

    for N in CLUSTER_SIZES:
        result = sir_table[
            (sir_table["Cluster Size"] == N) &
            (sir_table["Path Loss Exponent"] == n)
        ]

        values.append(
            result["Average SIR (dB)"].iloc[0]
        )

    plt.plot(
        CLUSTER_SIZES,
        values,
        marker="o",
        label="Path loss n = " + str(n)
    )

plt.xlabel("Cluster Size (N)")
plt.ylabel("Average SIR (dB)")
plt.title("SIR Comparison for Different Cluster Sizes")
plt.legend()
plt.grid()
plt.show()

# -------------------------------------------------
# 11. PLOT CAPACITY COMPARISON
# -------------------------------------------------

plt.figure(figsize=(8, 5))

plt.bar(
    capacity_table["Strategy"],
    capacity_table["Traffic Capacity (Erlangs)"]
)

plt.ylabel("Traffic Capacity (Erlangs)")
plt.title("Traffic Capacity Comparison")
plt.xticks(rotation=15)
plt.grid(axis="y")
plt.tight_layout()
plt.show()

# Save SIR experimental results
sir_table.to_csv("SIR_Experimental_Results.csv", index=False)

# Save traffic capacity results
capacity_table.to_csv("Traffic_Capacity_Results.csv", index=False)

# Save frequency allocation results
frequency_table = pd.DataFrame({
    "Cluster Size": [3, 4, 7, 12],
    "Total Channels": [336, 336, 336, 336],
    "Channels Per Cell": [112, 84, 48, 28]
})

frequency_table.to_csv(
    "Frequency_Allocation_Results.csv",
    index=False
)

print("Experimental CSV files saved successfully.")