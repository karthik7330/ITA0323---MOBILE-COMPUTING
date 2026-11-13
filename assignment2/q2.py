
import random

SIMULATION_TIME = 3600
FDMA_CAPACITY = 72
TDMA_CAPACITY = 70

def generate_poisson(rate, mean_duration, rng):
    events = []
    time = 0

    while True:
        time += rng.expovariate(rate)

        if time >= SIMULATION_TIME:
            break

        duration = rng.expovariate(1 / mean_duration)
        events.append((time, duration))

    return events


def generate_events(scenario, seed):
    rng = random.Random(seed)

    if scenario == "voice":
        events = generate_poisson(0.35, 180, rng)

    elif scenario == "bursty":
        phases = []

        for i in range(100):
            phases.append(rng.randrange(10))

        events = []

        for time in range(SIMULATION_TIME):
            for phase in phases:
                if time % 10 == phase:
                    events.append((float(time), 1.0))

    elif scenario == "mixed":
        voice = generate_poisson(42 / 180, 180, rng)
        data = generate_poisson(18 / 10, 10, rng)
        events = voice + data

    else:
        events = []

        for time in range(0, SIMULATION_TIME, 60):
            for i in range(100):
                events.append((float(time), 2.0))

    events.sort(key=lambda x: x[0])
    return events


def simulate(capacity, scenario):
    events = generate_events(scenario, 42)

    active = []
    arrivals = 0
    admitted = 0
    blocked = 0
    occupied_time = 0

    for time, duration in events:

        remaining = []

        for end_time in active:
            if end_time > time:
                remaining.append(end_time)

        active = remaining
        arrivals += 1

        if len(active) < capacity:
            end_time = time + duration
            active.append(end_time)
            admitted += 1

            if end_time > SIMULATION_TIME:
                occupied_time += SIMULATION_TIME - time
            else:
                occupied_time += duration

        else:
            blocked += 1

    blocking = blocked / arrivals
    utilization = occupied_time / (capacity * SIMULATION_TIME)
    wasted = 1 - utilization

    return arrivals, admitted, blocked, blocking, utilization, wasted


scenarios = ["voice", "bursty", "mixed", "sync"]

for scenario in scenarios:

    print("\nTraffic Dataset:", scenario)

    for name, capacity in [
        ("FDMA", FDMA_CAPACITY),
        ("TDMA", TDMA_CAPACITY)
    ]:

        result = simulate(capacity, scenario)

        print("\n", name)
        print("Total Requests:", result[0])
        print("Admitted:", result[1])
        print("Blocked:", result[2])
        print("Blocking Rate:", round(result[3] * 100, 2), "%")
        print("Utilization:", round(result[4] * 100, 2), "%")
        print("Wasted Capacity:", round(result[5] * 100, 2), "%")
